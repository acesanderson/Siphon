⠋ claude-sonnet-4-20250514 | [0/0] ✓ claude-sonnet-4-20250514 | [0/0]  | (51.6s)
⠋ Running 3 concurrent requests...⠋ Progress: 1/3 complete | 2 running | 0 failed | 12.0s elapsed⠋ Progress: 2/3 complete | 1 running | 0 failed | 22.7s elapsed⠋ Progress: 3/3 complete | 0 running | 0 failed | 44.0s elapsed✓ All requests complete: 3/3 successful in 44.0s
# This Month in DataDog: AI-Powered Observability and Data Visibility Solutions

## Introduction and Overview

Hi everyone, I'm Kevin H. On this month in DataDog, I'm joining Jeremy to chat about gaining visibility into your data sets throughout the entire data life cycle with DataDog data observability. That's on the latest episode of this month in DataDog.

Hello and welcome to this month in DataDog where we update you on our latest features, product announcements, events, and more. This month, we're switching gears from our usual roundup of new releases to bring you insightful conversations with folks from DataDog product and engineering. 

First, Tristan joins us to discuss saving time and effort when you're on call with Bits AAIS. We also dive into the biggest problems his team wants to solve for engineers. After that, Kevin joins us to chat about gaining visibility into your data sets throughout the data life cycle with DataDog data observability. We also discussed data as a new area of focus for DataDog, the concept of lineage, and why this space is important right now.

But before we get to those, we want to shout out DataDog's engineering blog. The engineering blog is where DataDog engineers share how they've solved interesting, deep technical challenges. A couple of recent posts are about building reliable log delivery to thousands of unpredictable endpoints and unwinding a shared database at DataDog scale. It's a great resource for learning something new or just getting inspired. You can find the engineering blog on DataDog's website, and we'll include a link to the blog in this video's description.

As always, be sure to subscribe to our channel. And while you're at it, give us a like, drop us a comment, or send us an email with your questions or suggestions.

## Bits AAIS: AI-Powered On-Call Engineering

So, the moment you're paged, Bits jumps right into action. In this case, we were paged because an endpoint on our flight query API is experiencing high latency. This will start its investigation by gathering context about the alert from your DataDog environment, your runbooks, and from lessons learned from previous investigations, all in **under a minute**. And like you or me, Bits is pulling related telemetry from your logs, metrics, traces, and more.

All right, check this out. This is the really cool part. Now, based on its initial findings, Bits will then generate a variety of hypotheses to what it thinks the problem could be and then go verify each one of them concurrently.

### The Problem Bits AAIS Solves

Tristan, thank you so much for joining. So, this year at Dash, you announced Bits AAIS, which helps on-call engineers autonomously solve or respond to alerts and solve some problems. It's been a while since I've been on call myself. So, can you tell us before we get to what the product does a little bit about the problem you're trying to solve?

We live in a very interesting time because observability has never been better. Yet, DevOps jobs and SRE jobs haven't gotten any easier. Systems are continuously getting more complex. There's just more to look at. So, it's even harder to make those connections, especially when you're on call. So, that's really kind of the problem that we're trying to solve here. 

Basically, we're trying to use AI to look across your entire system for problems and trying to find the root cause quickly. So, essentially, we're trying to find the holy grail of observability. We basically want to answer that classic question: you got paged at **2 a.m.** And we want to answer it with you got paged at 2 a.m., you look at your phone and Bits has the root cause right there. 

And this goes for both easy problems and hard problems. So, alerts where the problem's like a null pointer and it's obviously there — we want to be able for Bits to help with that. So kind of reduce alert fatigue and also the really hairy problems where the connections are very hard to find. So we should be able to do that with AI.

### Key Innovations and Differentiators

So that is a really difficult problem to solve and there's quite a bit going on there. If you had to pick the one thing you're most excited about solving, what would that be?

Yeah, for sure. I think the one thing that I'm really excited about solving is memories and learning from experience. So one thing — the idea is that as Bits does investigations you can kind of teach Bits when things went well and kind of tell it when it didn't so that it's continuously learning. So it kind of creates this virtuous cycle. So as you interact with Bits, it's learning more about your systems and learning more specifically how your system's set up. So for example, if your system is not really focused around service but around something like account ID or cluster, it can start to learn about that and be able to help you investigate things better. So it's going in with a bunch of context right from the beginning.

