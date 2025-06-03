#!/usr/bin/env python3
"""
Master Transcript Pipeline
Takes an MP3 file and produces a fully formatted, professional transcript.
"""

import os
import json
import torch
from pathlib import Path

# External dependencies
from pyannote.audio import Pipeline
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from Chain import Chain, Model, Prompt
from pathlib import Path

dir_path = Path(__file__).parent
asset_dir = dir_path.parent / "assets"
MP3_FILE = str(asset_dir / "output.mp3")


class TranscriptPipeline:
    def __init__(self, huggingface_token: str, use_gpu: bool = True):
        """
        Initialize the transcript pipeline.

        Args:
            huggingface_token: HuggingFace API token for accessing models
            use_gpu: Whether to use GPU acceleration if available
        """
        self.hf_token = huggingface_token
        self.device, self.torch_dtype = self._setup_device(use_gpu)
        self.whisper_model = None
        self.whisper_pipeline = None
        self.diarization_pipeline = None

    def _setup_device(self, use_gpu: bool):
        """Setup compute device and data type."""
        if use_gpu and torch.cuda.is_available():
            print("Using CUDA GPU acceleration")
            return "cuda:0", torch.float16
        elif use_gpu and torch.backends.mps.is_available():
            print("Using MPS (Apple Silicon) acceleration")
            return "mps", torch.float32
        else:
            print("Using CPU")
            return "cpu", torch.float32

    def _init_whisper(self):
        """Initialize Whisper model for transcription."""
        if self.whisper_pipeline is not None:
            return

        print("Loading Whisper model...")
        model_id = "openai/whisper-large-v3-turbo"

        model = AutoModelForSpeechSeq2Seq.from_pretrained(
            model_id,
            torch_dtype=self.torch_dtype,
            low_cpu_mem_usage=True,
            use_safetensors=True,
        )
        model.to(self.device)

        processor = AutoProcessor.from_pretrained(model_id)

        self.whisper_pipeline = pipeline(
            "automatic-speech-recognition",
            model=model,
            tokenizer=processor.tokenizer,
            feature_extractor=processor.feature_extractor,
            torch_dtype=self.torch_dtype,
            device=self.device,
        )
        print("Whisper model loaded successfully")

    def _init_diarization(self):
        """Initialize speaker diarization model."""
        if self.diarization_pipeline is not None:
            return

        print("Loading speaker diarization model...")
        self.diarization_pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            use_auth_token=self.hf_token,
        )
        self.diarization_pipeline.to(torch.device(self.device))
        print("Diarization model loaded successfully")

    def transcribe_audio(self, audio_file: str) -> list[dict]:
        """
        Transcribe audio file using Whisper.

        Returns:
            list of transcript segments with timestamps
        """
        self._init_whisper()

        print(f"Transcribing audio: {audio_file}")
        result = self.whisper_pipeline(
            audio_file,
            return_timestamps="word",
            chunk_length_s=30,
            stride_length_s=1,
        )

        # Extract segments with timestamps
        segments = []
        if "chunks" in result:
            for chunk in result["chunks"]:
                timestamp = chunk.get("timestamp")
                if timestamp and len(timestamp) >= 2:
                    segments.append(
                        {
                            "start": float(timestamp[0]),
                            "end": float(timestamp[1]),
                            "text": chunk["text"].strip(),
                        }
                    )
        else:
            # Fallback: if no chunks, try to use the full text
            print("Warning: No chunks found in transcription result")
            if "text" in result:
                segments.append(
                    {
                        "start": 0.0,
                        "end": 0.0,  # Unknown duration
                        "text": result["text"].strip(),
                    }
                )

        if not segments:
            raise RuntimeError("Transcription failed: no segments extracted")

        print(f"Transcription complete: {len(segments)} segments")
        return segments

    def diarize_audio(self, audio_file: str) -> list[dict]:
        """
        Perform speaker diarization on audio file.

        Returns:
            list of speaker segments with timestamps
        """
        self._init_diarization()

        print(f"Performing speaker diarization: {audio_file}")
        diarization = self.diarization_pipeline(audio_file)

        # Convert to our format
        speaker_segments = []
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            speaker_segments.append(
                {"start": turn.start, "end": turn.end, "speaker": speaker}
            )

        print(f"Diarization complete: {len(speaker_segments)} speaker segments")
        return speaker_segments

    def merge_transcription_and_diarization(
        self, transcript_segments: list[dict], speaker_segments: list[dict]
    ) -> list[dict]:
        """
        Merge transcription with speaker diarization.

        Returns:
            list of segments with both text and speaker labels
        """
        print("Merging transcription with speaker diarization...")

        if not transcript_segments:
            print("Warning: No transcript segments to merge")
            return []

        if not speaker_segments:
            print("Warning: No speaker segments found, using UNKNOWN speaker")
            return [{**seg, "speaker": "UNKNOWN"} for seg in transcript_segments]

        merged_segments = []
        for trans_seg in transcript_segments:
            # Skip segments with invalid timestamps
            if trans_seg["start"] == 0.0 and trans_seg["end"] == 0.0:
                merged_segments.append({**trans_seg, "speaker": "UNKNOWN"})
                continue

            # Find the speaker for this transcript segment
            speaker = "UNKNOWN"
            trans_mid = (trans_seg["start"] + trans_seg["end"]) / 2

            # Find best overlapping speaker segment
            best_overlap = 0
            for spk_seg in speaker_segments:
                overlap_start = max(trans_seg["start"], spk_seg["start"])
                overlap_end = min(trans_seg["end"], spk_seg["end"])
                overlap = max(0, overlap_end - overlap_start)

                if overlap > best_overlap:
                    best_overlap = overlap
                    speaker = spk_seg["speaker"]

            merged_segments.append(
                {
                    "start": trans_seg["start"],
                    "end": trans_seg["end"],
                    "speaker": speaker,
                    "text": trans_seg["text"],
                }
            )

        return merged_segments

    def consolidate_by_speaker(self, segments: list[dict]) -> list[dict]:
        """
        Consolidate consecutive segments from the same speaker.
        """
        print("Consolidating consecutive speaker segments...")

        if not segments:
            return []

        consolidated = []
        current_speaker = segments[0]["speaker"]
        current_text = segments[0]["text"]
        current_start = segments[0]["start"]
        current_end = segments[0]["end"]

        for segment in segments[1:]:
            if (
                segment["speaker"] == current_speaker and current_speaker != "UNKNOWN"
            ):  # Don't consolidate UNKNOWN speakers
                # Same speaker, append text
                current_text += " " + segment["text"]
                current_end = segment["end"]
            else:
                # New speaker, save current and start new
                if current_text.strip():  # Only add non-empty segments
                    consolidated.append(
                        {
                            "start": current_start,
                            "end": current_end,
                            "speaker": current_speaker,
                            "text": current_text.strip(),
                        }
                    )

                current_speaker = segment["speaker"]
                current_text = segment["text"]
                current_start = segment["start"]
                current_end = segment["end"]

        # Don't forget the last segment
        if current_text.strip():
            consolidated.append(
                {
                    "start": current_start,
                    "end": current_end,
                    "speaker": current_speaker,
                    "text": current_text.strip(),
                }
            )

        return consolidated

    def format_with_llm(self, raw_transcript: str, model_name: str = "gpt") -> str:
        """
        Format transcript using LLM for professional presentation.

        Args:
            raw_transcript: Raw transcript text
            model_name: Model to use for formatting
        """
        print(f"Formatting transcript with {model_name}...")

        format_prompt = """
I need you to transform a raw, unstructured audio transcript into a clean, professional document. This transcript has speaker labels. Please:

1. **Clean up the text** by:
   - Removing filler words (um, uh, like, you know, etc.) when they don't add meaning
   - Fixing grammatical errors while preserving the speaker's intended meaning
   - Consolidating fragmented thoughts into coherent sentences
   - Removing false starts and repetitions that don't contribute to understanding

2. **Add structural elements** like:
   - A title that captures the main topic of the conversation
   - Section headings where the conversation shifts to new topics
   - Bullet points for lists or enumerated points made by speakers
   - Bold formatting for key statements or conclusions

3. **Create a brief summary** (2-3 sentences) at the beginning that captures the main purpose and topics of the conversation.

4. **Preserve important verbal cues** in brackets where they add meaning, such as [laughs], [pauses], or [emphasizes].

5. **Maintain authenticity** by keeping distinctive phrases, terminology, or speech patterns that characterize each speaker.

Please be careful not to change the meaning of any statements or add information that wasn't in the original transcript. Present the final document in a clean, readable format that would be appropriate for professional use.

Here's the raw transcript:
<transcript>
{{transcript}}
</transcript>
""".strip()

        try:
            model = Model(model_name)
            prompt = Prompt(format_prompt)
            chain = Chain(model=model, prompt=prompt)
            response = chain.run(input_variables={"transcript": raw_transcript})
            return response.content if hasattr(response, "content") else str(response)
        except Exception as e:
            print(f"Warning: LLM formatting failed ({e}). Returning basic format.")
            return self._basic_format(raw_transcript)

    def _basic_format(self, raw_transcript: str) -> str:
        """Fallback basic formatting if LLM fails."""
        lines = raw_transcript.strip().split("\n")
        formatted_lines = []

        formatted_lines.append("# Transcript\n")
        formatted_lines.append("## Summary")
        formatted_lines.append(
            "*Auto-generated transcript - manual review recommended*\n"
        )

        for line in lines:
            if ":" in line:
                speaker, text = line.split(":", 1)
                formatted_lines.append(f"**{speaker.strip()}:** {text.strip()}")
            else:
                formatted_lines.append(line)

        return "\n\n".join(formatted_lines)

    def process_audio(
        self,
        audio_file: str,
        output_file: str = None,
        format_model: str = "gpt",
        save_intermediate: bool = False,
    ) -> str:
        """
        Complete pipeline: audio file to formatted transcript.

        Args:
            audio_file: Path to input MP3 file
            output_file: Optional output file path
            format_model: Model to use for final formatting
            save_intermediate: Whether to save intermediate files

        Returns:
            Formatted transcript text
        """
        if not os.path.exists(audio_file):
            raise FileNotFoundError(f"Audio file not found: {audio_file}")

        print(f"Starting transcript pipeline for: {audio_file}")

        try:
            # Step 1: Transcribe audio
            transcript_segments = self.transcribe_audio(audio_file)

            # Step 2: Diarize speakers
            speaker_segments = self.diarize_audio(audio_file)

            # Step 3: Merge transcription and diarization
            merged_segments = self.merge_transcription_and_diarization(
                transcript_segments, speaker_segments
            )

            # Step 4: Consolidate by speaker
            consolidated_segments = self.consolidate_by_speaker(merged_segments)

            if not consolidated_segments:
                raise RuntimeError("No valid segments produced from audio processing")

            # Step 5: Create raw transcript text
            raw_transcript = "\n".join(
                [
                    f"{seg['speaker']}: {seg['text']}"
                    for seg in consolidated_segments
                    if seg["text"].strip()  # Skip empty text segments
                ]
            )

            if not raw_transcript.strip():
                raise RuntimeError("Generated transcript is empty")

            # Step 6: Format with LLM
            formatted_transcript = self.format_with_llm(raw_transcript, format_model)

            # Save output
            if output_file:
                os.makedirs(
                    os.path.dirname(os.path.abspath(output_file)), exist_ok=True
                )
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(formatted_transcript)
                print(f"Formatted transcript saved to: {output_file}")

            # Save intermediate files if requested
            if save_intermediate:
                base_name = Path(audio_file).stem

                # Save raw merged transcript
                with open(f"{base_name}_raw.txt", "w", encoding="utf-8") as f:
                    f.write(raw_transcript)

                # Save detailed segments as JSON
                with open(f"{base_name}_segments.json", "w", encoding="utf-8") as f:
                    json.dump(consolidated_segments, f, indent=2, ensure_ascii=False)

            print("Pipeline complete!")
            return formatted_transcript

        except Exception as e:
            print(f"Pipeline failed: {e}")
            raise


