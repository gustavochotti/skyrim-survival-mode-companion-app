# app/scroll_picker.py

import tkinter as tk
import tkinter.font as tkfont
import customtkinter as ctk

class ScrollPicker(ctk.CTkToplevel):
    def __init__(self, master, values, title="Choose", initial="", width=420, height=480):
        super().__init__(master)
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.configure(fg_color=getattr(master, "BG_COLOR", "#1e1b18"))

        try:
            self.iconbitmap("media/skyrim_icon.ico")
        except Exception:
            pass

        self.transient(master)
        self.lift()
        self.attributes("-topmost", True)
        self.after(200, lambda: self.attributes("-topmost", False))
        self.grab_set()
        self.focus_force()

        self._all = list(values)
        self.result = None

        wrap = ctk.CTkFrame(self, fg_color=getattr(master, "FRAME_COLOR", "#3c322a"))
        wrap.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            wrap, text=title,
            text_color=getattr(master, "TEXT_COLOR", "#e0dcd1"),
            font=("Georgia", 18, "bold")
        ).pack(anchor="w", padx=10, pady=(10, 6))

        self.entry = ctk.CTkEntry(wrap, placeholder_text="Type to filter…", font=("Georgia", 16))
        self.entry.pack(fill="x", padx=10, pady=(0, 10))
        if initial:
            self.entry.insert(0, initial)

        list_wrap = ctk.CTkFrame(wrap, fg_color=getattr(master, "FRAME_COLOR", "#3c322a"))
        list_wrap.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.lb = tk.Listbox(
            list_wrap, activestyle="none", highlightthickness=0,
            bg=getattr(master, "ENTRY_COLOR", "#2b2621"),
            fg=getattr(master, "TEXT_COLOR", "#e0dcd1"),
            selectbackground="#5a4a3a", selectforeground="#e0dcd1",
            font=tkfont.Font(family="Georgia", size=16)
        )
        self.lb.pack(side="left", fill="both", expand=True)

        sb = tk.Scrollbar(list_wrap, orient="vertical", command=self.lb.yview)
        sb.pack(side="right", fill="y")
        self.lb.configure(yscrollcommand=sb.set)

        self.lb.bind("<MouseWheel>", lambda e: self.lb.yview_scroll(-int(e.delta/120), "units"))
        self.lb.bind("<Button-4>",  lambda e: self.lb.yview_scroll(-1, "units"))
        self.lb.bind("<Button-5>",  lambda e: self.lb.yview_scroll(+1, "units"))

        self.entry.bind("<KeyRelease>", self._on_filter)
        self.entry.bind("<Return>", lambda e: self._accept())
        self.lb.bind("<Return>", lambda e: self._accept())
        self.lb.bind("<Escape>", lambda e: self._cancel())
        self.bind("<Escape>", lambda e: self._cancel())
        self.lb.bind("<Double-Button-1>", lambda e: self._accept())

        btns = ctk.CTkFrame(wrap, fg_color=getattr(master, "FRAME_COLOR", "#3c322a"))
        btns.pack(fill="x", padx=10, pady=(0, 10))
        ctk.CTkButton(btns, text="OK", width=100, command=self._accept, font=("Georgia", 16)).pack(side="right", padx=4)
        ctk.CTkButton(btns, text="Cancel", width=100, command=self._cancel, font=("Georgia", 16)).pack(side="right", padx=4)

        self._refill()
        if initial:
            try:
                idx = self._all.index(initial)
                self.lb.selection_set(idx)
                self.lb.see(idx)
            except ValueError:
                pass

    def _refill(self, data=None):
        data = self._all if data is None else data
        self.lb.delete(0, "end")
        for v in data:
            self.lb.insert("end", v)

    def _on_filter(self, _=None):
        q = self.entry.get().strip().lower()
        if not q:
            self._refill()
            return
        view = [v for v in self._all if q in v.lower()]
        self._refill(view)

    def _accept(self):
        sel = self.lb.curselection()
        if sel:
            self.result = self.lb.get(sel[0])
        self.destroy()

    def _cancel(self):
        self.result = None
        self.destroy()


class PickerButton(ctk.CTkFrame):
    def __init__(self, master, values, variable: tk.StringVar, width=240, text_when_empty="Select…"):
        super().__init__(master, fg_color="transparent")
        self.values = list(values)
        self.var = variable
        self.placeholder = text_when_empty or "Select…"
        self.btn = ctk.CTkButton(self, text=self.placeholder, width=width, command=self._open, font=("Georgia", 16))
        self.btn.pack()
        self.var.trace_add("write", lambda *_: self._sync_text())

    def _open(self):
        pick = ScrollPicker(self.winfo_toplevel(), self.values,
                            title="Choose", initial=self.var.get() or "")
        self.wait_window(pick)
        if pick.result:
            self.var.set(pick.result)
        self._sync_text()

    def _sync_text(self):
        txt = self.var.get() or self.placeholder
        self.btn.configure(text=txt)

    def set(self, value: str):
        self.var.set(value); self._sync_text()

    def get(self) -> str:
        return self.var.get()
