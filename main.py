# main.py

import customtkinter as ctk
from app.ui import SkyrimAssistantApp
from rag.pipeline import setup_rag_pipeline

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def main():
    print("[INFO] Preparing Skyrim Survival Mode Assistant...")
    texts, index, _ = setup_rag_pipeline()

    if index is None:
        print("\n[CRITICAL] Knowledge base failed to load.")
        print("Check that you have:")
        print("  - API key in 'secrets/API_KEY.txt'")
        print("  - At least one PDF in the 'files/' folder")
        input("\nPress Enter to close...")
        return

    print("[INFO] Launching App...")
    app = SkyrimAssistantApp((texts, index))
    app.mainloop()
    print("[INFO] App closed.")

if __name__ == "__main__":
    main()
