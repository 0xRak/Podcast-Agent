# Podcast Tool Roadmap

## 🚀 Phase 1: Core Slash Command Enhancements (CURRENT PRIORITY)
**Status:** In Development
**Priority:** Immediate
**Estimated Effort:** 2-3 days

### Combined `/podcast-report` Command
Create single command that runs extract + summarize automatically, eliminating the need for manual two-step workflow.

### Weekly Batch Processing `/weekly-podcast-report`
Category-based weekly reports with enhanced format:
- Crypto Weekly Digest
- AI Weekly Digest
- Master weekly overview with cross-podcast analysis
- Extended intro explaining processed podcasts
- Trending topics across categories

### Command Naming Consistency
- Rename `/podcast_summary` → `/podcast-extract` for clarity
- Update all documentation and help text

---

## 🎯 Phase 2: Natural Language Interface
**Status:** Planned
**Priority:** Next
**Estimated Effort:** 3-4 days

### Natural Language Parser `/podcast-query`
Allow users to query in natural language:
- "summarize the podcasts for last week for empire and forward guidance"
- "Get me the AI podcasts from the last 2 weeks"
- "Weekly crypto digest for this week"

### Smart Channel/Category Mapping
- Intelligent mapping between natural language and channels
- Support aliases (e.g., "Empire" → @Empirepodcast)
- Category shortcuts ("crypto podcasts", "AI shows")
- Fuzzy matching for channel names

### Confirmation & Execution Flow
Parse → Display interpreted command → Ask confirmation → Execute

---

## ⚙️ Phase 2.5: Agent SDK Automation Pilot
**Status:** Planned
**Priority:** Later
**Estimated Effort:** 2-3 days

### Goal
Introduce Anthropic Agent SDK to automate a small, high-value segment without replatforming the pipeline.

### Scope (Pilot)
- Replace `ClaudeAnalyzer` JSON extraction with Agent SDK tool-calling to reliably produce structured analysis.
- Keep existing CLI orchestration; no changes to transcript extraction or deterministic `summarize.py`.

### Success Criteria
- ≥95% valid JSON parse rate across sample transcripts.
- ≤20% cost increase vs current analysis step; p95 latency ≤1.2x.
- Clear, auditable tool traces for analysis runs.

### Triggers to Execute Pilot
- Rising weekly batch retries/failures (>5%).
- Need unified extract→analyze→summarize automation with retry/resume.
- Desire for richer observability on analysis steps.

### Next (Post-Pilot, if green)
- Consider an end-to-end `/podcast_report` agent to orchestrate extract → analyze → summarize → export with resume/retries.

---

## 📋 Phase 3: Topic Research Functionality
**Status:** Planned
**Priority:** Future Enhancement
**Estimated Effort:** 2-3 days

#### Overview
Add a new `/topic_research` command that searches YouTube for videos on specific topics, finds relevant creators, extracts transcripts, and generates comprehensive research reports.

#### Use Case Example
```bash
/topic_research "personal finance bonds" --creators=5 --videos=10 --days=90
```
*Research what the main personal finance creators say about bond investing*

#### New Command Structure
```bash
/topic_research "search query" [options]

Options:
--creators=N     # Number of top creators to analyze (default: 5)
--videos=N       # Max videos per creator (default: 2)
--days=N         # Days to look back (default: 90)
--min-views=N    # Minimum view count filter
--output=PATH    # Custom output directory
--template=TYPE  # Report template (research|comparison|summary)
```

#### Implementation Plan

##### 1. Create New YouTube Search Module (`src/extractors/youtube_search.py`)
- **YouTube Search API Integration**: Use yt-dlp to search YouTube for topic keywords
- **Relevance Filtering**: Score videos by title/description relevance to search query
- **Creator Discovery**: Identify top creators discussing the topic
- **Metadata Extraction**: Extract video details (views, dates, duration, etc.)
- **Duplicate Detection**: Avoid processing same creator/topic combinations

##### 2. Create Topic Research Command (`src/topic_research.py`)
- **Command Parser**: Handle arguments like query, creator count, video limits
- **Search Orchestration**: Coordinate search → filter → extract → analyze workflow
- **Creator Grouping**: Group results by channel/creator for organized analysis
- **Progress Tracking**: Show search and processing progress
- **Smart Filtering**: Prioritize high-quality, recent, relevant content

##### 3. Create Research Report Generator (`src/processors/research_formatter.py`)
- **Multi-Creator Analysis**: Aggregate insights across different creators
- **Consensus Detection**: Identify common themes vs. divergent opinions
- **Creator Profiles**: Brief descriptions of each creator's perspective
- **Topic Summary**: Comprehensive overview of the research topic
- **Citation Management**: Track sources and quotes properly

##### 4. Enhance Existing Components
- **Extend YouTubeExtractor**: Add search capabilities and relevance scoring
- **Update TranscriptStorage**: Support topic-based file organization
- **Enhance ConfigManager**: Add topic research settings
- **Extend ProgressTracker**: Support search operation tracking

##### 5. Create Research Templates
- **Research Report Template**: Professional format for topic analysis
- **Creator Comparison Template**: Side-by-side creator perspectives
- **Topic Summary Template**: Executive summary format
- **Brief Template**: Quick overview for fast consumption

