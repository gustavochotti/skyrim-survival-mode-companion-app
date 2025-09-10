# 🧙 Skyrim Survival Mode Assistant

A desktop application that helps you survive the cold lands of Skyrim.  
It works like a wise old mage from High Hrothgar, guiding you with knowledge, potion recipes, travel advice, and a beautiful interactive map.

This app uses **Gemini AI** to read Skyrim guides in PDF format and answer your questions — but you are always in control of what it knows, because you provide (and can add more) PDFs.

---

## ✨ Features

- 📚 **Ask Your Guides (RAG)**  
  The app already comes with **preloaded Skyrim PDF guides** so it works right away.  
  You can also add your own PDF guides into the `files/` folder to expand or customize the mage’s knowledge.

- 🗺 **Interactive Map**  
  Explore Skyrim with zoom, pan, and city markers.

- ⚗ **Potion Calculator**  
  Pick 2–3 ingredients and instantly see which effects they share.

- 🌿 **Ingredient Advisor**  
  - Search by effect: "Show me all recipes for Restore Health."  
  - Search by inventory: "Here are my ingredients, what can I craft?"

- 🧙 **Random Mage Advice**  
  Get immersive roleplay tips for traveling and surviving.

---

## 🎥 Demo

![App Demo Gif](ssmc_demo.gif)

---

## 📂 Project Structure

```
SkyrimAssistant/
├── main.py                # Start the app
├── requirements.txt       # All dependencies
├── cache/                 # Auto-created cache files (no need to touch)
├── files/                 # ← Contains preloaded PDFs + your own if you add more
├── secrets/
│   └── API_KEY.txt        # ← Your Gemini API key goes here
├── media/
│   ├── skyrim_full_map.png
│   └── skyrim_icon.ico
├── data/
│   ├── advice.py          # Mage’s immersive quotes
│   └── ingredients.py     # Ingredient database
├── app/
│   ├── __init__.py
│   ├── constants.py
│   ├── ui.py
│   ├── map.py
│   ├── alchemy.py
│   └── scroll_picker.py
└── rag/
    ├── __init__.py
    ├── config.py
    ├── gemini.py
    └── pipeline.py
```

---

## ⚙️ Installation (Step by Step)

### Option 1 – Run from Source (for advanced users)

1. **Install Python 3.10+**  
   Download and install from [python.org](https://www.python.org/downloads/).

2. **Install dependencies**  
   Open a terminal inside the project folder and run:

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your Gemini API key**  
   - Create a free Gemini API key from:  
     👉 [Google AI Studio](https://aistudio.google.com/app/apikey)
   - Create a folder called `secrets/` inside the project (if it does not exist).
   - Inside `secrets/`, create a file named `API_KEY.txt`
   - Paste your API key inside this file (just the key, nothing else).

   Example:

   ```
   secrets/
   └── API_KEY.txt   ← contains: AIzaSy... (your Gemini API key)
   ```

4. **Run the application**  

   ```bash
   python main.py
   ```

---

### Option 2 – Download Ready-to-Use Executable (Recommended)

For non-technical users, you don’t need Python or installations.  
Simply download the executable, place your **Gemini API key** in the correct path, and run the program.

👉 **[Download the latest release here](https://drive.google.com/file/d/1TG3t8nQDHJTXJ6Or_xxV28GRrBfuezAo/view?usp=sharing)**

Steps:

1. Download and extract the program from the link above.  
2. Go to the `secrets/` folder and open `API_KEY.txt`.  
   - If it doesn’t exist, create it.  
   - Paste your Gemini API key inside (just the key).  
3. Double-click the program executable (`SkyrimAssistant.exe`).  
4. Start using the mage immediately!  

---

## 🖥 Usage

- **Ask the Mage**: type a question in the box and press Enter or "Ask the Mage".  
- **Map**: click "Open Map" to explore Skyrim with zoom and pan.  
- **Potion Calculator**: choose up to three ingredients to see shared effects.  
- **Ingredient Advisor**: search by effect or enter your inventory.  
- **Random Advice**: click the button for immersive roleplay tips.

---

## 🛠 Troubleshooting

- **The app says it cannot load the knowledge base**  
  - Make sure `secrets/API_KEY.txt` exists and contains your Gemini API key.  
  - Make sure there are PDFs in `files/` (some are already included by default).

- **Cache issues**  
  - If you add/remove PDFs, delete the `cache/` folder.  
    The app will rebuild the knowledge base automatically.

---

## 📌 Requirements (for source version)

- Python 3.10 or newer
- Internet connection (for Gemini API)
- Dependencies (install with `pip install -r requirements.txt`):
  - `customtkinter`
  - `pymupdf`
  - `faiss-cpu`
  - `numpy`
  - `Pillow`
  - `google-generativeai`

---

## 🧾 License

This project is for personal/educational use.  
Skyrim and all related content are © Bethesda Softworks.
