# rag/pipeline.py

import os
import pickle
import numpy as np
import fitz  # PyMuPDF
import faiss

from rag.config import EMBED_MODEL, configure_gemini
from rag.gemini import generate_response

GEMINI_KEY = configure_gemini()

def extract_text_from_pdfs(file_names):
    texts, metadata = [], []
    print("[INFO] Starting PDF text extraction...")
    for file_name in file_names:
        if not os.path.exists(file_name):
            print(f"[WARNING] File '{file_name}' not found.")
            continue
        try:
            with fitz.open(file_name) as doc:
                full_text = "\n".join(page.get_text() for page in doc)
                chunks = [c.strip() for c in full_text.split("\n\n") if c.strip()]
                texts.extend(chunks)
                metadata.extend([{"source": file_name}] * len(chunks))
            print(f"[OK] Extracted text from '{file_name}'. Chunks: {len(chunks)}")
        except Exception as e:
            print(f"[ERROR] Processing '{file_name}': {e}")
    return texts, metadata


def create_embeddings(texts, batch_size=100, normalize=True):
    import google.generativeai as genai
    if not texts:
        print("[WARNING] No texts to embed.")
        return None
    print("[INFO] Creating embeddings... (this may take a while)")
    emb_list = []
    try:
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            print(f"[INFO] Processing batch {i//batch_size + 1}...")
            result = genai.embed_content(model=EMBED_MODEL, content=batch)
            batch_embeddings = result.get("embedding")
            if not batch_embeddings:
                raise RuntimeError("Embedding response missing 'embedding' key.")
            emb_list.extend(batch_embeddings)
        embs = np.asarray(emb_list, dtype="float32")
        if normalize:
            faiss.normalize_L2(embs)
        print(f"[OK] Embeddings created. Shape: {embs.shape}")
        return embs
    except Exception as e:
        print(f"[ERROR] Creating embeddings: {e}")
        return None


def create_faiss_index(embeddings, use_cosine=True):
    if embeddings is None or len(embeddings) == 0:
        print("[WARNING] No embeddings to index.")
        return None
    d = embeddings.shape[1]
    index = faiss.IndexFlatIP(d) if use_cosine else faiss.IndexFlatL2(d)
    index.add(embeddings)
    print("[OK] FAISS index created.")
    return index


def search_relevant_context(query, index, texts, top_k=5, use_cosine=True):
    import google.generativeai as genai
    if index is None or not texts:
        return "Sorry, the knowledge base was not loaded correctly."
    try:
        r = genai.embed_content(model=EMBED_MODEL, content=query)
        qvec = np.array(r["embedding"], dtype="float32").reshape(1, -1)
        if use_cosine:
            faiss.normalize_L2(qvec)
        k = max(1, min(top_k, len(texts)))
        _, idx = index.search(qvec, k)
        candidates = [i for i in idx[0] if 0 <= i < len(texts)]
        context = "\n\n---\n\n".join(texts[i] for i in candidates)
        return context or "No relevant passages found."
    except Exception as e:
        print(f"[ERROR] Context search: {e}")
        return "An error occurred while searching the guides."


def setup_rag_pipeline():
    cache_dir = "cache"
    os.makedirs(cache_dir, exist_ok=True)

    index_path = os.path.join(cache_dir, "skyrim_guide.index")
    texts_path = os.path.join(cache_dir, "skyrim_guide_texts.pkl")
    files_dir  = "files"

    def find_pdf_files():
        pdfs = []
        if os.path.isdir(files_dir):
            for name in os.listdir(files_dir):
                if name.lower().endswith(".pdf"):
                    pdfs.append(os.path.join(files_dir, name))
        for name in os.listdir("."):
            if name.lower().endswith(".pdf"):
                pdfs.append(os.path.abspath(name))
        return sorted(set(pdfs))

    pdf_files = find_pdf_files()

    if os.path.exists(index_path) and os.path.exists(texts_path):
        print("[INFO] Loading knowledge base from cache...")
        try:
            index = faiss.read_index(index_path)
            with open(texts_path, "rb") as f:
                texts = pickle.load(f)
            print("[OK] Loaded from cache.")
            return texts, index, pdf_files
        except Exception as e:
            print(f"[WARNING] Could not load from cache: {e}. Rebuilding...")

    print("[INFO] Building knowledge base from scratch...")
    if not pdf_files:
        print("[ERROR] No PDF files found.")
        return None, None, []

    texts, _ = extract_text_from_pdfs(pdf_files)
    if not texts:
        print("[ERROR] No text extracted. Check PDFs.")
        return None, None, pdf_files

    embeddings_db = create_embeddings(texts)
    if embeddings_db is None:
        return texts, None, pdf_files

    index = create_faiss_index(embeddings_db, use_cosine=True)
    if index is None:
        return texts, None, pdf_files

    try:
        faiss.write_index(index, index_path)
        with open(texts_path, "wb") as f:
            pickle.dump(texts, f)
        print("[OK] Cache saved.")
    except Exception as e:
        print(f"[ERROR] Could not save cache: {e}")

    return texts, index, pdf_files
