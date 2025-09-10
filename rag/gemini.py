# rag/gemini.py

from rag.config import GEN_MODEL
import google.generativeai as genai

def generate_response(query, context):
    system = (
        "You are a wise old mage from High Hrothgar, offering help in Skyrim Survival Mode.\n"
        "Respond only with the CONTEXT. Never invent information.\n"
        "If no answer exists in the context, say so.\n"
        "For travel, suggest both walking and carriage routes.\n"
        "Keep answers short and immersive."
    )
    prompt = (
        f"{system}\n\n"
        f"CONTEXT:\n{context}\n\n"
        f"PLAYER'S QUESTION:\n\"{query}\"\n\n"
        f"Your answer (short, direct, immersive):"
        )

    try:
        model = genai.GenerativeModel(GEN_MODEL)
        resp = model.generate_content(prompt)
        text = getattr(resp, "text", "") or ""
        text = text.strip()
        for c in ["*", "#", "_"]:
            text = text.replace(c, "")
        return text or "The scrolls revealed nothing clear this time."
    except Exception as e:
        print(f"[ERROR] Gemini generation: {e}")
        return "The cold winds of Skyrim seem to interfere with my magic. Try again."
