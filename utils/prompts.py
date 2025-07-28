# utils/prompts.py

class RAGPrompts:
    """
    Centralized prompt management for the RAG system using static methods
    """

    @staticmethod
    def get_rag_chat_prompt(user_message: str, rag_context: str, conversation_context: str = "") -> str:
        """
        Generate a prompt for RAG-enabled chat with conversation history
        """
        prompt_parts = [
            "You are a helpful AI assistant with access to a knowledge base.",
            "Use the provided context to answer questions accurately and comprehensively.",
            "If the context doesn't contain relevant information, clearly state this and provide a helpful response based on your general knowledge.",
            ""
        ]

        if conversation_context:
            prompt_parts.extend([
                "CONVERSATION HISTORY:",
                conversation_context,
                ""
            ])

        if rag_context:
            prompt_parts.extend([
                "KNOWLEDGE BASE CONTEXT:",
                rag_context,
                ""
            ])

        prompt_parts.extend([
            "CURRENT USER MESSAGE:",
            user_message,
            "",
            "INSTRUCTIONS:",
            "- Use the knowledge base context to answer the user's question if relevant",
            "- Consider the conversation history to maintain context and continuity",
            "- If the knowledge base doesn't contain relevant information, clearly mention this",
            "- Provide a helpful, accurate, and conversational response",
            "- Be concise but comprehensive",
            "",
            "RESPONSE:"
        ])

        return "\n".join(prompt_parts)

    @staticmethod
    def get_chat_prompt(user_message: str, conversation_context: str = "") -> str:
        """
        Generate a prompt for regular chat without RAG
        """
        prompt_parts = [
            "You are a helpful AI assistant engaged in a conversation.",
            "Use the conversation history to maintain context and provide relevant, coherent responses.",
            "Be conversational and natural.",
            ""
        ]

        if conversation_context:
            prompt_parts.extend([
                "CONVERSATION HISTORY:",
                conversation_context,
                ""
            ])

        prompt_parts.extend([
            "CURRENT USER MESSAGE:",
            user_message,
            "",
            "INSTRUCTIONS:",
            "- Consider the conversation history to maintain context and continuity",
            "- Provide a helpful, accurate, and conversational response",
            "- Be natural and engaging in your communication style",
            "",
            "RESPONSE:"
        ])

        return "\n".join(prompt_parts)

    @staticmethod
    def get_summarization_prompt(conversation_text: str) -> str:
        """
        Generate a prompt for conversation summarization
        """
        prompt_parts = [
            "You are tasked with summarizing conversation history.",
            "Create a concise summary that captures the key topics discussed, important information shared, and the general context of the conversation.",
            "",
            "CONVERSATION TO SUMMARIZE:",
            conversation_text,
            "",
            "INSTRUCTIONS:",
            "- Create a brief but comprehensive summary (2-3 sentences)",
            "- Focus on key topics, decisions, and important information",
            "- Maintain the context and flow of the conversation",
            "- Use clear, concise language",
            "",
            "SUMMARY:"
        ]

        return "\n".join(prompt_parts)

    @staticmethod
    def get_system_prompt() -> str:
        """
        Get the base system prompt
        """
        return (
            "You are a helpful, accurate, and conversational AI assistant. "
            "Provide clear, concise, and relevant responses to user queries. "
            "When using knowledge base information, cite it appropriately. "
            "When information is uncertain or unavailable, be transparent about limitations."
        )

    @staticmethod
    def debug_prompt(prompt_type: str, **kwargs) -> str:
        """
        Debug method to see the actual prompt being generated
        """
        if prompt_type == "rag_chat":
            return RAGPrompts.get_rag_chat_prompt(
                kwargs.get("user_message", ""),
                kwargs.get("rag_context", ""),
                kwargs.get("conversation_context", "")
            )
        elif prompt_type == "chat":
            return RAGPrompts.get_chat_prompt(
                kwargs.get("user_message", ""),
                kwargs.get("conversation_context", "")
            )
        elif prompt_type == "summarization":
            return RAGPrompts.get_summarization_prompt(
                kwargs.get("conversation_text", "")
            )
        else:
            return f"Unknown prompt type: {prompt_type}"