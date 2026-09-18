# Development Notes

## Project Goal

This project implements a minimal end-to-end AI decision assistant for customer-support tickets.

The application demonstrates:

- Python backend development
- REST APIs with FastAPI
- JWT authentication
- Password hashing
- SQLite persistence
- Local RAG
- Gemini-based decision generation
- Structured AI output validation
- Streamlit frontend
- Automated testing
- Evaluation against supplied test cases

The implementation intentionally avoids unnecessary infrastructure and keeps the system small enough to run locally.

---

## Architecture

The application is divided into four main layers:

### Frontend

Streamlit provides the user interface.

Responsibilities:

- Registration
- Login
- Ticket submission
- Decision display
- Decision history
- Logout

The frontend communicates with FastAPI through HTTP and does not access SQLite directly.

### API

FastAPI provides:

- Authentication endpoints
- Current-user endpoint
- Ticket creation
- Ticket listing
- Ticket retrieval
- Request validation
- Authorization

### AI / RAG

The AI pipeline consists of:

1. Loading policy Markdown files.
2. Splitting policy documents into chunks.
3. Generating local sentence-transformer embeddings.
4. Persisting embeddings locally.
5. Embedding incoming ticket text.
6. Retrieving the most relevant policy chunks.
7. Passing retrieved evidence to Gemini.
8. Validating the structured decision.

### Database

SQLite stores:

- Users
- Tickets
- Decisions

A ticket belongs to one user and has one associated decision.

---

## Authentication Design

Passwords are hashed using Argon2 before storage.

Authentication uses signed JWT access tokens.

The token contains the authenticated user's ID and an expiration time.

Protected endpoints require:

```text
Authorization: Bearer <token>