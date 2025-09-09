# Personal Knowledge Base

A RAG-powered document Q&A system built with FastAPI, LangChain, and ChromaDB. Upload documents and ask questions about their content.

## Features

- Document upload (PDF, Word, Markdown, TXT)
- RAG-based question answering
- Semantic search with vector embeddings
- OCR support for scanned PDFs
- Web interface and REST API
- ChromaDB for vector storage

## Tech Stack

- **Backend**: FastAPI
- **AI**: LangChain + Groq (Llama 3.1-8b-instant)
- **Vector DB**: ChromaDB
- **Embeddings**: HuggingFace sentence-transformers
- **File Processing**: PyPDF2, python-docx, markdown
- **OCR**: Tesseract + pdf2image

## Quick Start

### Prerequisites

- Python 3.8+
- Groq API key (free at https://console.groq.com/)

### Installation

```bash
git clone https://github.com/yourusername/docu-ai.git
cd docu-ai
pip install -r requirements.txt
```

### Configuration

```bash
export GROQ_API_KEY=your_groq_api_key_here
```

### Run

```bash
python -m app.main
```

Open http://localhost:8000

## API Endpoints

- `POST /documents/upload` - Upload document
- `POST /chat/ask` - Ask question
- `GET /documents/search` - Semantic search
- `GET /documents/stats` - Get stats
- `GET /docs` - API documentation

## Project Structure

```
app/
├── main.py              # FastAPI app
├── api/
│   ├── documents.py     # Document endpoints
│   └── chat.py          # Chat endpoints
├── models/
│   └── schemas.py       # Pydantic models
└── services/
    ├── rag_service_groq.py  # RAG service
    └── file_service.py      # File processing
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GROQ_API_KEY` | Groq API key (required) | - |
| `TESSERACT_CMD` | Tesseract path | `/opt/homebrew/bin/tesseract` |
| `POPPLER_PATH` | Poppler path | `/opt/homebrew/bin` |

## OCR Setup (Optional)

For scanned PDF support:

**macOS:**
```bash
brew install tesseract poppler
```

**Ubuntu:**
```bash
sudo apt install tesseract-ocr poppler-utils
```

## Development

```bash
uvicorn app.main:app --reload
```

## Production

```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## How It Works

1. Upload document → Extract text
2. Split text into chunks
3. Generate embeddings with sentence-transformers
4. Store in ChromaDB
5. Query → Retrieve relevant chunks → Generate answer with Groq

## License

MIT