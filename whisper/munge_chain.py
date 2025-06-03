with open("formatted.txt", "r") as f:
    raw_transcript = f.read()

from Chain import Prompt, Model, Chain


prompt_string = """
Look at the raw transcript below:

<raw_transcript>
{{raw_transcript}}
</raw_transcript>

Your job is to convert this into a cleaner transcript, with proper punctuation and sentence structure. Add capitalization and punctuation where appropriate.

Note: as a transcript, it is sometimes unclear what a person is saying. Don't do too much guessing -- if the meaning of a sentence is unclear, please add a '[?]' to the end, as I will manually be going through and editing it by hand, as I was one of the speakers and have the context.

Return only the formatted transcript, no additional commentary.

""".strip()


raw_transcript = raw_transcript.split("\n")

# Split the raw_transcript into four equal-length parts

n = len(raw_transcript)

transcript_parts = [
    part1 := raw_transcript[: n // 4],
    part2 := raw_transcript[n // 4 : n // 2],
    part3 := raw_transcript[n // 2 : 3 * n // 4],
    part4 := raw_transcript[3 * n // 4 :],
]


def format_chain(part):
    model = Model("gpt")
    prompt = Prompt(prompt_string)
    chain = Chain(prompt=prompt, model=model)
    response = chain.run(input_variables={"raw_transcript": "\n".join(part)})
    return response.content


if __name__ == "__main__":
    output = ""
    for index, part in enumerate(transcript_parts):
        print(f"Processing part {index}.")
        response = format_chain(part)
        output += response + "\n"
    with open("chained.txt", "w") as f:
        f.write(output)
