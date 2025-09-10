# app/ui.py

import os
import platform
import random
import tkinter as tk
from threading import Thread
from tkinter import messagebox

import customtkinter as ctk
from PIL import Image, ImageTk

from app.constants import *
from app.map import MapWindowMixin
from app.alchemy import AlchemyMixin
from app.scroll_picker import ScrollPicker, PickerButton
from data.advice import MAGE_ADVICE
from rag.pipeline import search_relevant_context, generate_response


class SkyrimAssistantApp(ctk.CTk, MapWindowMixin, AlchemyMixin):
    def __init__(self, rag_pipeline):
        super().__init__()
        self.rag_pipeline = rag_pipeline  # (texts, index)

        self.title("Skyrim Survival Mode Companion")
        self.geometry("1280x720")
        self._maximize_window()

        try:
            app_icon_path = "media/skyrim_icon.ico"
            if os.path.exists(app_icon_path):
                self.iconbitmap(app_icon_path)
        except Exception as e:
            print(f"[ERROR] Could not load icon: {e}")

        self.BG_COLOR = BG_COLOR
        self.FRAME_COLOR = FRAME_COLOR
        self.TEXT_COLOR = TEXT_COLOR
        self.BUTTON_COLOR = BUTTON_COLOR
        self.BUTTON_HOVER = BUTTON_HOVER
        self.ENTRY_COLOR = ENTRY_COLOR

        self.TITLE_FONT = TITLE_FONT
        self.BODY_FONT = BODY_FONT
        self.BUTTON_FONT = BUTTON_FONT

        self.configure(fg_color=self.BG_COLOR)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(
            self, text="Skyrim Survival Mode Companion",
            font=self.TITLE_FONT, text_color=self.TEXT_COLOR
        ).grid(row=0, column=0, padx=20, pady=(16, 8), sticky="ew")

        toolbar = ctk.CTkFrame(self, fg_color=self.FRAME_COLOR, corner_radius=10)
        toolbar.grid(row=1, column=0, padx=20, pady=(0, 8), sticky="ew")
        toolbar.grid_columnconfigure((0, 1, 2, 3), weight=0)
        toolbar.grid_columnconfigure(4, weight=1)

        ctk.CTkButton(toolbar, text="Open Map", command=self.open_map_window).grid(row=0, column=0, padx=6, pady=10)
        ctk.CTkButton(toolbar, text="Potion Calculator", command=self.open_alchemy_calc).grid(row=0, column=1, padx=6)
        ctk.CTkButton(toolbar, text="Ingredient Advisor", command=self.open_ingredient_advisor).grid(row=0, column=2, padx=6)
        ctk.CTkButton(toolbar, text="Random Mage Advice", command=self.show_random_advice).grid(row=0, column=3, padx=6)

        self.main_frame = ctk.CTkFrame(self, fg_color=self.FRAME_COLOR, corner_radius=10)
        self.main_frame.grid(row=2, column=0, padx=20, pady=(0, 16), sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

        self.response_textbox = ctk.CTkTextbox(
            self.main_frame, wrap="word",
            font=self.BODY_FONT,
            fg_color=self.ENTRY_COLOR,
            text_color=self.TEXT_COLOR,
            border_color=self.BUTTON_COLOR,
            border_width=2,
            corner_radius=6
        )
        self.response_textbox.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        self._set_response("Greetings, Dovahkiin. What do the cold winds of Skyrim whisper to your mind?")

        bottom = ctk.CTkFrame(self.main_frame, fg_color=self.FRAME_COLOR)
        bottom.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="ew")
        bottom.grid_columnconfigure(0, weight=1)

        self.user_input = ctk.CTkEntry(
            bottom, placeholder_text="Type your question or scenario here...",
            font=self.BODY_FONT, fg_color=self.ENTRY_COLOR, text_color=self.TEXT_COLOR,
            border_color=self.BUTTON_COLOR, border_width=2, corner_radius=6
        )
        self.user_input.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        self.user_input.bind("<Return>", self.handle_ask_button)

        self.ask_button = ctk.CTkButton(
            bottom, text="Ask the Mage", font=self.BUTTON_FONT,
            fg_color=self.BUTTON_COLOR, hover_color=self.BUTTON_HOVER,
            command=self.handle_ask_button
        )
        self.ask_button.grid(row=0, column=1)

    def _set_response(self, text):
        self.response_textbox.configure(state="normal")
        self.response_textbox.delete("1.0", "end")
        self.response_textbox.insert("1.0", text)
        self.response_textbox.configure(state="disabled")

    def handle_ask_button(self, event=None):
        query = self.user_input.get()
        if not query.strip() or self.ask_button.cget("state") == "disabled":
            return
        self.user_input.delete(0, "end")
        self._set_response(f"Dovahkiin: {query}\n\nThe Mage consults the ancient scrolls...")
        self.ask_button.configure(state="disabled", text="Consulting...")
        Thread(target=self.run_rag_pipeline, args=(query,)).start()

    def run_rag_pipeline(self, query):
        texts, index = self.rag_pipeline
        context = search_relevant_context(query, index, texts, top_k=5, use_cosine=True)
        answer = generate_response(query, context)
        self.after(0, self.update_ui_with_response, answer)

    def update_ui_with_response(self, answer):
        self._set_response(answer)
        self.ask_button.configure(state="normal", text="Ask the Mage")

    def show_random_advice(self):
        advice = random.choice(MAGE_ADVICE)
        self._set_response(f"🧙 {advice}")

    def _maximize_window(self):
        system = platform.system()
        if system == "Windows":
            try:
                self.state("zoomed"); return
            except tk.TclError: pass
        try:
            self.attributes("-zoomed", True); return
        except tk.TclError: pass
        self.update_idletasks()
        w, h = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{w}x{h}+0+0")