The two things that really sets us apart from the other agents is the DataDog platform. So, we have all your data under one roof and it's interconnected. So, it really helps us be able to traverse that data as opposed to cobbling together different integrations to pull them in. This actually gets really important when you think about things like data governance and RBAC because it's all under one roof — you can set policies that Bits can look at and also that people can look at from your investigations.

And the second big differentiator is our applied AI organization at DataDog. These folks have been bathing in the problems for years and they've been developing models and I think our partnership with them has really — is really something that the other agents really don't have.

## DataDog Data Observability: A New Focus Area

Kevin, thank you so much for joining. Really excited to talk to you about data observability, which is really a new focus area for DataDog. So, you recently joined DataDog through the acquisition of Metaplane. So, before we get to what you're doing now, can you tell us a little bit about Metaplane and what you were all doing over there?

### The Metaplane Foundation

Yeah, we founded Metaplane in **2019** to help companies trust the data that powers their businesses — whether it was analytics or automations or recently AI — and we helped hundreds of companies build this kind of trust. Technically the field is called data observability, but over time our customers began to call us "the DataDog for data." 

That was prescient because eventually they kept asking us to build the integrations that DataDog had already built — the places that data comes from and it moves through. And at the same time, DataDog was in parallel being asked to build integrations into the tools that Metaplane supported like Snowflake and Databricks. 

Ultimately there's this divide that we see between software teams that produce data and data teams that transform and consume data. This divide is pretty painful — it gets in the way of using data as a real competitive advantage within companies and really remediating and preventing data issues when they start at all. And so eventually joining forces made sense.

### Why Data Observability Matters Now

So, expanding on that a little bit for those that might not be as familiar with data and data observability. Can you tell us a little bit about it and why you think it's increasingly important especially now?

So, data has been one of the first applications of software within businesses — you can imagine like an IBM International Business Machines — it's that companies want to understand how they're doing. But in the past few decades we've seen data being used for operations and automations, and in the past few years for GenAI applications. Companies are increasingly realizing that their competitive advantage most of the time is not in the model itself but in the proprietary data that only they have.

So on that side we see that the stakes of data are higher than ever, and as such the need to have trust in that data is higher than ever because it's no longer like a quarterly board report — which yes, it is not a good look when it goes wrong — but when the data is being seen directly by a customer in real time all the time, you have to maintain that level of trust extremely high.

### Building Data Observability at DataDog

What we're building here is we're taking the strength of a standalone data observability product like Metaplane where we would connect with a customer's warehouse. We would get the downstream dependencies like — for example, data might be used in a BI application like Looker, maybe transformed in a tool like DBT and ingested with a tool like Fivetran. The problem was that by the time that we detected an issue within the data warehouse often the damage was already done.

So like imagine we work at a restaurant, right? And yes, it's great if we can test the food on the way to a customer's table. It's way better than giving a customer food poisoning, right? But ideally, we can test the food all along the supply chain like in the kitchen and before the kitchen. And that's really where DataDog shines in this space where instead of detecting for data issues when it lands before consumption, we can get visibility throughout the entire data life cycle because DataDog already has integrations to the thousands of applications that produce data and into the streams that move it, the jobs that transform it.

And you can think of DataDog data observability as the last mile, right? We have all the bridges between all these islands — let's get it to the final destination of where data is being used.

## AI Voice Interface and Future Innovations

A special thanks to Tristan and Kevin for chatting with me today. Before we go, we want to share a short video showcasing one of our latest products, AI Voice Interface, which helps you speed up incident response. Be sure to stick around for that. We'll see you next month.

"Hey Sha, just calling to inform you about a critical latency alert on checkouts. I can acknowledge it and share more details with you. You want me to do that?"

"Let's go ahead and acknowledge that."

"Sure thing. The **P99 latency** on checkouts has increased from **900 milliseconds to 5.5 seconds** starting about five minutes ago. I've acknowledged the alert so it won't escalate any further. I also have the linked runbook handy. Would you like me to share the suggested next step?"

"Yeah, let's get the first step. And could we also post to Slack in the checkout channel that's going on?"

"Got it. I've posted to Slack in #checkout ops. The suggested next step is to look at the upstream payments API for any latency or errors. Want me to pull that information for you?"

"Yeah, let's grab that."

"The error rate for the payments API has climbed to **8%**. It seems there was a deploy to the payments API shortly before our monitor went off. I can pull the next few steps from the runbook."

"I think I know what we have to move forward."

"No worries. Feel free to reach out if you need another pair of eyes. Let me know if there's anything else I can assist with."
