⠋ claude-sonnet-4-20250514 | [0/0] ✓ claude-sonnet-4-20250514 | [0/0]  | (51.5s)
⠋ Running 3 concurrent requests...⠋ Progress: 1/3 complete | 2 running | 0 failed | 16.0s elapsed⠋ Progress: 2/3 complete | 1 running | 0 failed | 27.5s elapsed⠋ Progress: 3/3 complete | 0 running | 0 failed | 47.8s elapsed✓ All requests complete: 3/3 successful in 47.8s
# Building AI Agents at Datadog: The DevOps Engineer Who Never Sleeps

Hey, I'm Diamond. I hope everyone's feeling the AGI today. I'll be sharing our AI agents at Datadog and what we've learned building the DevOps engineer who never sleeps. I came all the way from the New York Times building right across here to see all of you, so I hope it's worth it.

I've been working for my entire career—about 15 years or so—in AI, trying to build more AI friends and co-workers. I wouldn't read too much into that; I have human ones too, I promise. Throughout the AI winters and lows of the last 15 years or so, I've managed to keep doing just that at Microsoft Cortana, building out Alexa at Amazon, working on PyTorch at Meta, and building my own AI startup that was working on a DevOps assistant. Now at Datadog, we're building out Bits AI, which is the AI assistant who's there to help all of you with your DevOps problems.

Today I'll talk a little about that, talk a little about the history of AI at Datadog, a little bit about how we think about AI agents today, and where we think things are going for the future.

## The Era Shift: Intelligence Becoming Too Cheap to Meter

Datadog is the observability and security platform for cloud applications. There's a lot that we do, but it all boils down to being able to observe what's happening in your system and take action on that—make it easier to understand, make it easier for us to simply understand and build out things to have a safer and more DevOps-friendly system.

We've been shipping AI for quite a while actually. It's not always in your face; it's not always out there saying "here's a big AI product," but things like proactive alerting, really understanding things like root cause analysis, impact analysis, and change tracking and much more has been happening since 2015 or so.

But things are changing. This is a clear era shift. I think of this in similar terms to the microprocessor or the shift to SaaS—bigger, smarter models, reasoning and multimodal coming, foundation model wars happening. This general shift where intelligence becomes too cheap to meter. What this means is products like Cursor are growing terribly fast, and really people are expecting more and more from AI every day.

With these advancements at Datadog, we're really trying to rise to meet this shift as well. The future is uncertain; this kind of ambiguity creates opportunity, but there's a lot of potential for us. That's kind of the dawning of this intelligence age. We're working to move up the stack to leverage these advancements and give even more to our customers by making it so that you don't use Datadog as just the DevOps platform, but also as AI agents that use that platform for you.

This requires work in a few key areas that I'll talk about: developing the actual agents, doing eval (you just heard a lot about eval—we think about that every day, for better or worse), and building out new types of observability.

## Our AI Agents: The On-Call Engineer and Software Engineer

There's a few agents that we're working on right now in private beta. The first is the **AI software engineer**—this kind of looks at problems for you, looks at errors, tries to recommend code that we can generate to help you improve your system. The second is the **AI on-call engineer**—this wakes up for you in the middle of the night, does your work, hopefully makes it so you have to get paged less frequently. And then we have a lot more on the way.

### The AI On-Call Engineer: Your 2 AM Hero

I'm going to talk a little bit about the AI on-call engineer first. This is the one that everyone wants to save them from that **2 AM alert**. You don't want to have to wake up in the middle of the night, go and look through your runbook, go and figure out what's going on if you can help it. Our on-call engineer is there to really make it so you can keep sleeping.

This agent proactively kicks off when an alert occurs and works to first situationally orient—read things like your runbooks, grab context of the alert—and then goes and figures out the kind of common stuff that each of you would do on Datadog already: look through logs, look through metrics, look through traces, and kind of act in this loop to figure out what's going on.

The on-call agent's great for both automatically running investigations for me, but also being able to look through and find summaries and find information for me before I even get to my computer. So if I want to get insights into why an alert just occurred or figure out why a trace might be showing an error, this agent can jump ahead, pull information for me, and show it to me.

We also have added a new page that makes it easy so that you can have human-AI collaboration. This is still something I'm thinking about a lot—what kind of collaboration do we expect? We want our agents to act as humans, but we also need to be able to verify what they did and be able to kind of look over what they're doing and really learn from it. It also helps you to kind of earn trust along the way. I can see the reason why this hypothesis, for example, was generated. I can see what the agent found, and I can make decisions about whether or not I agree along the way.

