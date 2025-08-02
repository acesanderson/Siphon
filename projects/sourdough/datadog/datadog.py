from pathlib import Path
from Chain import Chain, AsyncChain, Model, ModelAsync, Prompt, ChainCache

Model._chain_cache = ChainCache()
ModelAsync._chain_cache = ChainCache()


paths = Path(__file__).parent.glob("*.*")
paths = [str(p) for p in list(paths) if ".md" in str(p) or ".txt" in str(p)]

prompt1 = """
Extract all content relevant to the following contextual focus:

<contextual_focus>
{{contextual_focus}}
</contextual_focus>

From the provided document, identify and extract:
1. Direct statements, quotes, or claims related to this topic
2. Supporting data, metrics, or evidence  
3. Strategic decisions, initiatives, or plans
4. Customer use cases, examples, or case studies
5. Competitive positioning or market analysis
6. Future roadmap items or announced developments

For each extracted item:
- Provide the specific text or paraphrase
- Note the source context (e.g., "CEO statement", "product demo", "Q2 earnings call")
- Indicate confidence level: Direct quote, Clear inference, or Implied from context

Group extractions by category and prioritize recent information and authoritative sources.

Exclude general company background, tangential mentions, and purely historical information unless strategically relevant.

If no relevant content is found, state "No relevant content identified."

Here's the document content:
<document_content>
{{document_content}}
</document_content>

Return ONLY your summary.
"""


prompt2 = """
Based on the following extracted summaries from multiple sources, create a unified analysis of:
<contextual_focus>
{{contextual_focus}}
</contextual_focus>

EXTRACTED SUMMARIES:
<summaries>
{{summaries}}
</summaries>

Synthesize this information into a coherent summary that addresses:
- Key themes and strategic direction
- Supporting evidence and data points
- Notable contradictions or gaps between sources
- Actionable insights and implications

Structure your response with clear sections. Prioritize information from authoritative sources and recent developments. Where sources conflict or information is uncertain, note this explicitly.

Focus on providing a comprehensive yet concise understanding suitable for strategic decision-making.
"""

# Our contextual focus
contextual_focus = (
    "Datadog's GTM / thought leadership / product strategy in the age of generative AI."
)
prompt = Prompt(prompt1)

# generate async input variables
input_variables_list = []
for p in paths:
    document_content = Path(p).read_text()
    input_variables_list.append(
        {
            "contextual_focus": contextual_focus,
            "document_content": document_content,
        }
    )

# Async chain
model = ModelAsync("gemini")
chain = AsyncChain(
    model=model,
    prompt=prompt,
)
responses = chain.run(input_variables_list=input_variables_list)

# Combine responses into a single summary
model = Model("gemini2.5")
prompt = Prompt(prompt2)
chain = Chain(model=model, prompt=prompt)
response = chain.run(
    input_variables={
        "contextual_focus": contextual_focus,
        "summaries": "\n\n".join([str(r.content) for r in responses]),
    }
)
print(response)
