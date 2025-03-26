from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings

class VectorStoreManager:
    def __init__(self, embeddings):
        self.embeddings = embeddings
        self.vector_store = self._initialize_vector_store()

    def _initialize_vector_store(self):
        return Chroma(
            collection_name="knowledge_collection",
            embedding_function=self.embeddings,
            persist_directory="./storage/chroma_embeddings"
        )

    def update_vector_store(self, documents: list[Document]):
        self.vector_store.delete_collection()
        self.vector_store = Chroma.from_documents(
            collection_name="knowledge_collection",
            documents=documents,
            embedding=self.embeddings,
            persist_directory="./storage/chroma_embeddings"
        )
        return self.vector_store
