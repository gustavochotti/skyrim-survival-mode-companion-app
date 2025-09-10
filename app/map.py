# app/map.py

import os
import platform
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import customtkinter as ctk
from app.constants import CITIES, BG_COLOR, FRAME_COLOR, TEXT_COLOR

class MapWindowMixin:
    def open_map_window(self):
        map_path = "media/skyrim_full_map.png"
        if not os.path.exists(map_path):
            messagebox.showerror("Map not found", "File 'skyrim_full_map.png' was not found.")
            return

        win = ctk.CTkToplevel(self)
        win.title("Skyrim Map")
        win.geometry("1100x780")
        win.configure(fg_color=BG_COLOR)

        try:
            win.iconbitmap("media/skyrim_icon.ico")
        except Exception:
            pass

        toolbar = ctk.CTkFrame(win, fg_color=FRAME_COLOR, corner_radius=8)
        toolbar.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew")

        ctk.CTkLabel(
            toolbar, text="Skyrim Map", text_color=TEXT_COLOR,
            font=("Georgia", 16, "bold")
        ).grid(row=0, column=0, padx=(10, 8), pady=8)

        ctk.CTkButton(toolbar, text="−", width=36, command=lambda: self._map_zoom(step=0.9)).grid(row=0, column=1, padx=4)
        ctk.CTkButton(toolbar, text="+", width=36, command=lambda: self._map_zoom(step=1.1)).grid(row=0, column=2, padx=4)
        ctk.CTkButton(toolbar, text="Reset", command=self._map_reset_view).grid(row=0, column=3, padx=4)

        self._map_canvas = tk.Canvas(win, bg=BG_COLOR, highlightthickness=0)
        self._map_canvas.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        win.grid_rowconfigure(1, weight=1)
        win.grid_columnconfigure(0, weight=1)

        self._map_img_original = Image.open(map_path).convert("RGBA")
        self._map_scale = 1.0
        self._img_ofs_x = 10
        self._img_ofs_y = 10
        self._pan_start = None
        self._overlay_ids = []

        self._render_map(first_time=True)

        # bindings
        self._map_canvas.bind("<ButtonPress-1>", self._on_pan_start)
        self._map_canvas.bind("<B1-Motion>", self._on_pan_move)
        self._map_canvas.bind("<MouseWheel>", self._on_wheel_zoom)
        self._map_canvas.bind("<Button-4>", lambda e: self._wheel_zoom_generic(e, 1))
        self._map_canvas.bind("<Button-5>", lambda e: self._wheel_zoom_generic(e, -1))

        # IMPORTANT: mostrar primeiro (traz pra frente) e só depois maximizar
        self._show_toplevel(win)
        self._maximize_toplevel(win)

    def _render_map(self, first_time=False):
        ow, oh = self._map_img_original.size
        disp_w = max(1, int(ow * self._map_scale))
        disp_h = max(1, int(oh * self._map_scale))
        self._map_img_display = self._map_img_original.resize((disp_w, disp_h), Image.LANCZOS)
        self._map_tk = ImageTk.PhotoImage(self._map_img_display)

        if first_time:
            self._img_id = self._map_canvas.create_image(
                self._img_ofs_x, self._img_ofs_y, image=self._map_tk, anchor="nw"
            )
        else:
            self._map_canvas.itemconfig(self._img_id, image=self._map_tk)
        self._map_canvas.coords(self._img_id, self._img_ofs_x, self._img_ofs_y)
        self._redraw_city_markers()

    def _redraw_city_markers(self):
        for iid in getattr(self, "_overlay_ids", []):
            try:
                self._map_canvas.delete(iid)
            except Exception:
                pass
        self._overlay_ids = []
        r = 5
        for name, (xi, yi) in CITIES.items():
            x = self._img_ofs_x + xi * self._map_scale
            y = self._img_ofs_y + yi * self._map_scale
            dot = self._map_canvas.create_oval(
                x - r, y - r, x + r, y + r, fill="#e74c3c", outline="#111111", width=1
            )
            self._overlay_ids.append(dot)
            label = self._map_canvas.create_text(
                x + 10, y - 8, text=name, fill="#e0dcd1", font=("Georgia", 11), anchor="w"
            )
            self._overlay_ids.append(label)

    def _on_pan_start(self, event):
        self._pan_start = (event.x, event.y)

    def _on_pan_move(self, event):
        if self._pan_start is None:
            return
        dx = event.x - self._pan_start[0]
        dy = event.y - self._pan_start[1]
        self._pan_start = (event.x, event.y)
        self._map_canvas.move(self._img_id, dx, dy)
        self._img_ofs_x, self._img_ofs_y = self._map_canvas.coords(self._img_id)
        for iid in self._overlay_ids:
            self._map_canvas.move(iid, dx, dy)

    def _on_wheel_zoom(self, event):
        self._wheel_zoom_generic(event, 1 if event.delta > 0 else -1)

    def _wheel_zoom_generic(self, event, direction):
        cx = self._map_canvas.canvasx(event.x)
        cy = self._map_canvas.canvasy(event.y)
        factor = 1.1 if direction > 0 else 0.9
        self._map_zoom(step=factor, focus=(cx, cy))

    def _map_zoom(self, step=1.1, focus=None):
        prev = self._map_scale
        new_scale = max(0.2, min(4.0, prev * step))
        if abs(new_scale - prev) < 1e-6:
            return
        if focus is None:
            w = self._map_canvas.winfo_width()
            h = self._map_canvas.winfo_height()
            focus = (w / 2, h / 2)
        fx, fy = focus
        ox, oy = self._map_canvas.coords(self._img_id)
        ow, oh = self._map_img_original.size
        old_w = ow * prev
        old_h = oh * prev
        new_w = ow * new_scale
        new_h = oh * new_scale
        relx = (fx - ox) / max(1, old_w)
        rely = (fy - oy) / max(1, old_h)
        self._img_ofs_x = fx - relx * new_w
        self._img_ofs_y = fy - rely * new_h
        self._map_scale = new_scale
        self._render_map(first_time=False)

    def _map_reset_view(self):
        self._map_scale = 1.0
        self._img_ofs_x = 10
        self._img_ofs_y = 10
        self._render_map(first_time=False)

    def _maximize_toplevel(self, win):
        system = platform.system()
        if system == "Windows":
            try:
                win.state("zoomed"); return
            except tk.TclError:
                pass
        try:
            win.attributes("-zoomed", True); return
        except tk.TclError:
            pass
        win.update_idletasks()
        w, h = win.winfo_screenwidth(), win.winfo_screenheight()
        win.geometry(f"{w}x{h}+0+0")

    def _show_toplevel(self, win):
        """Garante que o Toplevel abre na frente e com foco."""
        try:
            # Preparar e trazer à frente de forma confiável em todas as plataformas
            win.withdraw()
            win.update_idletasks()
            win.transient(self)          # associa ao parent
            win.deiconify()
            win.lift()
            win.attributes("-topmost", True)
            # Desliga o topmost após um 'tick' para não incomodar o usuário
            win.after(200, lambda: win.attributes("-topmost", False))
            win.focus_force()
            try:
                win.wait_visibility()
            except Exception:
                pass
            win.focus_set()
        except Exception:
            pass
