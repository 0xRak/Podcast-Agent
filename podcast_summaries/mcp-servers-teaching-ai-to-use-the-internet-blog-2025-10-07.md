# MCP Servers: Teaching AI to Use the Internet Like Humans

**Source:** Every Podcast
**Guest:** Alex Ratray, Founder & CEO of Stainless
**Duration:** 51 minutes
**Published:** October 2025
**URL:** https://www.youtube.com/watch?v=lctDoa5M880

---

## Introduction

The internet was built for computers to talk to each other—but its entire architecture predates the AI revolution. Now, as we try to connect large language models to the web through the Model Context Protocol (MCP), we're discovering that the first generation of solutions isn't working as well as we hoped.

In this conversation, Alex Ratray, founder of Stainless (the company behind API infrastructure for OpenAI, Anthropic, and other major tech companies), shares a provocative vision for the future: instead of giving AI agents hundreds of specialized tools, we should give them just two—one to execute code, and one to search documentation. This approach could solve the fundamental scalability and security challenges plaguing current MCP implementations.

---

## Key Insights

### 1. **Current MCP Servers Are Hitting Fundamental Limitations**

The promise of MCP is compelling: imagine typing "refund Dan for those striped socks he bought yesterday and send him a discount code" into ChatGPT, and having the AI autonomously navigate through Stripe, create the refund, generate a discount code, and send it via email—all without human intervention.

But there's a problem. To truly replicate what a human operator can do, an AI would need access to *every* possible action in *every* tool they use. For a service like Stripe alone, that means hundreds of API endpoints. If you translate each endpoint into an MCP tool with full documentation, you've just consumed your entire context window before the AI even starts working.

As Alex explains: "If you were to take that list of tools today and go to an LLM and say, 'Hey, here's our MCP definition for all of this,' you've just burned through your entire context budget—maybe hundreds of thousands of tokens just there."

The result? Most MCP implementations today are highly constrained, handcrafted experiences that work for a few specific use cases but can't scale to the full breadth of what humans do with software.

### 2. **Code Execution Could Replace Thousands of Tools**

Alex proposes a radical simplification: instead of exposing hundreds of individual tools, give the AI just two:

1. **A code execution tool** where the model writes TypeScript/Python using the API's SDK
2. **A documentation search tool** for when the model needs clarification

This approach leverages what language models are already excellent at—writing code—while dramatically reducing context usage. When the AI needs to search through paginated transaction lists to find "Dan with the striped socks," it doesn't make dozens of round-trip tool calls. Instead, it writes a few nested loops that execute instantly on a server, returning only the final result.

"The context hit coming back from all of this is going to be like 10 lines of text," Alex notes. "It runs super fast because it's just CPU code running in the cloud right next to the Stripe API."

The code execution model also enables static type checking. When an AI hallucinates a non-existent API endpoint like `stripe.transactions.list`, the type checker can catch the error and suggest correct alternatives like `payment_intents`, `orders`, or `balance_transactions`—complete with inline documentation.

### 3. **Security Must Happen at the API Layer, Not the MCP Layer**

One of the most underexplored aspects of MCP is security. Current implementations try to implement security by limiting what's exposed through the MCP interface—but this is fundamentally flawed.

"At the end of the day, the security has to take place at the API layer itself," Alex argues. "You could do anything that's in the API under the hood, right? What people should be doing is using OAuth with granular permissions, with proper scopes."

This becomes even more critical when you're giving an AI the power to execute arbitrary code. Alex's vision involves sandboxed code execution environments with strict network controls—for example, ensuring that code running in a Stripe sandbox can only make requests to `api.stripe.com` and nowhere else.

The challenge? OAuth scopes are "pretty hard to build," and most APIs don't have sufficiently granular permission systems. This is an area ripe for innovation.

### 4. **The Future Is "Cyborgs"—AI Combined with Traditional Code**

Alex provocatively declares that "the future of AI is cyborgs"—not in the sci-fi sense, but in the sense that the most powerful AI agents will be hybrids of neural networks and traditional CPU-based software.

This manifests in two ways:

**For one-off operations:** Instead of the AI making dozens of tool calls, it writes code that executes traditional software functions at CPU speed, with the AI only involved at the planning and result-interpretation stages.

**For production systems:** Patterns that AI discovers and uses repeatedly (like "refund customer when they report defective socks") can be codified into permanent automation—essentially turning one-time AI solutions into enduring software.

