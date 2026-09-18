# MaxsorLabs AI Decision Assistant

A minimal end-to-end AI decision system for customer-support ticket triage.

The application combines **FastAPI, JWT authentication, SQLite, local RAG, Gemini, and Streamlit** to turn a customer-support ticket into a structured, evidence-backed policy decision.

---

## Overview

A user can:

1. Register and authenticate with JWT.
2. Submit a customer-support ticket.
3. Retrieve relevant policy evidence using local semantic search.
4. Generate a structured decision using Google Gemini.
5. Store the ticket and decision in SQLite.
6. Review previous decisions through the Streamlit interface.

The system is intentionally small and focused on demonstrating the complete application flow without introducing unnecessary infrastructure.

---

## Architecture

```text
                    ┌──────────────────────┐
                    │      Streamlit       │
                    │      Frontend        │
                    └──────────┬───────────┘
                               │ HTTP
                               ▼
                    ┌──────────────────────┐
                    │       FastAPI        │
                    │    REST API + JWT    │
                    └───────┬───────┬──────┘
                            │       │
                     Auth   │       │ Decision
                            │       ▼
                            │  ┌───────────────┐
                            │  │ Local RAG     │
                            │  │ Embeddings +  │
                            │  │ Policy Search │
                            │  └───────┬───────┘
                            │          │
                            │          ▼
                            │  ┌───────────────┐
                            │  │    Gemini     │
                            │  │ Structured AI │
                            │  │   Decision    │
                            │  └───────┬───────┘
                            │          │
                            ▼          ▼
                    ┌──────────────────────┐
                    │       SQLite         │
                    │ Users / Tickets /    │
                    │      Decisions       │
                    └──────────────────────┘