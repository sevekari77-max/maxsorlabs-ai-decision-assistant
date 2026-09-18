# MaxsorLabs AI Decision Assistant

A minimal end-to-end AI decision system for customer-support ticket triage.

The application combines **FastAPI, JWT authentication, SQLite, local RAG, Gemini, and Streamlit** to turn a customer-support ticket into a structured, evidence-backed policy decision.

## Demo Login

For quick testing, use the following demo account:

**Email:** `demo@maxsorlabs.com`  
**Password:** `MaxsorLabsDemo123!`

You can also create a new account using the Register option.

---

## Overview

The application allows a user to:

1. Register and log in.
2. Submit a customer-support ticket.
3. Retrieve relevant policy information using local RAG.
4. Generate an AI-based decision using Gemini.
5. Store the ticket and decision in SQLite.
6. View previous decisions in the Streamlit frontend.

The project is intentionally small and focused on demonstrating the complete backend, authentication, RAG, AI, database, and frontend workflow.

---

## Architecture

```text
Streamlit Frontend
        |
        | HTTP
        v
FastAPI Backend
        |
        +---- JWT Authentication
        |
        +---- SQLite Database
        |
        +---- Local RAG
        |       |
        |       v
        |   Policy Documents
        |
        v
     Gemini AI
        |
        v
Structured Decision
```

---

## Key Features

- User registration and login
- JWT-based authentication
- Argon2 password hashing
- User-specific ticket access
- Customer-support ticket submission
- SQLite database
- Local semantic RAG
- Sentence Transformer embeddings
- Gemini-powered decision generation
- Structured AI responses
- Confidence scores and policy sources
- Streamlit frontend
- Automated API tests
- Evaluation script for supplied test cases

---

## Technology Stack

| Component | Technology |
|---|---|
| Backend | FastAPI |
| Frontend | Streamlit |
| Database | SQLite + SQLAlchemy |
| Authentication | JWT |
| Password Hashing | Argon2 |
| RAG | Sentence Transformers |
| Embedding Model | all-MiniLM-L6-v2 |
| LLM | Google Gemini |
| Validation | Pydantic |
| Testing | Pytest |

---

## Project Structure

```text
maxsorlabs-ai-decision-assistant/
│
├── candidate_pack/
│   ├── data/
│   │   └── tickets.csv
│   ├── knowledge_base/
│   │   ├── cancellations.md
│   │   ├── damaged_goods.md
│   │   ├── defective_products.md
│   │   ├── returns.md
│   │   ├── shipping.md
│   │   └── wrong_item.md
│   ├── DATA_NOTES.md
│   └── sample_test_cases.json
│
├── frontend/
│   └── app.py
│
├── scripts/
│   ├── evaluate.py
│   └── ingest.py
│
├── src/
│   ├── ai/
│   │   └── gemini_service.py
│   ├── rag/
│   │   ├── embedder.py
│   │   ├── loader.py
│   │   └── retriever.py
│   ├── auth.py
│   ├── config.py
│   ├── database.py
│   ├── dependencies.py
│   ├── main.py
│   ├── models.py
│   └── schemas.py
│
├── tests/
│   └── test_api.py
│
├── .env.example
├── .gitignore
├── DEVELOPMENT.md
├── README.md
└── requirements.txt
```

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/sevekari77-max/maxsorlabs-ai-decision-assistant.git
cd maxsorlabs-ai-decision-assistant
```

### 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
JWT_SECRET=your_long_random_secret
DATABASE_URL=sqlite:///./data/app.db
```

Never commit the real `.env` file.

---

## Generate Policy Embeddings

Run:

```bash
python scripts/ingest.py
```

This loads the policy documents, creates text chunks, generates embeddings using `all-MiniLM-L6-v2`, and stores the local embedding index.

Expected output:

```text
Saved 6 chunks.
Embeddings shape: (6, 384)
```

---

## Run the Backend

Start FastAPI:

```bash
python -m uvicorn src.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

Swagger API documentation:

```text
http://127.0.0.1:8000/docs
```

---

## Run the Frontend

Open a second terminal.

Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Run Streamlit:

```bash
streamlit run frontend/app.py
```

Frontend:

```text
http://localhost:8501
```

The Streamlit frontend communicates with FastAPI through HTTP and does not access the database directly.

---

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/register` | Register a user |
| POST | `/login` | Authenticate and receive JWT |
| GET | `/me` | Get current user |
| POST | `/tickets` | Create ticket and generate decision |
| GET | `/tickets` | Get current user's tickets |
| GET | `/tickets/{id}` | Get a specific ticket |
| GET | `/health` | Health check |

Protected endpoints use:

```text
Authorization: Bearer <JWT>
```

---

## RAG Pipeline

The RAG pipeline is intentionally lightweight:

```text
Policy Documents
       |
       v
Document Loader
       |
       v
Text Chunking
       |
       v
Sentence Transformer
       |
       v
Local Embeddings
       |
       v
Incoming Ticket
       |
       v
Semantic Search
       |
       v
Relevant Policy Evidence
       |
       v
Gemini
       |
       v
Structured Decision
```

No external vector database is required.

---

## AI Decision Format

Gemini returns a structured JSON response:

```json
{
  "action": "REQUEST_PHOTOS",
  "confidence": 0.95,
  "reason": "The item value exceeds the policy threshold and photographic evidence is required.",
  "sources": [
    "damaged_goods.md"
  ]
}
```

The response is validated before being stored in the database.

If there is not enough information to determine the correct action, the system returns:

```text
NEEDS_MORE_INFORMATION
```

---

## Evaluation

Run the supplied evaluation cases with:

```bash
python scripts/evaluate.py
```

Current result:

```text
S01 PASS
S02 PASS
S03 PASS
S04 PASS
S05 PASS

Evaluation complete: 5/5 passed
ALL TEST CASES PASSED
```

---

## Automated Tests

Run:

```bash
pytest -q
```

Current result:

```text
6 passed
```

The tests cover:

- Authentication requirements
- Invalid JWT tokens
- Protected endpoints
- Health check
- Request validation

---

## Security

The application includes:

- Argon2 password hashing
- JWT authentication
- JWT expiration
- Protected API endpoints
- User-specific ticket authorization
- Pydantic request validation
- Environment-based secrets
- `.env` excluded from Git
- Database files excluded from Git
- Generated embedding files excluded from Git

---

## Error Handling

The API handles:

- Duplicate registration
- Invalid login credentials
- Missing authentication
- Invalid or expired JWTs
- Unauthorized ticket access
- Invalid request data
- Gemini/API failures

AI decision failures do not result in incomplete decisions being stored.

---

## Engineering Decisions

The project avoids unnecessary infrastructure and keeps the implementation easy to run locally.

The RAG system uses:

- Markdown policy documents
- Local text chunking
- Sentence Transformer embeddings
- NumPy similarity search

This provides a simple local RAG implementation without requiring a hosted vector database.

---

## Known Limitations

- Embeddings are generated locally and are not committed to Git.
- Gemini requires a valid API key and internet access.
- SQLite is used for simplicity.
- The embedding index must be regenerated when the policy documents change.
- The project is designed as a small take-home assignment rather than a production deployment.

---

## Development Notes

Additional architecture decisions, testing notes, trade-offs, and development information are available in:

```text
DEVELOPMENT.md
```

---

## Project Status

The project includes:

- FastAPI backend
- JWT authentication
- SQLite persistence
- Local RAG pipeline
- Gemini integration
- Streamlit frontend
- Evaluation script
- Automated tests
- Development documentation
- Supplied candidate data and policy documents