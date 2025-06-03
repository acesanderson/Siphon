import re

with open("integrated2.txt", "r") as f:
    transcript = f.read()

transcript = transcript.split("\n")


# First, double check the data is in our preferred format
for line in transcript:
    if not re.match("^[^:]+:[^:]+$", line):
        print(line)

transcript_tuples = [line.split(":") for line in transcript]

# Now, we can do the munging
# Combine all the lines that are part of the same speaker into one line
# We'll also remove any leading or trailing whitespace
new_transcript = []
current_speaker = None
current_line = ""
for line in transcript_tuples:
    if len(line) != 2:
        print("Skipping line: ", line)
        continue
    speaker, words = line
    speaker = speaker.strip()
    if speaker == current_speaker:
        current_line += " " + words.strip()
    else:
        new_transcript.append((current_speaker, current_line))
        current_line = ""
        current_speaker = speaker

output = "\n".join([f"{speaker}: {line}" for speaker, line in new_transcript])

with open("formatted.txt", "w") as f:
    f.write(output)