# Global pipeline instance for reuse
_pipeline_instance = None


def process_mp3_to_transcript(
    mp3_file: str,
    format_model: str = "gpt",
    use_gpu: bool = True,
    huggingface_token: str = None,
) -> str:
    """
    Convert MP3 audio file to formatted transcript.

    Args:
        mp3_file: Path to MP3 audio file
        format_model: LLM model to use for formatting (default: "gpt")
        use_gpu: Whether to use GPU acceleration if available (default: True)
        huggingface_token: HuggingFace API token (uses env var if None)

    Returns:
        Formatted transcript as string

    Raises:
        FileNotFoundError: If MP3 file doesn't exist
        RuntimeError: If processing fails
        ValueError: If HuggingFace token is missing
    """
    global _pipeline_instance

    # Get HuggingFace token
    hf_token = huggingface_token or os.getenv("HUGGINGFACEHUB_API_TOKEN")
    if not hf_token:
        raise ValueError(
            "HuggingFace API token required. Set HUGGINGFACEHUB_API_TOKEN "
            "environment variable or pass huggingface_token parameter."
        )

    # Initialize pipeline if needed (reuse for multiple calls)
    if _pipeline_instance is None:
        _pipeline_instance = TranscriptPipeline(
            huggingface_token=hf_token, use_gpu=use_gpu
        )

    # Process the audio file and return formatted transcript
    return _pipeline_instance.process_audio(
        audio_file=mp3_file,
        output_file=None,  # Don't save to file, just return string
        format_model=format_model,
        save_intermediate=False,
    )


# Example usage
if __name__ == "__main__":
    # Simple example usage
    try:
        transcript = process_mp3_to_transcript(MP3_FILE)
        print(transcript)
    except Exception as e:
        print(f"Error: {e}")