It also tells you things like what steps did it actually take out of your runbook, and kind of like a junior engineer who does this work, I can go ask follow-up questions, find out why I did a certain thing.

#### How It Works: Hypothesis-Driven Investigation

A little more insight into how we're making this happen: much like a human SRE or DevOps engineer, our agent works to put together hypotheses on what might be happening and reason over them, coming up with ways to test them. It uses tools in the tool-former sense to try out ideas, run queries against logs, metrics, etc., and work to validate or invalidate each hypothesis.

In the case that it does find a solid root cause, our agent can suggest remediations along the way. Again, just like a human might say "hey, we should page in that other team that's involved here," or it might offer to scale up or down your infrastructure. Over time, we plan to add more built-in actions and eventually discover new types of workflows based on what your team has done. But if you already have certain workflows that you set up in Datadog, we can tie directly into them and make it so that our agent can understand those workflows and how they might map to helping you remediate a problem.

And if it's a real incident, the on-call engineer is not usually done once an issue is remediated. You usually go and write a postmortem, you go try to learn from it, you share it with your team. Our agent can do the same—write out your postmortem for you, look at what occurred during the entire time, what it did, what humans did, and put that together so that you have something ready in the morning.

### The AI Software Engineer: Proactive Error Prevention

We also have this AI software engineer. I think of this as the proactive developer—the DevOps or software engineering agent who observes and acts on things like errors coming through. This is kind of the error tracking assistant. It automatically analyzes these errors, identifies causes, and proposes solutions. Those solutions can include generating a code fix and working to reduce the number of on-call incidents you have in the first place, so they can work in concert to make a better system over time.

In this case, the assistant has caught a recursion issue, proposes a fix, and even creates a recursion test so that we can catch it if it happens again in the future. We have the option to create a PR in GitHub or open the diff in VS Code for editing. This workflow significantly reduces the time spent by an engineer manually writing and testing code and greatly reduces human time spent overall.

## Key Lessons Learned: Building Effective AI Agents

So what have we learned building out these agents and some of the new ones that we're working on today? Well, we've learned quite a lot. There's a lot of things that we started with that we kind of went back and redid. But a few areas I'll touch on that I hope help you if you develop your own:

1. **Scoping tasks for evaluation**—it's very easy to build out demos quickly, much harder sometimes to scope and eval what's occurring
2. **Building the right team** who's ready to move fast and deal with the ambiguity that comes with these kind of problems
3. **The UX of old is changing**—that's something that everyone needs to be comfortable with
4. **Observability matters**—I'm sure it's surprising for Datadog to say that, but observability is terribly important even in this new era

### Scoping the Problems

Scoping the problems, scoping the work to be done—I like to think about this as defining jobs to be done and really kind of trying to clearly understand step by step what you'd like to do. Think about it from the human angle first and think about how another human might go and evaluate it. This is why we build out vertical, task-specific agents rather than building out generalized agents. We also want, where possible, this to be measurable and verifiable at each step.

This has honestly been one of the biggest pain points for us, and I think this is true for many people working in agents, where you can quickly build out a demo, you can quickly build something that looks like it works, but then it's very hard to actually verify that over time and improve it.

Use your domain experts, but use them more like design partners or task verifiers. Don't use them as the people who will go and kind of write the code or rules for it, because there is a big difference in how these kind of stochastic models work versus how experts work. You know, everyone kind of knows Noam and his anti-NLP rants, but that kind of stuff happens pretty frequently with domain experts.

**Eval, eval, eval**—I can't stress this enough. Start by thinking deeply about your eval. The number of mistakes we made by not thinking about eval first is frustrating and something that I think everyone should think about. It's very easy to build these demos, as I said, but everything in this fuzzy, stochastic world requires good eval—even something small to start. This means offline, online, and kind of living eval. Have end-to-end measurements, make it so you also instrument appropriately the way to know if humans are using your product right and giving you feedback, and then make this a living, breathing test set.

### Building the Team

Building the team—you don't have to have a bunch of ML experts. There aren't that many to go around right now. What you really need is you want to seed it with one or two and then have a bunch of optimistic generalists who are very good at writing code and very willing to try things out fast.