#### Expected Output Format
```markdown
# Personal Finance Bonds Research Report

**Generated:** 2025-01-15 14:30 UTC
**Search Query:** "personal finance bonds"
**Creators Analyzed:** 5
**Videos Processed:** 8
**Content Duration:** 3h 45m

## Topic Overview
Analysis of how top personal finance creators discuss bond investing, covering duration risk,
inflation protection, portfolio allocation strategies, and current market conditions.

## Creator Perspectives

### Ben Felix (@BenFelixCSI)
**Videos Analyzed:** 2 | **Total Duration:** 45m | **Avg Views:** 250K
- **Main Position**: Bonds serve as portfolio stabilizers with specific duration targeting
- **Key Insights**: Duration risk management, real vs nominal returns, yield curve analysis
- **Notable Quote**: "The duration of your bonds should match your investment timeline"

### Graham Stephan (@GrahamStephan)
**Videos Analyzed:** 2 | **Total Duration:** 32m | **Avg Views:** 180K
- **Main Position**: Bonds are "boring but necessary" portfolio components
- **Key Insights**: I-bonds for inflation protection, Treasury vs corporate bonds
- **Notable Quote**: "I-bonds are free money if you can stomach the restrictions"

### The Plain Bagel (@ThePlainBagel)
**Videos Analyzed:** 2 | **Total Duration:** 28m | **Avg Views:** 95K
- **Main Position**: Bonds provide stability but require understanding of risks
- **Key Insights**: Interest rate sensitivity, credit risk assessment
- **Notable Quote**: "Bond prices and interest rates have an inverse relationship"

## Consensus vs. Divergence

### Points of Agreement
- ✅ Bonds reduce portfolio volatility
- ✅ Duration risk is a key consideration
- ✅ Inflation-protected bonds have merit in current environment
- ✅ Bond allocation should increase with age/risk aversion

### Points of Debate
- 🔄 **Duration Preferences**: Short-term vs long-term strategies
- 🔄 **Corporate vs Treasury**: Credit risk tolerance varies
- 🔄 **International Bonds**: Currency hedging opinions differ
- 🔄 **Bond ETFs vs Individual**: Liquidity vs control tradeoffs

## Key Research Findings

### 🎯 Strategic Insights
1. **Duration Matching**: Bond duration should align with investment timeline
2. **Inflation Hedge**: I-bonds and TIPS recommended for inflation protection
3. **Rate Environment**: Rising rate periods favor shorter duration bonds
4. **Portfolio Role**: Bonds serve as volatility reducer, not return maximizer

### 🚀 Actionable Takeaways
1. **Allocation Strategy**: Use age-based bond allocation as starting point
2. **Duration Management**: Match bond duration to when you need the money
3. **Inflation Protection**: Allocate 5-10% to inflation-protected bonds
4. **Rebalancing**: Review bond allocation quarterly, especially in volatile markets

### 📊 Market Context
- **Current Environment**: Rising rate environment favors shorter durations
- **Historical Performance**: Bonds provided 4-6% annual returns historically
- **Risk Factors**: Duration risk, credit risk, inflation risk, liquidity risk

## Content Sources
- 8 videos analyzed from 5 creators
- Combined audience reach: ~2.1M views
- Content timeframe: Last 90 days
- Total analysis duration: 3h 45m

---
*Research conducted with /topic_research command | Generated by Podcast Research Tool*
```

#### New Files to Create
1. `src/topic_research.py` - Main command handler
2. `src/extractors/youtube_search.py` - Search functionality
3. `src/processors/research_formatter.py` - Report generation
4. `config/topic_research.yaml` - Configuration settings
5. `templates/research_report.md` - Output template

#### Integration Points
- Reuse existing transcript extraction and storage systems
- Leverage current Claude analysis capabilities for content processing
- Extend progress tracking for search operations
- Add new slash command integration following existing patterns
- Maintain same error handling and logging standards

#### Configuration Settings (`config/topic_research.yaml`)
```yaml
search:
  max_results_per_query: 50
  relevance_threshold: 0.7
  min_video_duration: 300  # 5 minutes
  max_video_duration: 7200  # 2 hours

creators:
  min_subscriber_count: 10000
  max_creators_per_topic: 10
  videos_per_creator: 3

analysis:
  focus_areas: ["consensus", "divergence", "insights", "actionable_takeaways"]
  include_creator_profiles: true
  cite_sources: true

output:
  default_template: "research"
  include_statistics: true
  save_raw_transcripts: true
```

#### Technical Considerations
- **Rate Limiting**: Implement proper delays between YouTube API calls
- **Caching**: Cache search results to avoid duplicate API calls
- **Scalability**: Support for large topic research (20+ creators, 50+ videos)
- **Quality Control**: Filter out low-quality or off-topic content
- **Ethical Usage**: Respect YouTube's terms of service and creator rights

---

## 🎯 Future Enhancements

### Phase 2: Advanced Research Features
- **Trend Analysis**: Track topic discussions over time
- **Creator Networks**: Identify relationships between creators
- **Sentiment Analysis**: Analyze creator sentiment on topics
- **Interactive Reports**: Generate searchable, interactive research reports

### Phase 3: Integration Features
- **API Access**: REST API for programmatic research
- **Scheduled Research**: Automated periodic topic monitoring
- **Alert System**: Notifications when new content appears on tracked topics
- **Export Options**: CSV, JSON, and database export capabilities

---

## 📝 Implementation Notes

**Dependencies to Add:**
- Enhanced search capabilities in yt-dlp usage
- Text similarity scoring for relevance filtering
- Template engine for flexible report generation

**Testing Strategy:**
- Test with various topic types (finance, tech, health, etc.)
- Validate search result quality and relevance
- Ensure proper creator attribution and citation
- Test with different creator counts and video limits

**Documentation Updates:**
- Update README with topic research examples
- Add configuration documentation
- Create usage guide for research workflows
- Document output format specifications

---

*Roadmap last updated: January 15, 2025*