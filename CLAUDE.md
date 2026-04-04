# Gas Man Ottawa - AI Chat Assistant

## Project Overview
AI-powered chat widget for gasmanottawa.com (HVAC contractor in Ottawa). The widget sits on their existing WordPress site as a single JavaScript embed. It includes a customer-facing chatbot and an admin panel for managing the knowledge base and AI instructions.

## Architecture
- **Frontend Widget**: Standalone JS/CSS bundle that injects a chat bubble into any website via `<script>` tag
- **Admin Panel**: Web app for managing knowledge base, AI instructions, and viewing conversation logs
- **Backend API**: Handles chat requests, RAG retrieval, stores conversations, serves the widget
- **AI**: Claude Sonnet via Anthropic API (claude-sonnet-4-20250514)
- **Knowledge Base**: Pinecone vector database for RAG — knowledge base entries are chunked, embedded, and stored. On each chat request, the user message is embedded and similarity-searched against Pinecone to retrieve the most relevant chunks.
- **Database**: SQLite (or Postgres for production) for AI instructions, conversation logs, leads, admin settings
- **Embeddings**: OpenAI text-embedding-3-small (or Cohere multilingual-embed) for embedding knowledge base entries and user queries
- **Deployment**: Vercel for production hosting (same as ConsulRo project). Localhost for demo.

## Existing Provider Accounts (reuse from ConsulRo project)
- **Anthropic API key**: Already have one — store in .env as ANTHROPIC_API_KEY
- **Pinecone**: Already have account — create new index "gasman-chatbot" or use a new namespace in existing index
- **Vercel**: Already have account — deploy as new project
- **GitHub**: Create new repo "gasman-chatbot"
- **OpenAI API key** (for embeddings only): If using OpenAI embeddings, store as OPENAI_API_KEY in .env

## RAG Flow
1. Customer sends a message
2. Embed the message using the embedding model
3. Search Pinecone for top 5-8 most relevant knowledge base chunks
4. Load AI instructions from SQLite database (NOT from vector store — instructions are rules/personality, not searchable knowledge)
5. Build prompt: AI instructions (system prompt) + retrieved knowledge chunks + conversation history
6. Send to Claude Sonnet API
7. Store user message and bot response in SQLite conversation log
8. Check if response triggers lead capture
9. Return response to widget

## Key Principles
- The chatbot must sound like a knowledgeable HVAC technician, not a generic AI
- Responses should be warm, professional, and conversational
- Always guide toward booking a free estimate or calling (613) 880-3888
- Emergency situations (gas smell, CO detector, no heat in winter) get immediate safety-first responses
- Support English and French seamlessly
- Never promise exact prices, always give ranges and recommend a free estimate
- The widget must be lightweight and not interfere with the existing WordPress site or Jobber integration

## Multi-Tenant Ready
Design with future multi-tenant support in mind:
- Each contractor gets their own Pinecone namespace (e.g., namespace="gasman", namespace="plumber-joe")
- Each contractor gets their own AI instructions in the database
- Each contractor gets their own admin login
- Same codebase serves all tenants — differentiated by config/namespace
- For MVP, hardcode to single tenant (Gas Man)

## Tech Stack
- **Backend**: Python + FastAPI
- **Frontend Widget**: Vanilla JS + CSS (no framework — must be lightweight to embed)
- **Admin Panel**: React or simple HTML/JS
- **AI**: Anthropic Claude API (claude-sonnet-4-20250514)
- **Vector DB**: Pinecone (free tier)
- **Embeddings**: OpenAI text-embedding-3-small
- **Database**: SQLite with SQLAlchemy (upgrade to Postgres on Vercel if needed)
- **Deployment**: Vercel (serverless functions for API, static for widget/admin)

## File Structure
```
gasman-chatbot/
├── CLAUDE.md
├── PROJECT_SPEC.md
├── backend/
│   ├── main.py              # FastAPI app + API routes
│   ├── chat.py              # Chat logic — RAG retrieval + Claude API calls
│   ├── database.py          # SQLite models (instructions, conversations, leads)
│   ├── embeddings.py        # Embedding helper (embed text, upsert to Pinecone, query)
│   ├── knowledge_base.py    # Knowledge base CRUD + Pinecone sync
│   ├── seed_data.py         # Initial Gas Man knowledge base — chunks and upserts to Pinecone
│   └── requirements.txt
├── widget/
│   ├── gasman-chat.js       # Embeddable chat widget
│   └── gasman-chat.css      # Widget styles
├── admin/
│   └── index.html           # Admin panel (single page app)
├── .env.example             # Template for API keys
└── .env                     # Actual API keys (git ignored)
```

## Environment Variables (.env)
```
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
PINECONE_API_KEY=...
PINECONE_INDEX=gasman-chatbot
PINECONE_NAMESPACE=gasman
ADMIN_USERNAME=admin
ADMIN_PASSWORD=gasman2024
```