I'll also note that UX and front end matters more than I'd like as a backend engineer myself, but it's terribly important as you collaborate with these agents and assistants. And then you want teammates and people who are excited to be AI-augmented themselves. This is day-to-day AI use. This is explorer types who want to learn. This is a field that's changing fast, and if you don't have people like that, you're going to kind of get stuck. You want folks who kind of yearn for the vast and endless AI capabilities, right? It's a big world out there and there's a lot going on.

### The Changing UX Landscape

Ye old UX—this is one of those things that I still think about; we go back and forth every day. It's an area that I didn't realize was quite so important initially when I started working in this field. Despite my engineering sensibilities and lack of UX, it's terribly important. This is such an early space of work; this is kind of one of the more important things here as you collaborate and work together. But the old UX patterns are changing—be comfortable with that. And so far, I'm partial to agents that work more and more like human teammates instead of building out a bunch of new pages or buttons.

## Observability: Who Watches the Watchmen?

So who watches the watchmen, right? You have these agents running around. Observability is actually really important, and don't make it an afterthought. These are complex workflows; you really need situational awareness to debug problems, and this has saved us a lot of time as we start to work with a new view that we're calling **LLM observability** in the Datadog product.

Datadog in general has a full observability stack, as many of you know. We can look at GPUs, we can look at LLM monitoring, we can look at really your system end-to-end. But tying in the LLM observability has been very helpful because you have a wide variety of interactions and calls out to models—you're hosting models, you're running maybe models you're using through an API—and we can make them all kind of group together in the same pane of glass so you can look at them and debug what's occurring.

I will note, though, that this can get messy fast with agents. Our agent, for example, has very complex multi-step calls. You're not going to look at this and figure out what's going on right away. This can be **hundreds of calls**, this can be tons of different places where it's making decisions about tools, looping time and time again. And if you just look through a full list of these things, you'll never really figure out what's going on.

So here's a quick sneak peek into a more agent view of what's occurring inside of our observability tools. This is our agent graph. Really what this means is that I can kind of look at it just like our agent did and look at workflows that are occurring. You can see in this, even though it's a big graph, there's a bright red node here. If we zoom into that, we can actually see where errors were occurring. This is very human-readable, something that makes it super easy to figure out what's going on when your complex workflow is running.

### The Agent Application Layer Bitter Lesson

As an aside, though, I do also want to note what I think of as kind of like the agent or application layer bitter lesson: **general methods that can leverage new off-the-shelf models are ultimately the most effective by a large margin**. I hate to say it, but like you sit there, you fine-tune, you do all this work on the specific project, the specific task, and then all of a sudden OpenAI or someone comes out with a new model and it handles all this kind of quickly. A lot of the reasoning is solved for you.

We're not quite there where it handles all of it very quickly, but you should be at a point where you can easily try out any of these models and don't feel stuck to a particular model that you've been working on for a while. You know, rising tide lifts all boats here.

## Looking Ahead: Agents as Users and the Future of DevOps

I also think a lot about not just building agents, but what it might mean for other agents to be users of Datadog and other SaaS products. There's a good chance that **agents surpass humans as users in the next five years**. I'm probably somewhere in the middle on my estimate there—there are people who will tell you that'll happen in the next year, there are people who will tell you it'll happen in 10 years. I think we're somewhere around the five-year mark.

But this means that you shouldn't just be building for humans or building your own agents; you should really think about agents that might use your product as well. An example of this is like third-party agents like Claude might use Datadog directly. I set this up with MCP (Model Context Protocol) relatively quickly, but any type of agent that might be coming in and using your platform, you should think of the context you want to provide them, the information you want to provide about your APIs that agents would use more than humans.

## The Weird and Fun Future

So looking ahead, the future is going to be weird. It'll be fun, and AI accelerating is accelerating each and every day. I strongly believe that we'll be able to offer a **team of DevSecOps agents for hire** to each of you soon. You don't have to go and use our platform directly and integrate directly—ideally our agents will do that for you and our agents will handle your on-call and everything like that for you.

I also do think that AI agents will be customers. Many of you building out SRE agents and other types of agents, coding agents, should use our platform, should use our tools just like a human would, and we can't wait to see that.

And generally, I think that small companies out there are going to be built by someone who can use automated developers like Cursor or Devon to get their ideas out into the real world, and then agents like ours to handle operations and security in a way that lets an order of magnitude more ideas make it out into the real world.

Thank you so much. Please reach out if you're building any agents that want to use us, or if you'd like to check out our agents as well. There's a lot to build here, and if you want to work in the space, we are hiring more AI engineers and people who are just excited about it. But thank you very much.