Alex is already experiencing this at Stainless, where he uses MCP servers to query their PostgreSQL database, cross-reference data in HubSpot, search notes in Notion, and review call transcripts in Gong—all through natural language. He's also having Claude Code maintain a git repository of insights, SQL queries, and customer quotes that accumulate over time as a knowledge base.

"I have a notes folder in a special git repo," Alex shares, "and I'm like, 'Hey, when you find interesting customer quotes, put them in this folder with full citations.' So the next time I ask interesting questions, it doesn't have to search through the MCP servers again—they're cached in markdown files."

---

## Notable Quotes

> "APIs are the dendrites of the internet. Just like there's no thought happening in a brain without connections between neurons, there's nothing going on in the internet without APIs connecting servers."

> "We haven't figured out how to expose an API ergonomically to an LLM in the same way that we've figured out how to expose it ergonomically to a Python developer. That's a new research problem, and it's harder because I can learn how to be a Python developer, but I can't really learn how to think or see like an LLM."

> "If you have a small API, exposing every endpoint as a tool works great. But if you have a large API, you need dynamic mode: three tools—list endpoints, get endpoint details, and execute endpoint. That scales really well for context, but it means three model turns just to do one thing."

> "The only way you really 'build a tool' once we have code execution is with instructions, with prompts. The full power of everything you could do in the Gmail API is all there in one tool—but you still need specific prompts to help the LLM perform sequences of actions as productively as possible."

---

## Key Takeaways

### For Product Teams Building with MCP:

1. **Keep tool counts low and descriptions precise.** Current LLMs perform best with a small number of well-designed tools rather than comprehensive API coverage. Each tool should have a clear, specific purpose with minimal input parameters.

2. **Think hard about product management, not just engineering.** The companies succeeding with MCP today are those who deeply understand their users' actual workflows and design tools specifically for those use cases, rather than trying to expose their entire API surface.

3. **Implement feedback loops.** Consider adding a "send feedback" tool so your MCP server can learn when responses are useful or "useless garbage," as Alex puts it.

### For API Providers:

4. **Invest in code execution infrastructure now.** The trajectory is clear—the winning pattern will be giving AI agents sandboxed environments to execute code against your API using well-typed SDKs, not proliferating hundreds of individual tool definitions.

5. **Design for static typing and great error messages.** When an AI hallucinates an incorrect API call, your type system should catch it and suggest the correct endpoints with inline documentation.

6. **Build granular OAuth scopes.** Security at the MCP layer is insufficient. You need API-level permissions systems that can enforce principle of least privilege for AI agents.

### For Teams Adopting AI Agents:

7. **Start building institutional knowledge repositories.** Follow Alex's pattern: have your AI agents maintain git repositories of useful queries, insights, and patterns. Structure can come later—start by accumulating knowledge in markdown files.

8. **Accept that this is experimental.** Even at Stainless, a company at the cutting edge of API infrastructure, MCP usage is still in "playing around mode" with paper cuts and disconnections. Set realistic expectations.

9. **Focus on operations, not production software (for now).** The sweet spot today is one-off operational tasks that require navigating multiple SaaS tools—customer support, business analysis, administrative workflows—rather than customer-facing production systems.

---

## Conclusion

The first wave of MCP servers revealed both the enormous potential and the significant limitations of current approaches to connecting AI with the internet. We're trying to retrofit AI agents into an API ecosystem designed for human developers and deterministic software, and the seams are showing.

Alex Ratray's vision points toward a more sustainable path: rather than multiplying tools and documentation until we overwhelm both models and humans, we should embrace what language models do best—writing code—and build the infrastructure to let them do it safely and efficiently.

The companies that figure out this transition first—from hand-crafted MCP tools to sandboxed code execution with excellent SDKs and type systems—will have a significant advantage in the AI-first decade ahead. The internet's architecture may have been built for a pre-AI world, but we're now in the process of building the bridges that will let AI navigate it natively.

As Alex notes, we're not quite there yet. But we're close enough that forward-thinking teams should start preparing now.

---

**Worth Listening?** Absolutely, especially if you're building MCP servers, designing API infrastructure, or thinking about how AI agents will interact with your product. This is a rare opportunity to hear from someone who's both deeply technical and actively working on next-generation solutions to these problems.

**Generated:** 2025-10-07
**Template:** Blog
