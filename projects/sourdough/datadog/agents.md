⠋ claude-sonnet-4-20250514 | [0/0] ✓ claude-sonnet-4-20250514 | [0/0]  | (12.2s)
⠋ Running 3 concurrent requests...⠋ Progress: 1/3 complete | 2 running | 0 failed | 16.4s elapsed⠋ Progress: 2/3 complete | 1 running | 0 failed | 19.8s elapsed⠋ Progress: 3/3 complete | 0 running | 0 failed | 33.7s elapsed✓ All requests complete: 3/3 successful in 33.7s
# Introducing DataDog's AI Agents Console: Comprehensive Monitoring for Enterprise AI Agents

Hi everyone, my name is Kathy Lynn and I'm a senior product manager here at DataDog. So, Victor just walked us through how DataDog helps teams evaluate the performance of the custom AI agents those teams are building. But there's now an ever growing number of external agents integral to the business that these teams don't build in-house.

Understanding these third-party agents' behavior is equally as important to achieve new efficiencies and accelerate innovation. And we've heard from you that keeping track of what each agent is doing and how they're interacting with each other is extremely challenging, especially when you're worried about security breaches or wasted investments.

## The Solution: DataDog's AI Agents Console

The good thing is DataDog is all about providing visibility to help teams scale safely. To help solve the challenges that come with integrating AI agents, I'm excited to introduce **DataDog's AI Agents Console**.

With AI Agents Console, you can now monitor the behavior and interactions of any AI agent that's a part of your enterprise stack. Whether that's:
- A computer use agent like OpenAI's Operator
- IDE agent like Cursor
- DevOps agent like GitHub Copilot
- Enterprise business agent like Agent Force

All in addition to your internally built agents.

## Key Monitoring Capabilities

With this visibility into both custom and external agents, DataDog helps you understand:
- Which agents are supporting your business and what actions are they executing
- Are they doing so securely and with the proper permissions?
- Do they deliver measurable business value?
- How are your end users engaging with your agent-powered business?

## Live Demonstration: Comprehensive Agent Monitoring

So, let's jump into DataDog, observe these agents, and get some answers. With a few simple setup clicks, I can instantly see a comprehensive summary of every agent that's powering my business. And for each of these agents, I get key insights out of the box.

For example, I can see the **total monthly costs** of using these agents as well as the **error rate** across each of my agents to easily detect the most ineffective ones for further investigation.

### Deep Dive: Anthropic Computer Use Agent

Now, let's deep dive into one of these agents, Anthropic computer use agent powered by Claude Sonnet 3.5. Here, Claude Sonnet powers my Slack-based AI agent, which creates personalized spreadsheets for each of my customer success managers of their churned customers and the respective product features that have blocked implementation—requiring Sonnet to access multiple systems like Salesforce, Jira, and Google Drive.

I can also see more granular insights about this agent such as the task completion status, which actions Sonnet took and which ones failed. And when I want to dive deeper into this agent's performance, security, or business value, I can do so by using the tabs on the left.

## Real-Time Issue Detection and Resolution

And if there's an increase in the number of task failures, I'm alerted instantly. So, let me click into this tile to see why this spike is happening.

This brings me to the activity insights tab where I can see user engagement insights like daily active users, who my power users are, and quickly filter to those failed sessions without needing to write a single query. And it looks like we have quite a few failed interactions here. So, I'm going to click into one to see what's going on.

### Action Replay Feature

By doing so, I get a replay of every action this agent has taken, which is amazing because I've just gone from not knowing what this agent is doing at all to seeing exactly where it's clicking and what it's entering into the browser—like signing into Salesforce or navigating into the analytics tab to pull that list of churned customers.

I can also click anywhere on the corresponding events timeline on the right to jump to that exact moment in the replay.

Now let's see if we can figure out why this interaction failed with this error. I can click into this details side panel which quickly reveals why the agent has failed to generate that requested spreadsheet. It looks like it lacked proper permissions in Salesforce to view customers' churn states. This led to the agent repeatedly trying to query on an unavailable field.

So by simply granting Sonnet proper permissions, I can restore user engagement and boost the business value that Sonnet provides.

## Summary: Innovation with Confidence

To summarize, DataDog's AI Agents Console allows you to innovate safely and with confidence. You'll get:
- **Full visibility** into every agent's actions
- **Insights** into the security and performance of every agent
- **Quantifiable business value** for all of your agents
- **Proof** that your agentic AI investments are paying off with your end users

And we can't wait to get this to all of you. Sign up to become one of our design partners by following the link above. Thank you.
