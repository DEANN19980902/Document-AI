""""""

import os
from typing import List, Dict, Any, Optional
from langchain_groq import ChatGroq
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.schema import Document
import chromadb
from datetime import datetime


class RAGServiceGroq:
    
    def __init__(self, persist_directory: str = "./vector_db"):
        self.persist_directory = persist_directory
        
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        self.vectorstore = Chroma(
            persist_directory=persist_directory,
            embedding_function=self.embeddings
        )
        
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            raise ValueError("Please set GROQ_API_KEY env var. Get one at https://console.groq.com/")
        
        self.llm = ChatGroq(
            groq_api_key=groq_api_key,
            model_name="llama-3.1-8b-instant",
            temperature=0.1,
            max_tokens=1024
        )
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        self.qa_chain = None
        self._setup_qa_chain()
    
    def _setup_qa_chain(self):
        try:
            doc_count = self.vectorstore._collection.count()
            print(f"DEBUG: vector db docs: {doc_count}")
            if doc_count > 0:
                self.qa_chain = RetrievalQA.from_chain_type(
                    llm=self.llm,
                    chain_type="stuff",
                    retriever=self.vectorstore.as_retriever(
                        search_kwargs={"k": 5}
                    ),
                    return_source_documents=True
                )
                print("DEBUG: qa chain ready")
            else:
                print("DEBUG: vector db empty, skip qa chain")
        except Exception as e:
            print(f"DEBUG: qa chain setup error: {str(e)}")
    
    def add_document(self, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        try:
            chunks = self.text_splitter.split_text(content)
            
            documents = []
            for i, chunk in enumerate(chunks):
                doc_metadata = {
                    **metadata,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "added_at": datetime.now().isoformat()
                }
                documents.append(Document(page_content=chunk, metadata=doc_metadata))
            
            self.vectorstore.add_documents(documents)
            
            self._setup_qa_chain()
            
            return {
                "success": True,
                "message": f"Added document with {len(chunks)} chunks",
                "chunks_count": len(chunks),
                "metadata": metadata
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Add failed: {str(e)}",
                "error": str(e)
            }
    
    def query(self, question: str, document_filter: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        try:
            if self.vectorstore._collection.count() == 0:
                return {
                    "success": False,
                    "answer": "No documents available. Please upload first.",
                    "sources": [],
                    "error": "No documents available"
                }
            
            if not self.qa_chain:
                self._setup_qa_chain()
            
            if not self.qa_chain:
                return {
                    "success": False,
                    "answer": "QA chain not initialized. Please retry.",
                    "sources": [],
                    "error": "QA chain not initialized"
                }
            
            if document_filter:
                retriever = self.vectorstore.as_retriever(
                    search_kwargs={"k": 5, "filter": document_filter}
                )
                chain = RetrievalQA.from_chain_type(
                    llm=self.llm,
                    chain_type="stuff",
                    retriever=retriever,
                    return_source_documents=True,
                )
                result = chain({"query": question})
            else:
                result = self.qa_chain({"query": question})
            
            sources = []
            if "source_documents" in result:
                for doc in result["source_documents"]:
                    sources.append({
                        "content": doc.page_content[:200] + "...",
                        "metadata": doc.metadata,
                        "relevance_score": getattr(doc, 'score', 0.0)
                    })
            
            return {
                "success": True,
                "answer": result["result"],
                "sources": sources,
                "question": question,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "answer": f"Error: {str(e)}",
                "sources": [],
                "error": str(e)
            }
    
    def search_similar(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        try:
            if self.vectorstore._collection.count() == 0:
                return []
            
            docs = self.vectorstore.similarity_search_with_score(query, k=k)
            
            results = []
            for doc, score in docs:
                results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "similarity_score": float(score)
                })
            
            return results
            
        except Exception as e:
            print(f"search error: {str(e)}")
            return []
    
    def get_document_stats(self) -> Dict[str, Any]:
        try:
            collection = self.vectorstore._collection
            total_docs = collection.count()
            
            all_docs = collection.get()
            metadata_list = all_docs.get("metadatas", [])
            
            doc_types = {}
            for metadata in metadata_list:
                doc_type = metadata.get("type", "unknown")
                doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
            
            return {
                "total_documents": total_docs,
                "document_types": doc_types,
                "vector_db_size": total_docs,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "total_documents": 0,
                "document_types": {},
                "error": str(e)
            }
    
    def clear_all_documents(self) -> Dict[str, Any]:
        try:
            import shutil
            if os.path.exists(self.persist_directory):
                shutil.rmtree(self.persist_directory)
            
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
            
            self.qa_chain = None
            
            return {
                "success": True,
                "message": "Cleared"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Clear failed: {str(e)}",
                "error": str(e)
            }
