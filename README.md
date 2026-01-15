# AI Website-Grounded Chatbot

An intelligent RAG (Retrieval-Augmented Generation) application that allows users to chat with the content of any website. 

The application crawls the target website, indexes its content into a vector database, and uses a high-performance Large Language Model (LLM) to answer questions based strictly on the website's data.

## 🚀 Key Features

*   **Instant Indexing**: Crawls and extracts text from user-provided URLs.
*   **Vector Search**: Uses semantic search to find the most relevant context for every question.
*   **Hallucination Prevention**: Strict prompts ensure the AI answers *only* using the provided website context.
*   **High-Speed Inference**: Powered by **Groq**'s LPU inference engine running Llama 3.
*   **Vibrant UI**: Custom-styled Streamlit interface with a premium, responsive design.

## 🛠️ Technology Stack

This project is built using a modern Python AI stack:

### Frontend
*   **[Streamlit](https://streamlit.io/)** (v1.28.0): The web framework used for the user interface.
    *   *Note*: Pinned to v1.28.0 to maintain compatibility with specific Tornado versions.
*   **Custom CSS**: Tailored styling for a "Vibrant" aesthetic (Inter font, custom color palette).

### AI & Logic Layer
*   **[LangChain](https://www.langchain.com/)** (v0.2.x): The orchestration framework managing the LLM interaction and retrieval chains.
    *   Uses `langchain-groq` for optimized API communication.
*   **[Groq API](https://groq.com/)**: Provides access to the **Llama-3.3-70b-versatile** model for near-instant text generation.
*   **[Sentence Transformers](https://sbert.net/)**: Uses `all-MiniLM-L6-v2` for generating efficient local embeddings.

### Data & crawling
*   **[ChromaDB](https://www.trychroma.com/)**: The persistent vector database used to store website embeddings.
*   **[Trafilatura](https://trafilatura.readthedocs.io/)** & **BeautifulSoup4**: Robust tools for scraping and cleaning HTML content from websites.

### Core Dependencies
*   **Python** 3.10+
*   **Tornado** (v6.1): The underlying web server for Streamlit (strictly pinned to 6.1 for stability).

## 🏗️ Architecture

1.  **Ingestion Phase**:
    *   **Crawl**: The generic crawler visits the seed URL and discovers internal links (limit 5 pages).
    *   **Extract**: `Trafilatura` parses the HTML to extract main content text, discarding menus/ads.
    *   **Chunk**: Text is split into chunks of 1000 characters with 150-character overlap.
    *   **Embed**: Chunks are converted to vector embeddings using `all-MiniLM-L6-v2`.
    *   **Store**: Embeddings + Metadata are saved in `chroma_db` (local directory).

2.  **Retrieval Phase (RAG)**:
    *   **Query**: User asks a question via the chat interface.
    *   **Search**: The system converts the question to a vector and queries ChromaDB for the top 4 matching chunks.
    *   **Generate**: A strict prompt (`"Answer only using the context..."`) is sent to Llama 3 via Groq, including the retrieved chunks.
    *   **Response**: The AI generates the final answer or states if the information is missing.

## 📦 Setup & Installation

### Prerequisites
*   Python 3.10 installed on your system.
*   A **Groq API Key** (Get it from [console.groq.com](https://console.groq.com)).

### Installation Steps

1.  **Clone the Repository**
    ```bash
    git clone <repository-url>
    cd mrigank
    ```

2.  **Create Virtual Environment**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment**
    Create a `.env` file in the root directory:
    ```bash
    GROQ_API_KEY=gsk_your_key_here...
    ```

5.  **Run the Application**
    ```bash
    streamlit run app.py
    ```

## 🧩 Versioning Notes (Dev Docs)

This project relies on specific versions to ensure stability between Streamlit, Tornado, and LangChain:

*   **Streamlit 1.28.0 + Tornado 6.1**: This combination is enforced to prevent `WebSocketHandler` errors common on macOS deployments.
*   **LangChain 0.2.x**: The codebase has been migrated to the new LangChain 0.2 architecture (separating `langchain-community`, `langchain-text-splitters`, etc.) to resolve OpenAI SDK conflicts.

## 📝 Usage

1.  Enter a URL (e.g., `https://developer.phonepe.com`) in the input box.
2.  Click **"Index Website"**. Wait for the specific pages to be crawled and processed.
3.  Once the "Currently Chatting with..." banner appears, type your questions in the chat box!
