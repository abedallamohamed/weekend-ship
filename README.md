# Weekend Ship

AI-powered project planning assistant that transforms your ambitious ideas into realistic, actionable weekend projects. Get time-boxed plans with concrete tasks to ship an MVP in 48 hours.

## Quick Start

```bash
# Clone and start the application
git clone https://github.com/abedallamohamed/weekend-ship.git
cd weekend-ship

# Create .env file with your OpenAI API key
OPENAI_API_KEY=your_openai_api_key_here

# Start with Docker Compose
docker compose up

# Access at http://localhost:5173
```

**Requirements:** Docker, OpenAI API key in `.env` file:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

## The Problem

Developers often have great project ideas but struggle with realistic scoping and concrete task breakdown. Most projects either never start or fail due to overambitious planning that ignores weekend time constraints.

## Product Design Decisions

### 🎯 **Target User & Use Case**
- **Solo developers** planning weekend coding projects
- **Time constraint**: Saturday + Sunday (18-20 hours realistic coding time)
- **Output**: Working MVP, not production-ready application

### 🤖 **AI Interaction Design**
- **Chat-based interface** for natural project description
- **Hybrid conversation flow**: 
  - First message → Generates structured project plan (JSON)
  - Follow-up messages → Conversational Q&A and plan refinements
- **Progressive disclosure**: Show overview first, then detailed timeline

### 📋 **Task Management Philosophy**
- **Essential vs Optional** task classification for flexible prioritization
- **Time-boxed blocks** (Saturday Morning, Afternoon, etc.) for realistic planning
- **Checkable tasks** with local state management (no AI overhead)
- **Visual progress tracking** with completion status

### 🎨 **UX/UI Decisions**
- **Single-page chat interface** - familiar pattern, low learning curve
- **Structured plan visualization** - converts AI output into actionable format
- **Optimistic UI updates** - instant checkbox feedback, background API sync
- **Markdown support** in responses for rich formatting

## Architecture Decisions

### 🔧 **Tech Stack**
- **Frontend**: SvelteKit 5 + TypeScript (fast dev, small bundle)
- **Backend**: FastAPI + Python (rapid AI integration, type safety)
- **AI**: OpenAI GPT-4o (reliable JSON generation, conversational ability)
- **Persistence**: In-memory storage (MVP simplicity, session-based)
- **Containerization**: Docker Compose (easy deployment)

### 🏗️ **Key Architectural Choices**

**1. Dual Prompt System**
- `WEEKEND_PLANNER_PROMPT` → Structured JSON planning
- `CONVERSATION_PROMPT` → Follow-up Q&A and refinements
- *Tradeoff*: More complex logic vs better user experience

**2. Unified JSON Response Format**
```json
{
  "message": "Conversational response",
  "projectPlan": { /* structured plan or null */ }
}
```
- *Benefit*: Predictable parsing, supports both planning and conversation
- *Tradeoff*: Slightly more tokens vs parsing reliability

**3. Client-Side Task Completion Tracking**
- Task completion state managed locally, not sent to AI
- *Benefit*: Saves tokens, reduces API costs
- *Tradeoff*: No AI awareness of progress vs performance

**4. Session-Based User Identification**
- No authentication, users identified by session cookies
- *Benefit*: Zero friction for MVP testing
- *Tradeoff*: No persistent user accounts vs simplicity

### 🔄 **AI Integration Strategy**
- **Context-aware conversations**: Include project plan in AI context for relevant responses
- **Token optimization**: Different max_tokens for planning (2000) vs conversation (1500)
- **Robust JSON extraction**: Multiple parsing strategies for reliable plan extraction
- **Graceful degradation**: Falls back to plain text if JSON parsing fails

## What's Missing for Production

1. **User accounts** and project persistence
2. **Database persistence** (currently in-memory, loses data on restart)
   - **Project history sidebar** - Persistent storage for previous chat sessions and project titles
   - **Conversation state** - Maintain chat history across browser sessions
3. **Automated testing** - Unit/integration tests for FastAPI endpoints and Svelte components
4. **Real-time collaboration** features
5. **Integration** with GitHub/project management tools
6. **Advanced AI features** (code generation, architecture suggestions)
7. **Mobile optimization** and PWA capabilities


## Roadmap for V2

1. **Enhanced Prompt Engineering** - Improved prompts especially for detailed mode:
   - Complete directory structure generation with folder hierarchy
   - Exact terminal commands and setup sequences
   - Package.json/requirements.txt content suggestions
   - Git workflow and commit message templates
   - Environment variables and configuration file examples
2. **Redis caching layer** - Cache AI responses and user sessions for better performance
3. **Multiple conversations** - Support concurrent projects with persistent conversation history
4. **Real-time AI streaming** - Stream AI responses progressively via Server-Sent Events for better UX
5. **Code generation integration** - Connect with code scaffolding services (GitHub Codespaces, Replit, etc.)
6. **Conversation summarization** - Auto-summarize long conversations every N messages to maintain full context while optimizing token usage
7. **Advanced context management** - Smart context pruning and expansion based on conversation relevance


---

*Built for developers who want to stop over-planning and start shipping.*
