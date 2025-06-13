def format_transcript(annotated_transcript, group_by_speaker=True):
    """
    Format the annotated transcript into readable text.

    Args:
        annotated_transcript: Output from combine()
        group_by_speaker: Whether to group consecutive words by same speaker

    Returns:
        str: Formatted transcript
    """
    if not annotated_transcript:
        return ""

    if not group_by_speaker:
        # Simple word-by-word format
        lines = []
        for item in annotated_transcript:
            timestamp = f"[{item['start_time']:.1f}s]"
            lines.append(f"{timestamp} {item['speaker']}: {item['word']}")
        return "\n".join(lines)

    # Group by speaker for more readable output
    lines = []
    current_speaker = None
    current_words = []
    current_start_time = None

    for item in annotated_transcript:
        speaker = item["speaker"]

        if speaker != current_speaker:
            # Speaker changed, output previous speaker's text
            if current_speaker is not None and current_words:
                timestamp = f"[{current_start_time:.1f}s]"
                text = " ".join(current_words)
                lines.append(f"{timestamp} {current_speaker}: {text}")

            # Start new speaker
            current_speaker = speaker
            current_words = [item["word"]]
            current_start_time = item["start_time"]
        else:
            # Same speaker, add word
            current_words.append(item["word"])

    # Don't forget the last speaker
    if current_speaker is not None and current_words:
        timestamp = f"[{current_start_time:.1f}s]"
        text = " ".join(current_words)
        lines.append(f"{timestamp} {current_speaker}: {text}")

    return "\n".join(lines)


if __name__ == "__main__":
    from example import example_file
    from combine import combine
    from diarize import diarize
    from transcribe import transcribe

    diarization_result = diarize(example_file)
    transcript_result = transcribe(example_file)
    annotated = combine(diarization_result, transcript_result)
    formatted = format_transcript(annotated, group_by_speaker=True)

    print(formatted)
