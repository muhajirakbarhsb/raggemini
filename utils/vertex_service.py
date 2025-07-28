# utils/vertex_service.py
import vertexai
import vertexai.preview.rag as rag
from vertexai.generative_models import GenerativeModel, GenerationConfig, Content, Part
from typing import List, Optional, Generator, Dict, Any, Tuple
import yaml
import os
from datetime import datetime
from utils.prompts import RAGPrompts


class VertexRAGService:
    def __init__(self, config_path: str = "config.yaml"):
        # Load configuration
        self.config = self._load_config(config_path)

        # Extract Vertex AI configuration
        vertex_config = self.config.get('vertex_ai', {})
        self.project_id = vertex_config.get('project')
        self.location = vertex_config.get('location')
        self.model_name = vertex_config.get('model_name')
        self.temperature = vertex_config.get('temperature', 0.7)
        self.max_output_tokens = vertex_config.get('max_output_tokens', 10000)
        self.top_p = vertex_config.get('top_p', 0.95)
        self.top_k = vertex_config.get('top_k', 40)

        # RAG configuration
        rag_config = self.config.get('rag', {})
        self.rag_corpus_id = rag_config.get('corpus_id')
        self.enable_rag = rag_config.get('enabled', True)
        self.rag_similarity_top_k = rag_config.get('similarity_top_k', 5)
        self.rag_vector_distance_threshold = rag_config.get('vector_distance_threshold', 0.3)

        # Chat history configuration
        chat_config = self.config.get('chat_history', {})
        self.max_history_length = chat_config.get('max_length', 3)
        self.summarize_threshold = chat_config.get('summarize_threshold', 5)
        self.max_context_length = chat_config.get('max_context_length', 4000)

        # Initialize services
        self._model = None
        self._rag_resources = None

        self._initialize_services()

    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file"""
        try:
            if not os.path.exists(config_path):
                raise FileNotFoundError(f"Configuration file not found: {config_path}")

            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
                print(f"✅ Configuration loaded from: {config_path}")
                return config
        except Exception as e:
            print(f"❌ Failed to load configuration: {e}")
            raise

    def _initialize_services(self):
        """Initialize Vertex AI and RAG services"""
        try:
            # Initialize Vertex AI using gcloud authentication
            vertexai.init(project=self.project_id, location=self.location)
            print(f"✅ Vertex AI initialized: {self.project_id} in {self.location}")

            # Initialize the generative model
            self._model = GenerativeModel(
                model_name=self.model_name,
                generation_config=GenerationConfig(
                    temperature=self.temperature,
                    max_output_tokens=self.max_output_tokens,
                    top_p=self.top_p,
                    top_k=self.top_k
                )
            )
            print(f"✅ Model initialized: {self.model_name}")

            # Initialize RAG resources if enabled
            if self.enable_rag and self.rag_corpus_id:
                self._rag_resources = [
                    rag.RagResource(
                        rag_corpus=f"projects/{self.project_id}/locations/{self.location}/ragCorpora/{self.rag_corpus_id}"
                    )
                ]
                print(f"✅ RAG engine initialized with corpus: {self.rag_corpus_id}")
            else:
                print("ℹ️ RAG engine disabled or no corpus ID provided")

        except Exception as e:
            print(f"❌ Failed to initialize services: {e}")
            raise

    def _retrieve_rag_context(self, query: str) -> str:
        """Retrieve context from RAG corpus"""
        if not self._rag_resources:
            return ""

        try:
            retrieval_response = rag.retrieval_query(
                rag_resources=self._rag_resources,
                text=query,
                similarity_top_k=self.rag_similarity_top_k,
                vector_distance_threshold=self.rag_vector_distance_threshold
            )

            if (retrieval_response and hasattr(retrieval_response, 'contexts') and
                    retrieval_response.contexts and hasattr(retrieval_response.contexts, 'contexts') and
                    retrieval_response.contexts.contexts):

                all_text_segments = []
                for context_obj in retrieval_response.contexts.contexts:
                    if hasattr(context_obj, 'text') and context_obj.text:
                        all_text_segments.append(context_obj.text)

                context = "\n\n".join(all_text_segments)
                return context[:self.max_context_length]

            return ""

        except Exception as e:
            print(f"⚠️ RAG retrieval error: {e}")
            return ""

    def _build_conversation_context(self, session_data: Dict[str, Any]) -> str:
        """Build conversation context from session data"""
        context_parts = []

        # Add summary if exists
        if session_data.get("summary"):
            context_parts.append(f"Previous conversation summary:\n{session_data['summary']}")

        # Add recent messages (last N messages)
        messages = session_data.get("messages", [])
        recent_messages = messages[-self.max_history_length:]

        if recent_messages:
            context_parts.append("Recent conversation:")
            for msg in recent_messages:
                context_parts.append(f"User: {msg['user']}")
                context_parts.append(f"Assistant: {msg['assistant']}")

        return "\n\n".join(context_parts)

    def _should_summarize(self, session_data: Dict[str, Any]) -> bool:
        """Check if conversation should be summarized"""
        message_count = session_data.get("message_count", 0)
        return message_count > 0 and message_count % self.summarize_threshold == 0

    def summarize_conversation(self, messages: List[Dict[str, Any]]) -> str:
        """Summarize conversation history"""
        if not messages:
            return ""

        try:
            # Prepare conversation for summarization
            conversation_text = []
            for msg in messages:
                conversation_text.append(f"User: {msg['user']}")
                conversation_text.append(f"Assistant: {msg['assistant']}")

            conversation = "\n".join(conversation_text)
            prompt = RAGPrompts.get_summarization_prompt(conversation)

            # Generate summary
            response = self._model.generate_content([Part.from_text(prompt)])
            return response.text.strip()

        except Exception as e:
            print(f"⚠️ Error summarizing conversation: {e}")
            return ""

    def chat_with_history(self, message: str, session_data: Dict[str, Any], use_rag: bool = True) -> Tuple[str, str]:
        """Chat with history management and optional RAG"""
        if not self._model:
            return "❌ Model not initialized.", ""

        try:
            # Retrieve RAG context if enabled
            rag_context = ""
            if use_rag and self._rag_resources:
                rag_context = self._retrieve_rag_context(message)

            # Build conversation context
            conversation_context = self._build_conversation_context(session_data)

            # Build final prompt
            if rag_context:
                prompt = RAGPrompts.get_rag_chat_prompt(
                    user_message=message,
                    rag_context=rag_context,
                    conversation_context=conversation_context
                )
            else:
                prompt = RAGPrompts.get_chat_prompt(
                    user_message=message,
                    conversation_context=conversation_context
                )

            # Generate response
            response = self._model.generate_content([Part.from_text(prompt)])

            # Check if we need to summarize
            if self._should_summarize(session_data):
                summary = self.summarize_conversation(session_data.get("messages", []))
                if summary:
                    session_data["summary"] = summary
                    # Keep only recent messages after summarization
                    session_data["messages"] = session_data["messages"][-2:]

            return response.text.strip(), rag_context

        except Exception as e:
            return f"❌ Error generating response: {e}", ""

    def chat_with_history_stream(self, message: str, session_data: Dict[str, Any], use_rag: bool = True) -> Generator[
        Tuple[str, str], None, None]:
        """Streaming chat with history management"""
        if not self._model:
            yield "❌ Model not initialized.", ""
            return

        try:
            # Retrieve RAG context if enabled
            rag_context = ""
            if use_rag and self._rag_resources:
                rag_context = self._retrieve_rag_context(message)

            # Build conversation context
            conversation_context = self._build_conversation_context(session_data)

            # Build final prompt
            if rag_context:
                prompt = RAGPrompts.get_rag_chat_prompt(
                    user_message=message,
                    rag_context=rag_context,
                    conversation_context=conversation_context
                )
            else:
                prompt = RAGPrompts.get_chat_prompt(
                    user_message=message,
                    conversation_context=conversation_context
                )

            # Stream response
            stream_response = self._model.generate_content(
                [Part.from_text(prompt)],
                stream=True
            )

            full_response = ""
            for chunk in stream_response:
                chunk_text = ""
                if hasattr(chunk, 'text') and chunk.text:
                    chunk_text = chunk.text
                elif hasattr(chunk, 'candidates') and chunk.candidates:
                    for candidate in chunk.candidates:
                        if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                            for part in candidate.content.parts:
                                if hasattr(part, 'text') and part.text:
                                    chunk_text += part.text

                if chunk_text:
                    full_response += chunk_text
                    yield chunk_text, rag_context

            # Check if we need to summarize after streaming is complete
            if self._should_summarize(session_data):
                summary = self.summarize_conversation(session_data.get("messages", []))
                if summary:
                    session_data["summary"] = summary
                    session_data["messages"] = session_data["messages"][-2:]

        except Exception as e:
            yield f"❌ Error generating response: {e}", ""

    def is_initialized(self) -> bool:
        """Check if the model is properly initialized"""
        return self._model is not None

    def is_rag_initialized(self) -> bool:
        """Check if RAG is properly initialized"""
        return self._rag_resources is not None

    def get_config(self) -> dict:
        """Get current configuration"""
        return self.config

    def get_stats(self) -> Dict[str, Any]:
        """Get service statistics"""
        return {
            "model_initialized": self.is_initialized(),
            "rag_initialized": self.is_rag_initialized(),
            "project_id": self.project_id,
            "location": self.location,
            "model_name": self.model_name,
            "rag_corpus_id": self.rag_corpus_id,
            "max_history_length": self.max_history_length,
            "summarize_threshold": self.summarize_threshold
        }