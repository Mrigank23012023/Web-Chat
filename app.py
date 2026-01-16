try:
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    pass

import streamlit as st
import time
import logging
import traceback

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Lazy load imports inside safe blocks or main
try:
    from frontend.ui import UI
    from backend.auth import Auth
    from config import Config
except Exception as e:
    st.error(f"Critical Error: Failed to import core modules. {e}")
    st.code(traceback.format_exc())
    st.stop()

@st.cache_resource
def get_embedder():
    from backend.embedder import Embedder
    return Embedder().get_embedding_function()

def main():
    st.set_page_config(page_title="AI Website Chatbot", page_icon="🤖", layout="wide")
    
    if not Config.GROQ_API_KEY:
        st.error("🚨 `GROQ_API_KEY` is missing! Please set it in your `.env` file or Streamlit secrets.")
        st.stop()
    
    UI.load_css()
    
    if not Auth.check_login():
        UI.render_login(Auth)
        return

    UI.init_state()
    UI.render_sidebar(Auth)
    
    UI.render_header()
    
    url_to_index = UI.render_input_section()
    
    if url_to_index:
        if st.session_state.get("indexed") and st.session_state.get("current_url") == url_to_index:
            pass
        else:
            with st.status("Indexing website content...", expanded=True) as status:
                t_start = time.time()
                
                # LAZY IMPORTS START
                from backend.crawler import Crawler
                from backend.extractor import Extractor
                from backend.cleaner import Cleaner
                from backend.chunker import Chunker
                from backend.vectorstore import VectorStore
                # LAZY IMPORTS END

                st.write(f"🕷️ Starting crawl for {url_to_index}...")
                crawler = Crawler()
                try:
                    crawled_pages = crawler.crawl(url_to_index)
                    st.write(f"✅ Found {len(crawled_pages)} pages:")
                    for page in crawled_pages:
                        st.write(f"- {page['url']}")
                    
                    st.session_state.raw_data = crawled_pages
                    
                except Exception as e:
                    st.error(f"Crawling failed: {str(e)}")
                    status.update(label="Indexing Failed", state="error")
                    st.stop()
                
                st.write("📝 Extracting content...")
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
                        st.caption(f"Extracted {len(result['text'])} chars from {page['url']} ('{result['title']}')")
                    else:
                        st.caption(f"⚠️ Skipped {page['url']} (Low quality/Empty)")
                
                st.session_state.extracted_data = extracted_data
                st.write(f"✅ Extracted content from {len(extracted_data)} pages.")

                st.write("🧩 Splitting text into chunks...")
                cleaner = Cleaner()
                chunker = Chunker()
                all_chunks = []
                
                for data in extracted_data:
                    clean_text = cleaner.clean(data['text'])
                    chunks = chunker.chunk(clean_text, data['url'], data['title'])
                    all_chunks.extend(chunks)
                
                st.session_state.chunks = all_chunks
                st.write(f"✅ Generated {len(all_chunks)} chunks from {len(extracted_data)} pages.")

                st.write(f"🧠 Generating embeddings and storing in {Config.VECTOR_STORE_PROVIDER.title()}...")
                
                embedding_function = get_embedder()
                
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
            st.rerun()

    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar="🧑‍💻" if message["role"] == "user" else "🤖"):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask a question about the website..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(prompt)
            
        with st.chat_message("assistant", avatar="🤖"):
            message_placeholder = st.empty()
            
            if "vectorstore" not in st.session_state:
                response = "Please index a website first!"
                message_placeholder.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
                return 

            try:
                from backend.qa_chain import QAChain
                qa_chain = QAChain(st.session_state.vectorstore)
                
                history_window = st.session_state.messages[-5:] 
                chat_history_str = ""
                for msg in history_window:
                    role_label = "Human" if msg["role"] == "user" else "AI"
                    chat_history_str += f"{role_label}: {msg['content']}\n"
                
                with st.spinner("Thinking..."):
                    result = qa_chain.answer(prompt, chat_history=chat_history_str)
                
                answer_text = result['answer']
                sources = result['sources']
                
                message_placeholder.markdown(answer_text)
                
                if sources:
                    with st.expander("📚 View Sources"):
                        for i, doc in enumerate(sources):
                            source_url = doc.metadata.get('source', 'Unknown')
                            source_title = doc.metadata.get('title', 'Unknown Title')
                            st.markdown(f"**{i+1}. [{source_title}]({source_url})**")
                            st.caption(doc.page_content[:300].replace('\n', ' ') + "...")
                            st.divider()

                st.session_state.messages.append({"role": "assistant", "content": answer_text})
                
            except Exception as e:
                error_msg = f"I encountered an error: {str(e)}"
                message_placeholder.error(error_msg)

if __name__ == "__main__":
    main()
