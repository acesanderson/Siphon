def parse_timestamp_line(line):
    """Parse a transcript line with timestamps like '[0.00 -> 0.12]: Do'"""
    try:
        # Split on ']:'
        time_part, text = line.split("]:", 1)
        # Remove '[' and split on '->'
        start_str, end_str = time_part[1:].split("->")
        return {
            "start": float(start_str.strip()),
            "end": float(end_str.strip()),
            "text": text.strip(),
        }
    except Exception as e:
        print(f"Error parsing transcript line: {line}")
        print(f"Error details: {str(e)}")
        return None


def parse_rttm_line(line):
    """Parse an RTTM format line"""
    try:
        parts = line.strip().split()
        if len(parts) < 8:
            print(f"Warning: Invalid RTTM line format: {line}")
            return None

        return {
            "start": float(parts[3]),
            "duration": float(parts[4]),
            "end": float(parts[3]) + float(parts[4]),
            "speaker": parts[7],
        }
    except Exception as e:
        print(f"Error parsing RTTM line: {line}")
        print(f"Error details: {str(e)}")
        return None


def merge_diarization_and_transcript(diarization_data, transcript_data):
    """
    Merge diarization data with transcript data to create a fully annotated transcript.

    Args:
        diarization_data (str): Raw RTTM format diarization data
        transcript_data (str): Raw transcript data with timestamps

    Returns:
        list: List of dictionaries containing merged segments
    """
    # Parse diarization data
    speaker_segments = []
    for line in diarization_data.strip().split("\n"):
        if not line.strip() or line.startswith("#"):
            continue

        segment = parse_rttm_line(line)
        if segment:
            speaker_segments.append(segment)

    # Parse transcript data
    transcript_segments = []
    for line in transcript_data.strip().split("\n"):
        if not line.strip():
            continue

        segment = parse_timestamp_line(line)
        if segment:
            transcript_segments.append(segment)

    # Merge the data
    annotated_transcript = []
    for trans_seg in transcript_segments:
        # Find matching speaker segment
        speaker = None
        for spk_seg in speaker_segments:
            if (
                trans_seg["start"] >= spk_seg["start"]
                and trans_seg["end"] <= spk_seg["end"]
            ):
                speaker = spk_seg["speaker"]
                break

        annotated_transcript.append(
            {
                "start": trans_seg["start"],
                "end": trans_seg["end"],
                "speaker": speaker or "UNKNOWN",
                "text": trans_seg["text"],
            }
        )

    return annotated_transcript


if __name__ == "__main__":
    # Read diarization data
    try:
        with open("audio.rttm", "r") as f:
            diarization_data = f.read()
    except Exception as e:
        print(f"Error reading diarization file: {str(e)}")
        exit(1)

    # Read transcript data
    try:
        with open("processed/dr_visit_12-16-2024_timestamps.txt", "r") as f:
            transcript_data = f.read()
    except Exception as e:
        print(f"Error reading transcript file: {str(e)}")
        exit(1)

    # Process the data
    try:
        integrated = merge_diarization_and_transcript(diarization_data, transcript_data)

        # Print merged transcript
        for segment in integrated:
            print(
                f"[{segment['start']:.2f} -> {segment['end']:.2f}] {segment['speaker']}: {segment['text']}"
            )

        with open("integrated.txt", "w") as f:
            for segment in integrated:
                f.write(
                    f"[{segment['start']:.2f} -> {segment['end']:.2f}] {segment['speaker']}: {segment['text']}\n"
                )

    except Exception as e:
        print(f"Error during merge: {str(e)}")
