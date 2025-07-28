# 🤖 RAG Chat System

A complete Retrieval-Augmented Generation (RAG) chat system built with FastAPI backend and Streamlit frontend, powered by Google Vertex AI.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Usage Examples](#usage-examples)
- [Project Structure](#project-structure)

## 🌟 Overview

This RAG Chat System combines the power of Google Vertex AI's generative models with retrieval-augmented generation capabilities. Users can choose between RAG-enhanced responses (using a knowledge base) or standard conversational AI responses.

### Key Components:
- **FastAPI Backend**: RESTful API with streaming support
- **Streamlit Frontend**: Interactive web interface
- **Vertex AI Integration**: Google Cloud's generative AI models
- **RAG Engine**: Knowledge base retrieval and context injection
- **Session Management**: Conversation history and summarization

## ✨ Features

### 🎯 Core Features
- **Dual Chat Modes**: Toggle between RAG-enhanced and regular chat
- **Real-time Streaming**: Server-sent events for live responses
- **Session Management**: Persistent conversation history
- **Auto-summarization**: Intelligent conversation summarization
- **Context Retrieval**: Knowledge base integration via Vertex AI RAG
- **Health Monitoring**: API status and service health checks

### 🛠️ Technical Features
- **Async Processing**: Non-blocking request handling
- **Error Handling**: Comprehensive error management
- **Configuration Management**: YAML-based configuration
- **Cloud Ready**: Designed for Google Cloud Run deployment
- **API Documentation**: Auto-generated OpenAPI/Swagger docs

## 🏗️ Architecture

```
┌─────────────────┐    HTTP/WebSocket    ┌─────────────────┐
│   Streamlit     │ ◄──────────────────► │   FastAPI       │
│   Frontend      │                      │   Backend       │
└─────────────────┘                      └─────────────────┘
                                                   │
                                                   ▼
                                         ┌─────────────────┐
                                         │  Vertex AI      │
                                         │  - Gemini Model │
                                         │  - RAG Engine   │
                                         │  - Knowledge DB │
                                         └─────────────────┘
```

## 📋 Prerequisites

### System Requirements
- Python 3.8 or higher
- Google Cloud Account with Vertex AI enabled
- Google Cloud CLI (`gcloud`) installed and configured

### Google Cloud Setup
1. **Enable APIs**:
   ```bash
   gcloud services enable aiplatform.googleapis.com
   gcloud services enable vertexai.googleapis.com
   ```

2. **Authentication**:
   ```bash
   gcloud auth application-default login
   ```

3. **Set Project**:
   ```bash
   gcloud config set project YOUR_PROJECT_ID
   ```

### Required Permissions
- `aiplatform.endpoints.predict`
- `aiplatform.models.predict`
- Vertex AI User role

## 🚀 Installation

### 1. Clone Repository
```bash
git clone <repository-url>
cd rag-chat-system
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Create requirements.txt
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
google-cloud-aiplatform==1.38.0
pyyaml==6.0.1
streamlit==1.28.0
requests==2.31.0
```

## ⚙️ Configuration

### 1. Create config.yaml
```yaml
# config.yaml
vertex_ai:
  project: "your-gcp-project-id"
  location: "us-central1"  # or your preferred region
  model_name: "gemini-1.5-pro-001"
  temperature: 0.7
  max_output_tokens: 8192
  top_p: 0.95
  top_k: 40

rag:
  enabled: true
  corpus_id: "your-rag-corpus-id"  # Optional: leave empty to disable RAG
  similarity_top_k: 5
  vector_distance_threshold: 0.3

chat_history:
  max_length: 5
  summarize_threshold: 10
  max_context_length: 4000
```

### 2. Environment Variables (Optional)
```bash
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account.json"
```

## 🏃‍♂️ Running the Application

### Method 1: Development Mode

1. **Start FastAPI Backend**:
   ```bash
   cd backend
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Start Streamlit Frontend** (in new terminal):
   ```bash
   cd frontend
   streamlit run streamlit_app.py --server.port 8501
   ```

3. **Access Applications**:
   - Streamlit UI: http://localhost:8501
   - FastAPI Docs: http://localhost:8000/docs
   - FastAPI Health: http://localhost:8000/health

### Method 2: Production Mode

1. **Start FastAPI**:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
   ```

2. **Start Streamlit**:
   ```bash
   streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0
   ```

### Method 3: Docker (Optional)

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t rag-chat .
docker run -p 8000:8000 rag-chat
```

## 📚 API Documentation

### Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| POST | `/chat` | Send message (non-streaming) |
| POST | `/chat/stream` | Send message (streaming) |
| GET | `/sessions` | List all sessions |
| GET | `/sessions/{id}` | Get session details |
| DELETE | `/sessions/{id}` | Delete session |
| POST | `/sessions/{id}/summarize` | Force summarization |
| GET | `/health` | Detailed health status |

### Request/Response Examples

**Chat Request**:
```json
{
  "message": "What is machine learning?",
  "session_id": "optional-session-id",
  "use_rag": true
}
```

**Chat Response**:
```json
{
  "response": "Machine learning is a subset of artificial intelligence...",
  "session_id": "uuid-string",
  "message_count": 1,
  "used_rag": true,
  "context_used": "Retrieved context from knowledge base..."
}
```

## 💡 Usage Examples

### Using the Streamlit Interface

1. **Open the Streamlit app** at http://localhost:8501
2. **Toggle RAG mode** in the sidebar
3. **Type your message** in the chat input
4. **View responses** with metadata and context information
5. **Manage sessions** using sidebar controls

### Using cURL

```bash
# Basic chat with RAG
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Explain quantum computing",
    "use_rag": true
  }'

# Streaming chat
curl -X POST "http://localhost:8000/chat/stream" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Tell me about AI trends",
    "use_rag": true
  }' --no-buffer
