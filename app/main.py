""""""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os

from .api import documents, chat
from .models.schemas import HealthResponse

app = FastAPI(
    title="📚 Personal Knowledge Base",
    description="RAG-powered document QA with multiple file formats",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router)
app.include_router(chat.router)

if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def read_root():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>📚 Personal Knowledge Base</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .header {
                text-align: center;
                margin-bottom: 40px;
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .container {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                margin-bottom: 40px;
            }
            .card {
                background: white;
                padding: 25px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .upload-area {
                border: 2px dashed #ddd;
                border-radius: 10px;
                padding: 40px;
                text-align: center;
                margin-bottom: 20px;
                cursor: pointer;
                transition: all 0.3s;
            }
            .upload-area:hover {
                border-color: #007bff;
                background-color: #f8f9fa;
            }
            .chat-area {
                height: 400px;
                border: 1px solid #ddd;
                border-radius: 10px;
                padding: 15px;
                overflow-y: auto;
                background-color: #fafafa;
                margin-bottom: 15px;
            }
            .input-group {
                display: flex;
                gap: 10px;
            }
            input[type="text"], input[type="file"] {
                flex: 1;
                padding: 12px;
                border: 1px solid #ddd;
                border-radius: 5px;
                font-size: 14px;
            }
            button {
                padding: 12px 20px;
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 14px;
                transition: background-color 0.3s;
            }
            button:hover {
                background-color: #0056b3;
            }
            .message {
                margin-bottom: 15px;
                padding: 10px;
                border-radius: 5px;
            }
            .user-message {
                background-color: #e3f2fd;
                text-align: right;
            }
            .bot-message {
                background-color: #f1f8e9;
            }
            .features {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-top: 40px;
            }
            .feature {
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                text-align: center;
            }
            .feature-icon {
                font-size: 2em;
                margin-bottom: 10px;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📚 Personal Knowledge Base</h1>
            <p>RAG-powered document question answering</p>
            <p>Supports PDF, Word, Markdown, and TXT</p>
        </div>

        <div class="container">
            <div class="card">
                <h3>📄 Upload Document</h3>
                <div class="upload-area" onclick="document.getElementById('fileInput').click()">
                    <p>Click to choose or drag a file here</p>
                    <p>Supported: PDF, Word, Markdown, TXT</p>
                </div>
                <input type="file" id="fileInput" style="display: none;" accept=".pdf,.docx,.doc,.md,.txt" onchange="uploadFile()">
                <div id="uploadStatus"></div>
            </div>

            <div class="card">
                <h3>💬 Chat</h3>
                <div id="chatArea" class="chat-area">
                    <div class="message bot-message">
                        <strong>Assistant:</strong> Hi! Please upload some documents, then ask your question.
                    </div>
                </div>
                <div class="input-group">
                    <input type="text" id="questionInput" placeholder="Type your question..." onkeypress="handleKeyPress(event)">
                    <button onclick="askQuestion()">Ask</button>
                </div>
            </div>
        </div>

        <div class="features">
            <div class="feature">
                <div class="feature-icon">🤖</div>
                <h4>QA</h4>
                <p>RAG to understand docs and answer questions</p>
            </div>
            <div class="feature">
                <div class="feature-icon">📚</div>
                <h4>Formats</h4>
                <p>PDF, Word, Markdown, TXT</p>
            </div>
            <div class="feature">
                <div class="feature-icon">🔍</div>
                <h4>Semantic Search</h4>
                <p>Vector DB to retrieve relevant content</p>
            </div>
            <div class="feature">
                <div class="feature-icon">💡</div>
                <h4>Suggestions</h4>
                <p>Prompt ideas based on content</p>
            </div>
        </div>

        <script>
            async function uploadFile() {
                const fileInput = document.getElementById('fileInput');
                const file = fileInput.files[0];
                const statusDiv = document.getElementById('uploadStatus');
                
                if (!file) return;
                
                statusDiv.innerHTML = '<p>Uploading...</p>';
                
                const formData = new FormData();
                formData.append('file', file);
                
                try {
                    const response = await fetch('/documents/upload', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const result = await response.json();
                    
                    if (result.success) {
                        statusDiv.innerHTML = `<p style="color: green;">✅ Uploaded successfully</p>`;
                        window.__lastDocumentId = result.document_id;
                        addMessage('bot', `Document "${result.filename}" has been added. (id: ${result.document_id})`);
                    } else {
                        statusDiv.innerHTML = `<p style="color: red;">❌ Upload failed: ${result.message}</p>`;
                    }
                } catch (error) {
                    statusDiv.innerHTML = `<p style="color: red;">❌ Upload failed: ${error.message}</p>`;
                }
            }
            
            async function askQuestion() {
                const input = document.getElementById('questionInput');
                const question = input.value.trim();
                
                if (!question) return;
                
                addMessage('user', question);
                input.value = '';
                
                try {
                    const response = await fetch('/chat/ask', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ question: question, document_id: window.__lastDocumentId || null })
                    });
                    
                    const result = await response.json();
                    
                    if (result.success) {
                        addMessage('bot', result.answer);
                    } else {
                        addMessage('bot', `Sorry, an error occurred: ${result.error || 'Unknown error'}`);
                    }
                } catch (error) {
                    addMessage('bot', `Sorry, an error occurred: ${error.message}`);
                }
            }
            
            function addMessage(type, content) {
                const chatArea = document.getElementById('chatArea');
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${type}-message`;
                
                const sender = type === 'user' ? 'You' : 'Assistant';
                messageDiv.innerHTML = `<strong>${sender}:</strong> ${content}`;
                
                chatArea.appendChild(messageDiv);
                chatArea.scrollTop = chatArea.scrollHeight;
            }
            
            function handleKeyPress(event) {
                if (event.key === 'Enter') {
                    askQuestion();
                }
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    try:
        rag_stats = documents.rag_service.get_document_stats()
        
        return HealthResponse(
            status="healthy",
            timestamp=datetime.now().isoformat(),
            version="1.0.0",
            rag_service_status="running" if rag_stats["total_documents"] >= 0 else "error",
            vector_db_status="connected",
            openai_status="not_configured"
        )
    except Exception as e:
        return HealthResponse(
            status="unhealthy",
            timestamp=datetime.now().isoformat(),
            version="1.0.0",
            rag_service_status="error",
            vector_db_status="error",
            openai_status="error"
        )


@app.get("/api")
async def api_info():
    return {
        "name": "Personal Knowledge Base",
        "version": "1.0.0",
        "description": "RAG-powered document QA",
        "endpoints": {
            "documents": {
                "POST /documents/upload": "Upload document",
                "GET /documents/list": "List documents",
                "GET /documents/stats": "Get stats",
                "DELETE /documents/clear": "Clear all documents"
            },
            "chat": {
                "POST /chat/ask": "Ask question",
                "GET /chat/history": "Get chat history",
                "POST /chat/search": "Semantic search",
                "POST /chat/feedback": "Submit feedback"
            }
        },
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
