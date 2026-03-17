# LoanPilot
AI-powered loan underwriting using multi-agent orchestration with LangGraph + Next.js

## What is LoanPilot?
LoanPilot is a multi-agent AI system that automates loan underwriting decisions. Instead of a single AI making one call, 4 specialist agents run in parallel — each analyzing a different dimension of the application — then a judge agent synthesizes a plain-English verdict for the loan officer to review.
What used to take days now takes under 10 seconds.

# Tech Stack
## Backend

LangGraph — multi-agent orchestration and state management
FastAPI — REST API with Server-Sent Events (SSE) for live streaming
LangChain OpenAI — LLM calls for the judge agent
Python 3.11+

## Frontend

Next.js 14 (App Router) — React framework
Tailwind CSS — styling
Custom useSSE hook — live agent status streaming

# Roadmap
✅ Phase 1 — Core multi-agent system

 LangGraph multi-agent with parallel fan-out
 4 specialist agents with mock tools
 LLM judge with plain-English verdict
 FastAPI with SSE streaming
 Next.js live dashboard

🔄 Phase 2 — Document intelligence

 PDF ingestion with pypdf
 Doc agent reads pay stubs and bank statements
 Knowledge base with ChromaDB + policy documents
 Compliance agent queries lending guidelines via RAG
 Application history with SQLite persistence

🔮 Phase 3 — Production ready

 Human-in-the-loop override + audit trail
 Real API integrations (Plaid, Experian, Stripe Identity, OFAC)
 Auth + role-based access (Clerk / NextAuth)
 Analytics dashboard (approval rates, agent performance)
 Agent memory with LangGraph checkpointer
 Email / SMS notifications (Resend, Twilio)
