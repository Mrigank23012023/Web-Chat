
try:
    import backend.validator
    import backend.crawler
    import backend.extractor
    import backend.cleaner
    import backend.chunker
    import backend.embedder
    import backend.vectorstore
    import backend.retriever
    import backend.qa_chain
    import frontend.ui
    import config
    print("All modules imported successfully.")
except ImportError as e:
    print(f"ImportError: {e}")
    exit(1)
