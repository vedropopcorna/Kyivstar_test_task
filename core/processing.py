import re
import uuid
from typing import List, Any
# from langchain_core.documents import Document
from langchain_experimental.text_splitter import SemanticChunker
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
# from pdfminer.high_level import extract_text
import os
from dotenv import load_dotenv


class TextPreprocessor:
    @staticmethod
    def preprocess(text: str) -> str:
        """Clean and normalize text from PDF extraction"""
        text = text.replace('\x0c', '')
        text = re.sub(r'\n{2,}', '\n\n', text)
        text = re.sub(r'\n\n', '', text)
        text = re.sub(r'\n', ' ', text)
        text = '\n'.join(line.strip() for line in text.split('\n'))
        text = text.replace('•', '•')
        text = re.sub(r' +', ' ', text)
        text = re.sub(r'\s+([.,;:!?])', r'\1', text)
        text = text.replace('«', '"').replace('»', '"')
        return text.strip()

class DocumentProcessor:
    def __init__(self):

        self.semantic_splitter = SemanticChunker(
            HuggingFaceEmbeddings(model_name="intfloat/multilingual-e5-small")
        )
        self.embeddings = HuggingFaceEmbeddings(
            model_name="intfloat/multilingual-e5-small"
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=700,
            chunk_overlap=150,
            length_function=len,
            is_separator_regex=False,
        )

    def process_documents(self, text: str) -> List[Any]:
        """Process text into chunks with metadata"""
        final_chunks = []
        docs = self.semantic_splitter.create_documents([text])

        for i, doc in enumerate(docs):
            doc_id = str(uuid.uuid4())
            chunks = self.text_splitter.split_documents([doc])

            for chunk in chunks:
                chunk.metadata.update({
                    "semantic_doc_id": doc_id,
                    "semantic_doc_index": i,
                    "parent_content": doc.page_content[:200] + "..."
                })
            final_chunks.extend(chunks)
        return final_chunks