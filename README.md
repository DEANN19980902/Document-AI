# 📚 Personal Knowledge Base

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A powerful AI-powered document Q&A system that lets you upload documents and ask questions about their content. Built with RAG (Retrieval Augmented Generation) technology for accurate, context-aware answers.

## ✨ Features

- 🤖 **AI-Powered Q&A**: Ask questions about your documents using advanced RAG technology
- 📄 **Multiple Formats**: Support for PDF, Word, Markdown, and text files
- 🔍 **Semantic Search**: Find relevant information using vector similarity search
- 🌐 **Web Interface**: Clean, intuitive browser-based interface
- 📊 **Document Analytics**: Track usage statistics and chat history
- 🔧 **OCR Support**: Process scanned PDFs with optical character recognition
- 🚀 **Easy Setup**: Get started in minutes with free Groq API

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Free Groq API key ([Get one here](https://console.groq.com/))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/personal-knowledge-base.git
   cd personal-knowledge-base
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   # Option 1: Export directly
   export GROQ_API_KEY=your_groq_api_key_here
   
   # Option 2: Create .env file
   echo "GROQ_API_KEY=your_groq_api_key_here" > .env
   ```

4. **Run the application**
   ```bash
   python -m app.main
   ```

5. **Open your browser**
   Navigate to [http://localhost:8000](http://localhost:8000)

## 🎯 Usage

1. **Upload Documents**: Click "Upload Document" and select your file
2. **Ask Questions**: Type your question in the chat interface
3. **Get Answers**: Receive intelligent responses based on your document content

### Example Questions

- "What is the main topic of this document?"
- "Summarize the key points"
- "What data or statistics are mentioned?"
- "What methods or techniques are described?"

## 📋 Supported File Types

| Format | Extension | Features |
|--------|-----------|----------|
| PDF | `.pdf` | Text extraction + OCR for scanned documents |
| Word | `.docx`, `.doc` | Full document parsing |
| Markdown | `.md` | Markdown to text conversion |
| Text | `.txt` | Direct text processing |

## 🔧 Advanced Setup

### OCR Support (Optional)

For scanned PDF processing, install system dependencies:

**macOS:**
```bash
brew install tesseract poppler
```

**Ubuntu/Debian:**
```bash
sudo apt update && sudo apt install -y tesseract-ocr poppler-utils
```

**Windows:**
Download and install [Tesseract](https://github.com/UB-Mannheim/tesseract/wiki) and [Poppler](https://blog.alivate.com.au/poppler-windows/)

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GROQ_API_KEY` | Groq API key (required) | - |
| `TESSERACT_CMD` | Path to tesseract executable | `/opt/homebrew/bin/tesseract` |
| `POPPLER_PATH` | Path to poppler utilities | `/opt/homebrew/bin` |

## 🛠️ API Documentation

Once running, access the interactive API documentation:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

### Key Endpoints

- `POST /documents/upload` - Upload documents
- `POST /chat/ask` - Ask questions about documents
- `GET /documents/search` - Semantic search across documents
- `GET /documents/stats` - Get document statistics

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Interface │    │   FastAPI       │    │   RAG Pipeline  │
│   (HTML/CSS/JS) │◄──►│   Backend       │◄──►│   LangChain     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   File Service  │    │   Vector DB     │
                       │   (PDF/Word/OCR)│    │   (ChromaDB)    │
                       └─────────────────┘    └─────────────────┘
```

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python web framework)
- **AI Engine**: LangChain with Groq's Llama 3.1-8b-instant
- **Vector Database**: ChromaDB for semantic search
- **Embeddings**: HuggingFace sentence-transformers
- **File Processing**: PyPDF2, python-docx, markdown
- **OCR**: Tesseract via pytesseract and pdf2image
- **Frontend**: Vanilla HTML/CSS/JavaScript

## 🚀 Deployment

### Development
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production with Gunicorn
```bash
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t knowledge-base .
docker run -p 8000:8000 -e GROQ_API_KEY=your_key knowledge-base
```

## 📊 Groq API Limits

**Free Tier:**
- 14,400 requests per day
- 30 requests per minute
- No credit card required
- Completely free forever

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [LangChain](https://github.com/langchain-ai/langchain) for the RAG framework
- [Groq](https://groq.com/) for providing free LLM API access
- [ChromaDB](https://github.com/chroma-core/chroma) for vector storage
- [FastAPI](https://fastapi.tiangolo.com/) for the web framework

## 📞 Support

If you encounter any issues or have questions:

1. Check the [API documentation](http://localhost:8000/docs)
2. Review the [health check](http://localhost:8000/health)
3. Open an [issue](https://github.com/yourusername/personal-knowledge-base/issues)

---

**⭐ Star this repository if you find it helpful!**