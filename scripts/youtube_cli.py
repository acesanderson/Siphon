raise NotImplementedError()



from Siphon.ingestion.youtube.retrieve_youtube import retrieve_youtube
# from Chain.cli.

YouTube_prompt_string = """
You are tasked with summarizing a YouTube video transcript. The purpose of this summary is to highlight the most interesting and useful information from the video, focusing on its unique contributions rather than generic content. This summary will help users quickly understand the key points and valuable insights without watching the entire video.

You will be provided with the following transcript:

<transcript>
{{transcript}}
</transcript>

Begin by determining the word count of the provided transcript. This will be used to calculate the appropriate length for your summary.

Read through the entire transcript carefully, paying attention to the main topics, key arguments, and unique insights presented. As you read, make mental notes of the most important points and any recurring themes.

Your summary should be structured as follows:
1. Brief introduction (1-2 sentences about the video's topic and speaker, if known)
2. Main topics covered (bullet point list)
3. Key insights and unique contributions (3-5 paragraphs)
4. Notable quotes or examples (2-3 direct quotes that illustrate important points)
5. Conclusion (1-2 sentences summarizing the video's significance or main takeaway)

When writing the summary, follow these guidelines:
1. Calculate the summary length based on the transcript word count:
   - For transcripts over 6,000 words, aim for a summary of at least 2,000 words.
   - For shorter transcripts, use a ratio of approximately 1:3 (summary:transcript). For example, a 3,000-word transcript should have a summary of about 1,000 words.
2. Focus on the unique contributions and insights presented in the video. Avoid generic summaries that could apply to any video on the topic.
3. Do not comment on the qualities of the video, we do not need to hear that you found the video insightful.
4. Use specific examples, data points, or arguments from the transcript to illustrate key points.
5. Highlight any novel ideas, counterintuitive claims, or particularly compelling arguments made in the video.
6. If the video presents multiple perspectives on a topic, ensure that you accurately represent each viewpoint.
7. Pay attention to the speaker's tone and emphasis, noting any points they seem to consider particularly important.
8. If the transcript includes descriptions of visual elements (e.g., charts, demonstrations), mention these in your summary if they are crucial to understanding the content.

To avoid sounding too generic:
1. Use specific terminology and jargon from the video when appropriate, explaining it if necessary.
2. Highlight any unique methodologies, case studies, or research mentioned in the video.
3. Note any personal anecdotes or experiences shared by the speaker that illustrate key points.
4. Identify and emphasize any calls to action or practical applications suggested in the video.

For shorter transcripts (under 3,000 words):
1. Adjust the summary length to approximately 1:3 ratio of the transcript word count.
2. Focus on the 2-3 most important points rather than trying to cover everything.
3. Combine the "Key insights" and "Notable quotes" sections if necessary.

Before writing your final summary, use <scratchpad> tags to outline the main points and structure of your summary. This will help you organize your thoughts and ensure you cover all important aspects of the video.

Present your final summary within <summary> tags. Use appropriate markdown formatting for headings, bullet points, and emphasis where necessary.

Remember, the goal is to provide a comprehensive yet concise summary that captures the essence of the video and its unique contributions to the topic at hand.
""".strip()

def query_text(
    text: str, query: str, messagestore: MessageStore, preferred_model: str
) -> str:
    """
    This function takes a text and a query and returns the response.
    """
    with console.status("[green]Query...", spinner="dots"):
        model = Model(preferred_model)
        prompt_string = "Look at this text and answer the following question: <text>{{text}}</text> <query>{{query}}</query>"
        prompt = Prompt(prompt_string)
        chain = Chain(prompt=prompt, model=model)
        response = chain.run(
            input_variables={"text": text, "query": query}, verbose=True
        )
        messagestore.add_new("assistant", response.content)
    return response.content


def extract_summary_from_string(text: str, tries: int = 0) -> str:
    """
    Our summarization prompts have the LLM put the summary in xml tags.
    We want to grab text within <summary> xml tags.
    """
    if tries > 3:
        console.print(
            "Prompt is not working, no <summary> xml tags detected. Attempted three times."
        )
        return None
    pattern = r"<summary>(.*?)</summary>"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    else:
        console.print("LLM output didn't have <summarize> tags.")
        tries += 1
        return extract_summary_from_string(text=text, tries=tries)


def summarize_youtube_transcript(transcript: str, preferred_model: str) -> str:
    """
    This function takes a YouTube transcript and summarizes it.
    """
    with console.status("[green]Summarizing YouTube transcript...", spinner="dots"):
        model = Model(preferred_model)
        prompt = Prompt(YouTube_prompt_string)
        chain = Chain(prompt=prompt, model=model)
        response = chain.run(input_variables={"transcript": transcript}, verbose=True)
    summary = extract_summary_from_string(response.content)
    return summary


