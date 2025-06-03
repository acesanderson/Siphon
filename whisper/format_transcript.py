from Chain import Chain, Model, Prompt

transcript = """While there's chaos or you know complexity in the world that the world is looking towards LinkedIn to be one of the shining lights through that so it's good to see. All right let's hear some questions. Oh we have one. Yeah we've got one in Graz here. of content for International. And so my question to you and basically everybody here is to, yeah, how do you see the future of LinkedIn learning and how it will evolve from your perspective. We here in Graz we produce most of the international content for LinkedIn learning and we are dedicated to deliver really good quality but it would be especially interesting to hear let's say the wider view from you and everybody who is with you today. Yeah thanks Cornelia. So it turns out that the very first European office that I've ever visited for LinkedIn happens to be Graz so holds a special place in my heart. Yeah go Graz Yeah, that's right. I mean, you know, one of the things that we're paying a lot of attention to right now are kind of the focus on not only the importance of learning, but how learning is going to need to change. So let's take a step back. I know we're not in the U.S. right now, but right now in the U.S. this year, 50 percent of college graduates are going to graduate either unemployed or underemployed. And for the first time in U.S. history, student loan debt is outpacing credit card debt so the process is starting to become a really really flawed in the country traditional ways of education similarly if you take the average person on linkedin the skills that are needed to do their job have changed by 25 percent uh over the past five years and we expect them to change by another uh by up to 70 percent over you know by by the time it's 2030. so no matter what your job is uh even if you're not changing jobs your job is changing on you all of a sudden on you. All of a sudden, what I think historically had been thought of is a nice to have, which was real-time upskilling based on potentially technology that didn't even exist a year ago, is now becoming a necessity in order to do your job, no matter what your job is. Historically, people would, you know, go through college, through a four-year degree, you know, get a master's degree, etc. is the way to train we can't afford to have those processes these days in order processes these days in order to create an efficient labor market. So more than ever, kind of the vision of LinkedIn learning is becoming more important than it ever has been. But we're going to need to do a couple of things. Number one, identify the critical skills that need to be taught through our data. I'm going to be going to Brussels, like Sue said, I guess tomorrow, if Ryanair makes it there. And we're going to talk about what are the most in-demand skills that are happening right there's a huge skills imbalance. So the skills that a lot of companies are trying to hire for, quite frankly, a lot of Gen AI skills, the labor force doesn't have those skills. So we need to be able to identify that to quickly create the content, the framework, the learning styles, get that in front of the people that need to learn those skills. Because on the other end, there's a recruiter right there waiting to hire them as soon as they have those skills and can demonstrate them. And they need that real time. It's not a four-year degree type of real time, it's not a four-year degree type of thing anymore. So I think that more than ever, learning is becoming a critical part of, you know, not only as a business for LinkedIn, but quite frankly, as a necessary, you know, platform component to help the economies move forward. The one thing I will say, though, is we need to be really innovative on what we're doing inside of learning. You know, to a certain extent, the old model of, you know, here's a whatever, you know, three, four hour video on a topic, you know, watch it, maybe take an assessment at the end, is going to need to evolve into something that's different. I think some of the stuff that, you know, I know Cornelia and the Grouch team has been focused on a lot in the coding space are actual practical applications of using those skills and showing those skills in the product. Some of the AI tools that we're building now that allow you to practice with AI as you're learning if they're going to become more important. So I think we're going to need to, you know, number one, keep our ethos of having the highest quality, dependable learning content online, but then evolving the application and demonstration of that in our AI tools that then lead to credentials that flow into the recruiting tools so people can get hired and get jobs. So that's kind of, you know, directionally where I see it going. Also, we're going to have to move much faster. Like, you know, I know that some of the things we pride ourselves on in grats and carpentry with our learning products is the, you. We have to make sure that we are constantly, though, innovating on the format, I think, to a certain extent. Anything you want to add? Pia, I mean, it's like anything on your side? Thank you, very much. Spot on. Yeah, great. Wonderful. I'd add maybe there's two things on the customer side. So on the customer's success experience, we're hearing two critical use cases for learning right now. is internal mobility and career development. and career development. And that's what customers are talking to us about, is at a time when they may not be hiring, how do they help career development within their organization? And at a time when we might have great tenure of employees, especially in the EMEA region, what they're looking for is how can they use learning to foster internal mobility? And then the second hot topic from our customers is very much to what you mentioned, Ryan, AI. Help us upskill our organization with AI. So from those two use cases as So from those two use cases as well, that's what we hear most frequently from our customers. I love it. Ready? Open, honest, constructive. There's no right or wrong answer. Raise your hand if you used AI at all today to do your job. Unbelievable. Wait. Ready? Raise your hand today if you didn't. I see you. I see you up there. Nice job. All right. Thanks. Hi, my name
""".strip()


format_prompt = """
I need you to transform a raw, unstructured audio transcript into a clean, professional document. This transcript has no speaker labels (diarization) or timestamps. Please:

1. **Identify different speakers** based on context clues and speech patterns. Label them as "Speaker 1," "Speaker 2," etc., or with their actual names if they're mentioned in the transcript.

2. **Format the document** with clear paragraph breaks between different speakers' statements.

3. **Clean up the text** by:
   - Removing filler words (um, uh, like, you know, etc.) when they don't add meaning
   - Fixing grammatical errors while preserving the speaker's intended meaning
   - Consolidating fragmented thoughts into coherent sentences
   - Removing false starts and repetitions that don't contribute to understanding

4. **Add structural elements** like:
   - A title that captures the main topic of the conversation
   - Section headings where the conversation shifts to new topics
   - Bullet points for lists or enumerated points made by speakers
   - Bold formatting for key statements or conclusions

5. **Create a brief summary** (2-3 sentences) at the beginning that captures the main purpose and topics of the conversation.

6. **Preserve important verbal cues** in brackets where they add meaning, such as [laughs], [pauses], or [emphasizes].

7. **Maintain authenticity** by keeping distinctive phrases, terminology, or speech patterns that characterize each speaker.

Please be careful not to change the meaning of any statements or add information that wasn't in the original transcript. Present the final document in a clean, readable format that would be appropriate for professional use.

Here's the raw transcript:
<transcript>
{{transcript}}
</transcript>
""".strip()

preferred_model = "phi4:latest"

if __name__ == "__main__":
    model = Model(preferred_model)
    prompt = Prompt(format_prompt)
    chain = Chain(model=model, prompt=prompt)
    response = chain.run(input_variables={"transcript": transcript})
    print(response)
