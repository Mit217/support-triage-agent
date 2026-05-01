print("Starting script...")
try:
    print("Importing modules...")
    from retriever import load_docs
    print("Modules imported successfully")
    print("Loading docs...")
    docs = load_docs()
    print(f"Loaded {len(docs)} docs")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()