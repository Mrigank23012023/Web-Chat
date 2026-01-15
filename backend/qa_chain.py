import logging
from langchain_groq import ChatGroq
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from config import Config

logger = logging.getLogger(__name__)

class QAChain:
    """Orchestrates the answer generation using LLM and strict RAG logic."""
    
    def __init__(self, vectorstore_retriever):
        """
        Initialize the RAG chain.
        
        Args:
            vectorstore_retriever: The retriever interface from VectorStore.
        """
        self.retriever = vectorstore_retriever
        
        # Initialize LLM (Groq via ChatGroq interface)
        self.llm = ChatGroq(
            model_name=Config.LLM_MODEL_NAME, # langchain-groq uses 'model_name' or 'model'
            temperature=Config.LLM_TEMPERATURE,
            groq_api_key=Config.GROQ_API_KEY
        )
        
        # Strict Prompt Template with History
        template = """Use the following pieces of context to answer the question at the end. 
If you don't know the answer, just say 'The answer is not available on the provided website.', don't try to make up an answer.

{context}

Current Conversation:
{chat_history}

Question: {question}
Answer:"""
        
        self.prompt = PromptTemplate(
            template=template, 
            input_variables=["context", "chat_history", "question"]
        )
        
        # Load the "stuff" chain for manual execution
        self.chain = load_qa_chain(
            llm=self.llm, 
            chain_type="stuff", 
            prompt=self.prompt
        )
    
    def answer(self, query: str, chat_history: str = ""):
        """
        Generates an answer using strict pre-flight retrieval check.
        """
        logger.info(f"Generating answer for query: {query}")
        try:
            # 1. Pre-flight Retrieval Check
            # Robust retrieval: try .invoke then .get_relevant_documents
            if hasattr(self.retriever, 'invoke'):
                docs = self.retriever.invoke(query)
            else:
                docs = self.retriever.get_relevant_documents(query)
            
            # QA Rule: If retrieval empty → fallback message
            if not docs:
                logger.warning(f"No relevant documents found for: {query}")
                return {
                    "answer": "The answer is not available on the provided website.",
                    "sources": []
                }
            
            # 2. Execution
            # Robust chain execution: try .invoke then .run/.call
            inputs = {"input_documents": docs, "question": query, "chat_history": chat_history}
            
            if hasattr(self.chain, 'invoke'):
                response = self.chain.invoke(inputs, return_only_outputs=True)
                answer_text = response['output_text']
            else:
                # Legacy fallback
                response = self.chain(inputs, return_only_outputs=True)
                answer_text = response['output_text']
            
            return {
                "answer": answer_text,
                "sources": docs
            }
            
        except Exception as e:
            logger.error(f"Error executing QA chain: {e}", exc_info=True)
            return {
                "answer": f"An error occurred: {str(e)}",
                "sources": []
            }
