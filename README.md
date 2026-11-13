# DocAnswer — Document-Grounded AI Assistant

A full-stack Retrieval-Augmented Generation (RAG) application that answers questions from an indexed company HR policy document and provides source-linked citations.

DocAnswer combines semantic retrieval, BM25 keyword search, hybrid ranking, and answer-generation safeguards to help users locate relevant policy information.

> **Important:** DocAnswer is a demonstration project, not a substitute for legal, HR, or professional advice. Always verify important decisions against the original document.

## Features

- Natural-language questions over an indexed HR policy.
- Hybrid retrieval using ChromaDB and BM25.
- Reciprocal Rank Fusion (RRF) for combining retrieval results.
- Source citations containing document, page, and section information.
- Structured API responses with confidence and retrieval status.
- Refusal behavior when available document evidence is insufficient.
- Deterministic embedding fallback for supported offline workflows.
- Next.js chat interface with document status information.
- Automated Python tests and a 30-question evaluation benchmark.

## Architecture

```text
                 SOURCE DOCUMENT
                       |
                       v
                scripts/ingest.py
                       |
              Text extraction and chunking
                       |
               +-------+-------+
               |               |
               v               v
          ChromaDB           BM25
          Vector Index     Keyword Index
               |               |
               +-------+-------+
                       |
                 Hybrid Retrieval
                       |
               Reciprocal Rank Fusion
                       |
                Answer Generation
                       |
             Citation Reference Checks
                       |
                 FastAPI Response
                       |
                 Next.js Frontend
```

## Technology Stack

| Layer | Technologies |
|---|---|
| Frontend | Next.js 14, React 18, TypeScript |
| Styling | Tailwind CSS |
| Backend | Python, FastAPI |
| Validation | Pydantic |
| Vector database | ChromaDB |
| Keyword retrieval | BM25 |
| Retrieval strategy | Hybrid search and RRF |
| Document processing | PyPDF and text chunking |
| Testing | Pytest |
| Deployment configuration | Vercel |

## Repository Structure

```text
docanswer/
├── api/
│   ├── config.py
│   ├── embeddings.py
│   ├── generator.py
│   ├── index.py
│   ├── models.py
│   ├── retriever.py
│   └── utils.py
├── app/
│   ├── globals.css
│   ├── layout.tsx
│   └── page.tsx
├── data/
│   ├── acme_corp_hr_policy.md
│   └── acme_corp_hr_policy.pdf
├── eval/
│   ├── questions.json
│   └── results.md
├── index/
│   ├── bm25_index.json
│   └── chroma_db/
├── scripts/
│   ├── evaluate.py
│   ├── generate_pdf.py
│   ├── ingest.py
│   └── smoke_test.py
├── tests/
├── .env.example
├── next.config.js
├── requirements.txt
├── vercel.json
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.11 or later
- Node.js 18 or later
- npm

### 1. Clone the repository

```bash
git clone https://github.com/anasrizwan572-create/docanswer-rag.git
cd docanswer-rag
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

On Windows PowerShell, use:

```powershell
Copy-Item .env.example .env
```

Configure the provider credentials required by your selected model and embedding configuration. Never commit `.env` or expose API keys.

### 3. Install backend dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Run the backend

```bash
python -m uvicorn api.index:app --reload --port 8001
```

Backend API:

- Health: `http://127.0.0.1:8001/api/health`
- Document information: `http://127.0.0.1:8001/api/document-info`
- API documentation: `http://127.0.0.1:8001/docs`

### 5. Install frontend dependencies

```bash
npm install
```

### 6. Run the frontend

```bash
npm run dev
```

Open `http://localhost:3000`.

The Next.js development rewrite forwards `/api/*` requests to the local FastAPI service on port `8001`.

## API Overview

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/health` | GET | Backend and index health |
| `/api/document-info` | GET | Indexed document information |
| `/api/query` | POST | Ask a question about the indexed document |

See the automatically generated FastAPI documentation at `/docs` when the backend is running.

## Testing

Run the complete test suite:

```bash
python -m pytest tests/ -q
```

Run the evaluation benchmark:

```bash
python scripts/evaluate.py
```

The latest recorded test run completed with **23 passed**.

### Evaluation Results

The recorded 30-question benchmark contains:

- 20 single-section questions
- 5 multi-section questions
- 5 deliberately unanswerable questions

| Metric | Recorded result |
|---|---:|
| Faithfulness | 1.0000 |
| Answer relevancy | 0.8419 |
| Context precision | 0.7363 |
| Context recall | 0.9503 |
| Refusal accuracy | 100% (5/5) |

**Evaluation note:** Context precision is below its stated target of 0.80. The benchmark report also identifies 75 source chunks, while the currently verified indexed database contains 98 chunks. These figures should be reconciled before presenting the benchmark as a final release result.

## Indexing

The repository includes a prebuilt ChromaDB and BM25 index.

To rebuild the index from source documents:

```bash
python scripts/ingest.py
```

**Warning:** Rebuilding ingestion deletes and recreates the existing ChromaDB index. Back up the current index before running this command.

## Limitations

- The current application is centered on the included HR policy document.
- Users cannot assume that arbitrary documents are available without ingestion.
- Citation-reference validation does not independently prove that every generated factual statement is entailed by its cited passage.
- Retrieval quality can vary with question wording and document structure.
- Important policy decisions require checking the original source.

## Roadmap

- [ ] Multi-document ingestion and collections
- [ ] Secure document upload
- [ ] Authentication and role-based access control
- [ ] Persistent query and audit history
- [ ] Improved table-aware document extraction
- [ ] Stronger claim-to-source verification
- [ ] Expanded retrieval and evaluation benchmarks
- [ ] Continuous integration and deployment checks

## Security

- Keep API credentials in environment variables.
- Do not commit `.env` files, credentials, or private documents.
- Review document access and deployment permissions before using sensitive company material.

## License

No license has been specified yet. All rights reserved unless a license is added to this repository.

