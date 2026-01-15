import streamlit as st
import time
import logging
from frontend.ui import UI
from backend.auth import Auth
from config import Config

# Backend Imports
from backend.crawler import Crawler
from backend.extractor import Extractor
from backend.cleaner import Cleaner
from backend.chunker import Chunker
from backend.vectorstore import VectorStore
# Lazy load QAChain or import here - lazy loading inside loop was fine if expensive init, but import is cheap.
from backend.qa_chain import QAChain 

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

@st.cache_resource
def get_embedder():
    from backend.embedder import Embedder
    return Embedder().get_embedding_function()

def main():
    """Main application loop."""
    st.set_page_config(page_title="AI Website Chatbot", page_icon="🤖", layout="wide")
    
    # Critical Check
    if not Config.GROQ_API_KEY:
        st.error("🚨 `GROQ_API_KEY` is missing! Please set it in your `.env` file to use the Chatbot.")
        st.stop()
    
    # 1. Load Styles
    UI.load_css()
    
    # 2. Check Auth
    if not Auth.check_login():
        UI.render_login(Auth)
        return

    # 3. Authenticated Flow
    UI.init_state()
    UI.render_sidebar(Auth)
    
    UI.render_header()
    
    # Render Input Section
    url_to_index = UI.render_input_section()
    
    # Handle Indexing Trigger
    if url_to_index:
        # Guard: Check if this URL is already indexed to prevent loops
        if st.session_state.get("indexed") and st.session_state.get("current_url") == url_to_index:
            # Already indexed, do nothing (or show minor toast)
            pass
        else:
            with st.status("Indexing website content...", expanded=True) as status:
                t_start = time.time()
                
                # 1. Crawl
                st.write(f"🕷️ Starting crawl for {url_to_index}...")
                from backend.crawler import Crawler
                crawler = Crawler()
                try:
                    crawled_pages = crawler.crawl(url_to_index)
                    st.write(f"✅ Found {len(crawled_pages)} pages:")
                    for page in crawled_pages:
                        st.write(f"- {page['url']}")
                    
                    # Store raw data for next phases (Extraction/Embedding)
                    # In a real app, we might store this in a temp folder or pass it to the pipeline directly.
                    # For now, we just acknowledge it.
                    st.session_state.raw_data = crawled_pages
                    
                except Exception as e:
                    st.error(f"Crawling failed: {str(e)}")
                    status.update(label="Indexing Failed", state="error")
                    st.stop()
                
                # 2. Extract
                st.write("📝 Extracting content...")
                from backend.extractor import Extractor
                extractor = Extractor()
                extracted_data = []
                
                for page in crawled_pages:
                    result = extractor.extract(page['html'])
                    if result:
                        extracted_data.append({
                            "url": page['url'], 
                            "text": result['text'], 
                            "title": result['title']
                        })
                        # Show snippet (first 100 chars)
                        st.caption(f"Extracted {len(result['text'])} chars from {page['url']} ('{result['title']}')")
                    else:
                        st.caption(f"⚠️ Skipped {page['url']} (Low quality/Empty)")
                
                st.session_state.extracted_data = extracted_data
                st.write(f"✅ Extracted content from {len(extracted_data)} pages.")

                # 3. Clean & Chunk
                st.write("🧩 Splitting text into chunks...")
                from backend.cleaner import Cleaner
                from backend.chunker import Chunker
                
                cleaner = Cleaner()
                chunker = Chunker()
                all_chunks = []
                
                for data in extracted_data:
                    clean_text = cleaner.clean(data['text'])
                    chunks = chunker.chunk(clean_text, data['url'], data['title'])
                    all_chunks.extend(chunks)
                
                st.session_state.chunks = all_chunks
                st.write(f"✅ Generated {len(all_chunks)} chunks from {len(extracted_data)} pages.")
                
                # 4. Embed & Store
                st.write("🧠 Generating embeddings and storing in Vector DB...")
                from backend.vectorstore import VectorStore
                
                # Load cached embedder
                embedding_function = get_embedder()
                
                # Create Vector Store
                try:
                    vs_wrapper = VectorStore(collection_name="website_content")
                    vectorstore = vs_wrapper.create_collection(all_chunks, embedding_function)
                    
                    if vectorstore:
                        st.session_state.vectorstore = vs_wrapper.as_retriever(vectorstore)
                        st.write(f"✅ Successfully stored in {Config.VECTOR_STORE_PROVIDER.title()} DB.")
                    else:
                         raise RuntimeError("Vector Store returned None without exception.")

                except Exception as e:
                    st.error(f"Failed to create Vector Store: {str(e)}")
                    status.update(label="Indexing Failed", state="error")
                    st.stop()
                
                status.update(label=f"Indexing Complete! ({len(all_chunks)} chunks indexed)", state="complete", expanded=False)
            
            st.session_state.indexed = True
            st.session_state.current_url = url_to_index
            st.success(f"Successfully indexed: {url_to_index}")
            # Note: No rerun needed here necessarily if we want to show the success message, 
            # but rerun helps update the UI state cleanly (e.g., enabling chat input).
            # However, rerun will clear the success message. 
            # Let's keep rerun for strict state synchronization.
            st.rerun()

    # Render Chat Interface
    # UI.render_chat_interface() -> Replaced with custom RAG integration logic
    
    # 1. Display Chat History
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar="🧑‍💻" if message["role"] == "user" else "🤖"):
            st.markdown(message["content"])

    # 2. Handle User Input
    if prompt := st.chat_input("Ask a question about the website..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(prompt)
            
        # Display assistant response
        with st.chat_message("assistant", avatar="🤖"):
            message_placeholder = st.empty()
            
            # Check if knowledge base is ready
            if "vectorstore" not in st.session_state:
                response = "Please index a website first!"
                message_placeholder.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
                return # Stop execution for this turn

            try:
                # Initialize QA Chain
                from backend.qa_chain import QAChain
                qa_chain = QAChain(st.session_state.vectorstore)
                
                # Build Chat History String (Last 5 turns for context)
                history_window = st.session_state.messages[-5:] # Last 5 messages
                chat_history_str = ""
                for msg in history_window:
                    role_label = "Human" if msg["role"] == "user" else "AI"
                    chat_history_str += f"{role_label}: {msg['content']}\n"
                
                with st.spinner("Thinking..."):
                    # Phase 10: Pass history for memory
                    result = qa_chain.answer(prompt, chat_history=chat_history_str)
                
                answer_text = result['answer']
                sources = result['sources']
                
                message_placeholder.markdown(answer_text)
                
                # Display Sources
                if sources:
                    with st.expander("📚 View Sources"):
                        for i, doc in enumerate(sources):
                            source_url = doc.metadata.get('source', 'Unknown')
                            source_title = doc.metadata.get('title', 'Unknown Title')
                            st.markdown(f"**{i+1}. [{source_title}]({source_url})**")
                            # Show a small snippet
                            st.caption(doc.page_content[:300].replace('\n', ' ') + "...")
                            st.divider()

                # Add assistant message to history
                st.session_state.messages.append({"role": "assistant", "content": answer_text})
                
            except Exception as e:
                error_msg = f"I encountered an error: {str(e)}"
                message_placeholder.error(error_msg)

if __name__ == "__main__":
    main()
