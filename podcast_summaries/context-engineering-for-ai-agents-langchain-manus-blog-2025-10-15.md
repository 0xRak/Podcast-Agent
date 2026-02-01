# Context Engineering for AI Agents with LangChain and Manus

**Source:** LangChain
**Speakers:** Lance Martin (LangChain Founding Engineer), Yichao "Pete" (Manus Co-Founder & Chief Scientist)
**Duration:** 1 hour
**Published:** October 2025
**URL:** https://www.youtube.com/watch?v=6_BcCthVvb8

---

## Introduction

As AI agents evolve from simple chatbots to autonomous systems capable of hundreds of tool calls, a new discipline has emerged: **context engineering**. This webinar brings together Lance Martin from LangChain and Yichao (Pete) from Manus to explore the critical challenge facing production AI agents today—managing context growth without sacrificing performance.

The core paradox is simple but profound: agents need extensive context to function (from tool calls, observations, and state), but model performance degrades as context windows fill up. This phenomenon, known as "context rot," means that the very thing agents need to be effective—rich contextual information—becomes their Achilles' heel.

---

## Key Insights

### 1. **Context Engineering Is the New Prompt Engineering**

Context engineering emerged in mid-2025 as a distinct discipline, following the same trajectory that prompt engineering took after ChatGPT's launch. As Andrej Karpathy defined it: "Context engineering is the delicate art and science of filling the context window with just the right information needed for the next step."

The shift reflects a fundamental change in how we build AI systems. In 2022, the challenge was "how do we prompt chat models effectively?" In 2025, it's "how do we manage context for autonomous agents that make 50+ tool calls per task?"

**Why this matters:** Manus observed that typical production tasks require around 50 tool calls. Anthropic reported that production agents engage in conversations spanning hundreds of turns. Every tool call adds observations to the message history, creating unbounded context explosion. Research from Crom demonstrated that performance drops measurably as context grows—creating a critical engineering challenge.

### 2. **The Five Pillars of Context Management**

Through analysis of production systems (Claude Code, Manus, Deep Agents, Open Deep Research), five core strategies have emerged:

**Offloading:** Don't keep all context in message history. Dump token-heavy tool outputs (like web search results) to the file system, returning only a minimal reference. The agent can retrieve the full data if needed, but it doesn't pollute the context window indefinitely.

- Used by: Manus, Claude Code, Deep Agents, Long-running agents
- Best for: Large tool outputs that may not always be needed

**Reducing:** Summarize or compress information before adding it to context. This can mean summarizing tool outputs, pruning old tool calls, or compacting message history.

- Used by: Claude 4.5 (now built-in), Claude Code, Open Deep Research
- Best for: Unavoidable context growth when offloading isn't enough

**Retrieving:** Pull context on-demand using indexing/semantic search or file-system tools like `glob` and `grep`.

- Cursor uses: Indexing + semantic search
- Claude Code uses: File system tools only
- Both approaches work—choose based on your use case

**Isolating:** Split context across multiple sub-agents, each with its own context window and separated concerns.

- Used by: Manus, Deep Agents, Claude Code (sub-agents), Cognition (Devon)
- Trade-off: Agent-to-agent communication becomes complex

**Caching:** Reuse KV cache across related requests to reduce cost and latency.

- Critical for production: Manus found that using frontier models with good caching infrastructure can be *cheaper* than open-source models at scale
- Design consideration: Tool definitions at the front of context affect cache reusability

### 3. **Manus's Battle-Tested Insights: Compaction vs. Summarization**

Pete from Manus introduced a crucial distinction that most teams miss: **compaction** and **summarization** are fundamentally different operations.

**Compaction is reversible:** Strip out information that can be reconstructed from external state. For example, when a "write file" tool executes, the compact format keeps only the file path—not the entire content—because the file exists in the environment and can be read again if needed.

**Summarization is irreversible:** Use an LLM to condense information, but you lose the ability to reconstruct the original. Manus handles this carefully by:
1. Offloading key context to files *before* summarizing
2. Dumping entire pre-summary context as a log file so it's retrievable
3. Using structured schemas (not free-form prompts) for summaries to ensure consistency
4. Keeping the last few tool calls in full detail so the model has recent examples

