# News to Video AI Agent

**AI Agentic Application that transforms latest AI & Robotics news into educational blog posts, LinkedIn content, and positive, accessible videos for non-technical audiences.**

Created: December 30, 2025  
Status: Conceptual / Early Planning

## 🎯 Project Goal

This application automatically:

1. Finds the latest credible news about **AI and robotics advancements**
2. Evaluates realistic, balanced impact on **daily life**, **jobs**, and the **long-term future**
3. Converts insights into **high-quality text content** (blog articles + LinkedIn posts)
4. Produces **short, positive, human-centric videos** explaining the news in plain language
5. Ensures all output is **educational, enriching, optimistic**, and avoids fear-mongering

Target audience: non-technical people who want to stay informed without being overwhelmed by jargon or doom narratives.

## 📋 Core Requirements

- **Input focus**: Latest trends & breakthroughs in AI and robotics
- **Analysis**: How it affects everyday life, employment landscape, and future society
- **Text output**:
  - ~800-word educational blog post
  - Professional LinkedIn post (Hook → Value → CTA format)
- **Video output**:
  - 2–4 minute video in plain English
  - Positive tone, inspiring visuals, uplifting background music
  - Ends with actionable “What you can do today” segment
- **Tone guardrails**: Always pivot negatives → opportunities; emphasize human creativity, new roles, accessibility

## 🏗️ Architecture Overview

Multi-agent system built with **CrewAI** or **LangGraph**.

Four specialized agents collaborate in sequence:

| Agent                | Role                        | Main Responsibility                              | Key Tools / LLM Calls                  |
|----------------------|-----------------------------|--------------------------------------------------|----------------------------------------|
| Trend Researcher     | Scraper & Analyst           | Find + filter latest credible AI/robotics news   | Tavily / Serper.dev                    |
| Impact Strategist    | Evaluation Engine           | Analyze socio-economic impact (positive lens)    | Gemini 1.5 Pro / GPT-4o reasoning      |
| Content Specialist   | Copywriter                  | Write blog post + LinkedIn content               | Long-context writing                   |
| Video Producer       | Script & Visual Logic       | Create video script + call video generation API  | HeyGen / InVideo AI / Sora + ElevenLabs|

### System Layers

1. **Input Layer**            – Triggers, user queries, scheduling  
2. **Orchestration Layer**    – CrewAI / LangGraph (agent coordination, memory, retries)  
3. **Agent Processing Layer** – The 4 core agents  
4. **Tool / Integration Layer** – Search, LLM, Video & Voice APIs  
5. **Output Layer**           – Markdown/HTML posts + MP4 video files  
6. **Guardrails Layer**       – Positivity enforcement, sentiment checks

### High-Level Architecture Diagram (Mermaid)

```mermaid
graph TD
    A[Triggers<br>User / Cron] --> B[Orchestrator<br>CrewAI or LangGraph]

    B --> C[1. Trend Researcher]
    C -->|News summaries + sources| D[2. Impact Strategist]

    D -->|Positive impact analysis| E[3. Content Specialist]
    E -->|Blog post + LinkedIn text| F[4. Video Producer]

    F -->|Video script| G[Video Generation API<br>HeyGen / InVideo / Sora]
    F -->|Narration text| H[Voice Synthesis<br>ElevenLabs]

    G & H --> I[Final Video<br>MP4 + hosted link]

    subgraph "Output Artifacts"
        J[Blog Post .md / .html]
        K[LinkedIn Post text]
        I
    end

    E --> J & K
![workflow](https://github.com/user-attachments/assets/c57fa246-a3c8-4914-a10b-a44bfe979ae7)

