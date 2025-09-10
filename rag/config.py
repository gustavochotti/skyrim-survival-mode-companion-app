# rag/config.py

import os
import google.generativeai as genai

# Caminho do arquivo com a chave da API
API_KEY_PATH = "secrets/API_KEY.txt"

# Modelos Gemini
EMBED_MODEL = "models/embedding-001"
GEN_MODEL = "models/gemini-2.5-pro"

# Função para carregar a chave da API e configurar a lib
def configure_gemini():
    try:
        if os.path.exists(API_KEY_PATH):
            with open(API_KEY_PATH, "r") as file:
                key = file.read().strip()
                genai.configure(api_key=key)
                print("[OK] Gemini API key loaded and configured.")
                return key
        else:
            print(f"[WARNING] API key file not found: {API_KEY_PATH}")
    except Exception as e:
        print(f"[ERROR] Failed to configure Gemini: {e}")
    return None
