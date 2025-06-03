"""
Following instructions from the official HuggingFace repo:
    https://huggingface.co/openai/whisper-large-v3-turbo
"""

import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import json
from pathlib import Path

dir_path = Path(__file__).parent
asset_dir = dir_path.parent / "assets"
MP3_FILE = str(asset_dir / "output.mp3")


def setup_device():
    if torch.cuda.is_available():
        print("CUDA is available.")
        return "cuda:0", torch.float16
    print("CUDA is not available.")
    return "mps", torch.float32


def initialize_model(device, torch_dtype):
    model_id = "openai/whisper-large-v3-turbo"
    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        model_id,
        torch_dtype=torch_dtype,
        low_cpu_mem_usage=True,
        use_safetensors=True,
    )
    model.to(device)
    return model, model_id


def create_pipeline(model, model_id, torch_dtype, device):
    processor = AutoProcessor.from_pretrained(model_id)
    return pipeline(
        "automatic-speech-recognition",
        model=model,
        tokenizer=processor.tokenizer,
        feature_extractor=processor.feature_extractor,
        torch_dtype=torch_dtype,
        device=device,
    )


def transcribe_audio(pipe, audio_file):
    # Set chunk_length_s to process longer audio files
    # Set return_timestamps="word" for word-level timestamps or "chunk" for chunk-level
    result = pipe(
        audio_file,
        return_timestamps="word",
        chunk_length_s=30,  # Process 30 seconds at a time
        stride_length_s=1,  # 1 second overlap between chunks
    )
    return result


def save_transcription(result, output_file="transcription_with_timestamps.json"):
    # Save the complete result including timestamps
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)


def main():
    # Setup and initialization
    device, torch_dtype = setup_device()
    model, model_id = initialize_model(device, torch_dtype)
    pipe = create_pipeline(model, model_id, torch_dtype, device)

    # Transcribe audio
    print(f"Transcribing {MP3_FILE}...")
    result = transcribe_audio(pipe, MP3_FILE)

    # Save results
    save_transcription(result)

    # Print the text and timestamps
    results = ""
    if "chunks" in result:
        for chunk in result["chunks"]:
            try:
                timestamp = (
                    f"[{chunk['timestamp'][0]:.2f} -> {chunk['timestamp'][1]:.2f}]"
                )
                print(f"{timestamp}: {chunk['text']}")
                results += chunk["text"]
            except:
                print("Error")
    else:
        print("Full text:", result["text"])
        print("\nTimestamps:", result.get("timestamps", []))

    print(results)


if __name__ == "__main__":
    main()
