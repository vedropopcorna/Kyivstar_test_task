from collections import deque
from typing import Dict, Deque
from langchain_core.messages import HumanMessage, AIMessage
from pdfminer.high_level import extract_text

from app.api.models import APIRequest, APIResponse


class ChatbotService:
    def __init__(self):
        from core.processing import TextPreprocessor, DocumentProcessor
        from core.vectorstore import VectorStoreManager
        from core.llm import LLMFactory, RAGChainBuilder

        self.text_processor = TextPreprocessor()
        self.doc_processor = DocumentProcessor()
        self.vector_store_manager = VectorStoreManager(self.doc_processor.embeddings)
        self.llm = LLMFactory.create_llm()

        text = extract_text("./data/knowledge.pdf")
        processed_text = self.text_processor.preprocess(text)
        documents = self.doc_processor.process_documents(processed_text)
        self.vector_store_manager.update_vector_store(documents)

        self.rag_chain = RAGChainBuilder.build_chain(
            self.vector_store_manager.vector_store,
            self.llm
        )
        self.sessions: Dict[str, Deque] = {}

    def get_session(self, session_id: str) -> deque:
        if session_id not in self.sessions:
            self.sessions[session_id] = deque(maxlen=8)
        return self.sessions[session_id]

    def process_query(self, api_input: APIRequest) -> APIResponse:
        chat_input = api_input.input
        session_id = chat_input.session_id
        chat_history = self.get_session(session_id)

        inputs = {
            "input": chat_input.question,
            "chat_history": list(chat_history),
            "language": chat_input.language
        }

        response = self.rag_chain.invoke(inputs)
        answer = response.split(": ")[-1].strip()

        chat_history.extend([
            HumanMessage(content=chat_input.question),
            AIMessage(content=answer)
        ])

        return APIResponse(
            output=answer,
            session_id=session_id,
            language=chat_input.language
        )