```

### Using Python Requests

```python
import requests

# Send a chat message
response = requests.post(
    "http://localhost:8000/chat",
    json={
        "message": "What is the future of AI?",
        "use_rag": True
    }
)

print(response.json())
```

## 📁 Project Structure

```
rag-chat-system/
├── README.md
├── requirements.txt
├── config.yaml
├── main.py                 # FastAPI application
├── app.py        # Streamlit frontend
├── utils/
  ├── __init__.py
  ├── vertex_service.py   # Vertex AI integration
  └── prompts.py          # Prompt templates
```

## 🛠️ Script Explanations

### main.py
- **Purpose**: FastAPI application entry point
- **Key Functions**:
  - Route definitions for chat endpoints
  - Session management logic
  - Streaming response handling
  - Health check implementations

### utils/vertex_service.py
- **Purpose**: Vertex AI integration and RAG functionality
- **Key Classes**:
  - `VertexRAGService`: Main service class
- **Key Methods**:
  - `chat_with_history()`: Non-streaming chat
  - `chat_with_history_stream()`: Streaming chat
  - `_retrieve_rag_context()`: Knowledge base retrieval
  - `summarize_conversation()`: Auto-summarization

### utils/prompts.py
- **Purpose**: Centralized prompt management
- **Key Methods**:
  - `get_rag_chat_prompt()`: RAG-enhanced prompts
  - `get_chat_prompt()`: Regular chat prompts
  - `get_summarization_prompt()`: Summarization prompts

### streamlit_app.py
- **Purpose**: Web-based chat interface
- **Key Features**:
  - Interactive chat UI
  - RAG mode toggle
  - Session management
  - Real-time API status monitoring

## 🐛 Troubleshooting

### Common Issues

1. **Authentication Error**:
   ```bash
   gcloud auth application-default login
   gcloud config set project YOUR_PROJECT_ID
   ```

2. **RAG Corpus Not Found**:
   - Verify corpus ID in config.yaml
   - Ensure RAG corpus exists in your project
   - Check region consistency

3. **Model Access Denied**:
   - Verify Vertex AI API is enabled
   - Check IAM permissions
   - Ensure model is available in your region

4. **Connection Refused**:
   - Check if FastAPI is running on correct port
   - Verify firewall settings
   - Update API_BASE_URL in Streamlit app

### Debug Commands

```bash
# Check API health
curl http://localhost:8000/health

# Test authentication
gcloud auth list

# Check project settings
gcloud config list

# View FastAPI logs
uvicorn main:app --log-level debug

# Test Vertex AI access
python -c "import vertexai; vertexai.init(project='YOUR_PROJECT')"
```

### Log Analysis

**FastAPI Logs**: Look for initialization messages
```
✅ RAG service initialized successfully
✅ Vertex AI initialized: project-id in us-central1
✅ Model initialized: gemini-1.5-pro-001
```

**Error Patterns**:
- `❌ Failed to initialize RAG service`: Check credentials
- `⚠️ RAG retrieval error`: Verify corpus configuration
- `Connection error`: Check network and firewall

## 🌐 Deployment

### Google Cloud Run

1. **Build and Deploy**:
   ```bash
   gcloud run deploy rag-chat-api \
     --source . \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

2. **Update Streamlit Config**:
   ```python
   API_BASE_URL = "https://rag-chat-api-xxx.run.app"
   ```

### Environment Variables for Production

```bash
export PORT=8000
export GOOGLE_CLOUD_PROJECT="your-project-id"
export RAG_CORPUS_ID="your-corpus-id"
```

## 📊 Monitoring

### Health Checks
- **Basic**: `GET /`
- **Detailed**: `GET /health`
- **Sessions**: `GET /sessions`

### Metrics to Monitor
- Response times
- Error rates
- Active sessions
- RAG retrieval success rate
- Token usage


## 🔗 Useful Links

- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Google Cloud Run](https://cloud.google.com/run/docs)

---

**Happy Chatting! 🚀**