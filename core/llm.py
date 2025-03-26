# from langchain_experimental.text_splitter import SemanticChunker
from transformers import pipeline
from langchain_huggingface import HuggingFacePipeline
from langchain.retrievers import ContextualCompressionRetriever
from langchain_cohere import CohereRerank
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.runnables import RunnablePassthrough
import os
from dotenv import load_dotenv
load_dotenv()


class LLMFactory:
    @staticmethod
    def create_llm():
        """Create and configure the language model"""
        model_id = "google/gemma-3-4b-it"
        hf_pipeline = pipeline(
            "text-generation",
            model=model_id,
            max_length=4096,
            temperature=0.1,
            do_sample=True,
            truncation=True
        )
        return HuggingFacePipeline(pipeline=hf_pipeline)


class RAGChainBuilder:
    @staticmethod
    def build_chain(vector_store, llm):
        """Construct the RAG pipeline with history awareness"""
        # Contextualize question prompt
        contextualize_q_system_prompt = (
            "Given a chat history and the latest user question, "
            "formulate a standalone question which can be understood "
            "without the chat history. Do NOT answer the question, just "
            "reformulate it if needed and otherwise return it as is."
        )
        contextualize_q_prompt = ChatPromptTemplate.from_messages([
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])

        # Create retriever with compression
        retriever = vector_store.as_retriever(search_kwargs={"k": 4})
        if not os.getenv("COHERE_API_KEY"):
            raise RuntimeError("COHERE_API_KEY environment variable is required")
        compressor = CohereRerank(
            model="rerank-v3.5",
            cohere_api_key=os.getenv("COHERE_API_KEY")
        )
        compression_retriever = ContextualCompressionRetriever(
            base_compressor=compressor,
            base_retriever=retriever
        )
        history_aware_retriever = create_history_aware_retriever(
            llm,
            compression_retriever,
            contextualize_q_prompt
        )

        # QA system prompt
        qa_system_prompt = """You are a multilingual assistant. Respond exclusively in {language} language.
        Use the following context and chat history to answer the question.
        If you don't know the answer, say you don't know in {language}.
        Keep answers concise (2-3 sentences max).

        Context:
        {context}"""

        qa_prompt = ChatPromptTemplate.from_messages([
            ("system", qa_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])

        # Create document chain
        question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

        # Create full RAG chain
        return (
                RunnablePassthrough.assign(
                    context=lambda x: history_aware_retriever.invoke({
                        "input": x["input"],
                        "chat_history": x["chat_history"]
                    })
                )
                | question_answer_chain
        )
