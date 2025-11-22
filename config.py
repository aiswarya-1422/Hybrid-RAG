# config.py

PDF_PATH = "data/2025-bmw-x5-owners-manual.pdf"

# Folder where Chroma DB will store embeddings
VECTOR_DB_DIR = "enbeddings"

# Ollama config
OLLAMA_BASE_URL = "http://localhost:11434"
EMBED_MODEL = "nomic-embed-text"
LLM_MODEL = "llama3"

# Chunking
CHUNK_SIZE = 800       # characters
CHUNK_OVERLAP = 200    # characters

# Retrieval
TOP_K = 5
MIN_SIMILARITY_THRESHOLD = 0.2