**The threshold strategy:** Manus identifies a "pre-rot threshold" (typically 128K-200K tokens, well below the model's hard limit) where quality starts degrading. When approaching it:
1. First: Apply compaction to the oldest 50% of tool calls
2. Check: How much context was freed?
3. If still not enough: Apply summarization to compacted data
4. Always: Keep recent tool calls in full detail for few-shot learning

### 4. **The Layered Action Space: Offloading Tools Themselves**

One of the most innovative ideas from Manus addresses a problem most teams haven't encountered yet: **tool overload**. With MCP (Model Context Protocol) enabling infinite tool extensibility, you can't simply add every possible tool to your function-calling space.

Manus's solution is a three-tier action space:

**Layer 1: Function Calling** (~10-20 atomic functions)
- Schema-safe thanks to constrained decoding
- Fixed set: read/write files, execute shell, search, browser operations
- Everything else is offloaded to lower layers

**Layer 2: Sandbox Utilities**
- Pre-installed CLI tools in the VM sandbox (format converters, speech recognition, even an MCP CLI)
- Accessed via the shell tool, so no additional function-calling overhead
- Great for large outputs; models can use `grep`, `less`, `more` to process results
- Example: All MCP tools are accessed via a CLI interface, not injected into function-calling space

**Layer 3: Packages & APIs**
- Python scripts using pre-authorized APIs and custom libraries
- Perfect for computation-heavy tasks (e.g., analyzing a year of stock data)
- Return only summaries to context, not raw data
- Highly composable: chain multiple API calls in one script

**The genius:** From the model's perspective, all three layers use the same interface—standard function calls to shell/file tools. No cache-breaking changes, no context overhead.

---

## Notable Quotes

> "Context engineering is the delicate art and science of filling the context window with just the right information needed for the next step." — Andrej Karpathy

> "Typical tasks require around 50 tool calls. Production agents can engage in conversations spanning hundreds of turns. The challenge is that agents, because they are increasingly long-running and autonomous, accumulate a large amount of context." — Lance Martin, LangChain

> "Be firm about where you draw the line. Right now, context engineering is the clearest and most practical boundary between application and model. Trust your choice." — Yichao (Pete), Manus

> "Do not communicate by sharing memory; instead share memory by communicating." — Go programming proverb (adapted for agents by Pete)

> "The biggest leap we've ever seen didn't come from adding more fancy context management layers or clever retrieval hacks. They all came from simplifying, from removing unnecessary tricks and trusting the model a little more." — Yichao (Pete), Manus

> "If you're at the scale of Manus and building a real agent where input is way longer than output, then KV cache is super important. Using flagship models with distributed caching can sometimes be even cheaper than open-source models." — Yichao (Pete), Manus

> "Avoid context over-engineering. Context engineering should make the model's job simpler, not harder. Build less and understand more." — Yichao (Pete), Manus

---

## Key Takeaways

### For AI Engineers Building Agents:

1. **Establish your context thresholds early.** Identify where performance degradation begins (typically 128K-200K tokens) and use it as your trigger for context management, not the model's hard limit.

2. **Use compaction before summarization.** Compaction is reversible and preserves the ability to reconstruct information from external state. Only summarize when compaction gains diminish.

3. **Structure your summaries.** Don't use free-form prompts for summarization. Define schemas with specific fields (files modified, goals, current state) to ensure consistency and completeness.

4. **Keep recent context detailed.** When compacting or summarizing old messages, always keep the last few tool calls in full detail. This provides few-shot examples and prevents the model from imitating compact formats.

5. **Choose your agent architecture based on evaluation across model tiers.** Test your architecture with both weaker and stronger models. If performance scales well when upgrading models, your architecture is future-proof.

### For Teams Scaling Production Agents:

6. **File systems are your friend.** The most common and effective offloading strategy across all production systems is dumping token-heavy outputs to files and returning minimal references.

7. **Sub-agents enable context isolation, but agent communication is hard.** Use schemas as contracts between agents. Have the parent agent define the output schema, then use constrained decoding to ensure sub-agents submit results that match.

8. **Consider the two patterns for sub-agents:**
   - **By communicating:** Sub-agent gets only a brief instruction, works independently, returns result (best for clear, isolated tasks)
   - **By sharing memory:** Sub-agent sees full parent context but has different system prompt/action space (best for complex tasks requiring history)

9. **Invest in caching infrastructure.** KV cache management can be more impactful than model choice. Frontier providers with distributed caching infrastructure may be cheaper than self-hosted open models at scale.

10. **Tool selection: Keep atomic functions minimal (~10-20), offload everything else.** Use sandbox utilities, scripts, and code execution for extended capabilities without bloating your function-calling space.

### Strategic Principles:

11. **Context engineering is your boundary, not fine-tuning.** Startups should lean on general models and context engineering as long as possible. Fine-tuning locks you into fixed action spaces and product behaviors that shift constantly in the AI-first world.

12. **Simplify aggressively.** Manus refactored their architecture five times in seven months. Each time they simplified, the system got faster, more stable, and smarter.

13. **Test with model diversity.** Don't just track benchmark scores. Fix your architecture and switch between models (weak to strong, different providers). If you gain a lot from model upgrades, your architecture is likely resilient to future model improvements.

14. **User ratings > benchmarks.** Manus found that high scores on academic benchmarks (like GAIA) didn't correlate with user satisfaction. Prioritize real user feedback (1-5 star ratings) over automated evals.

---

## Conclusion

Context engineering represents a fundamental shift in how we build AI applications. Just as developers mastered RESTful API design, database indexing, and caching strategies, a new generation of engineers is now learning to architect context flows for autonomous agents.

The lessons from LangChain and Manus are clear: simplicity wins. Don't over-engineer. Use file systems. Compact before you summarize. Keep tools minimal. Trust the model to handle more as it improves. And always remember that context engineering isn't about cramming more information into the window—it's about ensuring the *right* information is available at the *right* time.

As Pete from Manus wisely concludes: "Build less and understand more." In the rapidly evolving world of AI agents, the teams that master context engineering while maintaining architectural simplicity will be the ones that scale successfully from prototype to production.

The future belongs to those who can make their agents smarter by making their context windows leaner.

---

**Worth Watching?** Absolutely essential for anyone building production AI agents. This is packed with battle-tested insights from teams running agents at scale, not theoretical concepts. The Q&A section alone contains gold about real-world challenges like agent communication, tool selection, and evaluation strategies.

**Generated:** 2025-10-15
**Template:** Blog
