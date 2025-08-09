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

### 1. Update config.yaml

The `config.yaml` file contains all the configuration settings for your application:

```yaml
# config.yaml - Complete configuration for Vertex AI LLM with RAG support

vertex_ai:
  project: "genai-sandbox-test"     # Your Google Cloud Project ID
  location: "us-central1"           # Vertex AI region (us-central1, europe-west1, asia-southeast1, etc.)
  model_name: "gemini-2.5-flash"    # Gemini model name (gemini-2.5-flash, gemini-1.5-pro, etc.)
  temperature: 0.7                  # Controls randomness (0.0-1.0): 0=deterministic, 1=creative
  max_output_tokens: 10000          # Maximum tokens to generate (up to model limit)
  top_p: 0.95                       # Nucleus sampling (0.0-1.0): probability mass to sample from
  top_k: 40                         # Top-k sampling: number of highest probability tokens to consider

# Authentication token for your application (optional)
auth_token: "simpletoken"

# RAG (Retrieval-Augmented Generation) Configuration
rag:
  corpus_id: "6917529027641081856"    # Your RAG corpus ID from Vertex AI
  enabled: true                       # Enable/disable RAG functionality
  similarity_top_k: 3                 # Number of similar documents to retrieve (1-10)
  vector_distance_threshold: 0.7      # Similarity threshold for retrieval (0.0-1.0)

# Application settings
app:
  debug_mode: false                 # Enable debug logging and verbose output
  max_history_messages: 10          # Maximum chat history messages to maintain
  response_timeout: 30              # Response timeout in seconds

# Logging configuration
logging:
  level: "INFO"                     # Log level: DEBUG, INFO, WARNING, ERROR
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

#### Configuration Parameter Details:

**Vertex AI Settings:**
- `project`: Your Google Cloud Project ID where Vertex AI is enabled
- `location`: Region for Vertex AI services (affects latency and data residency)
- `model_name`: The Gemini model to use:
  - `gemini-2.5-flash`: Fast, cost-effective for most tasks
  - `gemini-1.5-pro`: More capable, slower, higher cost
- `temperature`: Response creativity (0.0=deterministic, 1.0=very creative)
- `max_output_tokens`: Maximum response length (affects cost and latency)
- `top_p`: Controls diversity of token selection
- `top_k`: Limits token choices to top K most likely options

**RAG Settings:**
- `corpus_id`: Your Vertex AI RAG corpus identifier (create in Google Cloud Console)
- `enabled`: Toggle RAG functionality on/off
- `similarity_top_k`: How many relevant documents to retrieve
- `vector_distance_threshold`: Minimum similarity score for including documents

**App Settings:**
- `debug_mode`: Enables detailed logging for troubleshooting
- `max_history_messages`: Controls conversation memory length
- `response_timeout`: Prevents hanging requests

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

### Method 3: Docker (Recommended)

The application includes Docker support with Google Cloud authentication using your personal login credentials.

#### Prerequisites for Docker
1. **Install Docker and Docker Compose**
2. **Authenticate with Google Cloud**:
   ```bash
   # Login to Google Cloud
   gcloud auth login
   
   # Set up application default credentials
   gcloud auth application-default login
   
   # Set your project (replace with your actual project ID)
   gcloud config set project your-project-id
   ```

#### Docker Deployment Steps

1. **Update Configuration**:
   Update `config.yaml` with your project details:
   ```yaml
   vertex_ai:
     project: "your-project-id"        # Your Google Cloud Project ID
     location: "us-central1"           # Vertex AI region
     model_name: "gemini-2.5-flash"    # Gemini model name
   
   rag:
     corpus_id: "your-corpus-id"       # Your RAG corpus ID
     enabled: true
   ```

2. **Build and Start Services**:
   ```bash
   # Build and start all services
   docker-compose up --build
   
   # Or run in detached mode
   docker-compose up --build -d
   ```

3. **Access Applications**:
   - **Streamlit Frontend**: http://localhost:8501
   - **FastAPI Backend**: http://localhost:8000
   - **API Documentation**: http://localhost:8000/docs

#### Docker Services Overview

The Docker setup includes two services:

- **Backend (FastAPI)**:
  - Port: 8000
  - Features: RAG chat API, session management, health checks
  - Authentication: Uses mounted Google Cloud credentials from `~/.config/gcloud`

- **Frontend (Streamlit)**:
  - Port: 8501
  - Features: Interactive chat interface, session management, RAG toggle
  - Connects to backend via internal Docker network

#### Managing Docker Services

```bash
# View running containers
docker-compose ps

# View logs
docker-compose logs backend
docker-compose logs frontend

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up --build

# Stop and remove all containers, networks, and volumes
docker-compose down -v
```

#### Docker Files Included

- `Dockerfile.backend`: Backend container with Google Cloud SDK
- `Dockerfile.frontend`: Frontend container with Streamlit
- `docker-compose.yml`: Service orchestration
- `.dockerignore`: Excludes unnecessary files from containers

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