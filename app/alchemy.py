# app/alchemy.py

import tkinter as tk
import customtkinter as ctk
from app.scroll_picker import PickerButton
from data.ingredients import INGREDIENTS, ALL_EFFECTS, EFFECT_TO_INGREDIENTS
from itertools import combinations

class AlchemyMixin:
    def open_alchemy_calc(self):
        win = ctk.CTkToplevel(self)
        win.title("Potion Calculator")
        win.geometry("820x520")
        win.configure(fg_color=self.BG_COLOR)
        try:
            win.iconbitmap("media/skyrim_icon.ico")
        except Exception:
            pass

        self._show_toplevel(win)

        top = ctk.CTkFrame(win, fg_color=self.FRAME_COLOR, corner_radius=10)
        top.pack(fill="x", padx=12, pady=12)

        ctk.CTkLabel(top, text="Pick up to three ingredients:",
                     text_color=self.TEXT_COLOR, font=("Georgia", 16, "bold")
                     ).pack(anchor="w", padx=10, pady=(10, 4))

        opts = sorted(INGREDIENTS.keys())
        var1, var2, var3 = tk.StringVar(), tk.StringVar(), tk.StringVar()
        row = ctk.CTkFrame(top, fg_color=self.FRAME_COLOR); row.pack(fill="x", padx=10, pady=6)

        pick1 = PickerButton(row, opts, var1, width=240, text_when_empty="Ingredient 1")
        pick2 = PickerButton(row, opts, var2, width=240, text_when_empty="Ingredient 2")
        pick3 = PickerButton(row, opts, var3, width=240, text_when_empty="Ingredient 3")
        pick1.grid(row=0, column=0, padx=6, pady=6)
        pick2.grid(row=0, column=1, padx=6, pady=6)
        pick3.grid(row=0, column=2, padx=6, pady=6)

        out = ctk.CTkTextbox(win, wrap="word", fg_color=self.ENTRY_COLOR, text_color=self.TEXT_COLOR)
        out.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        def calc():
            picks = [v.get() for v in (var1, var2, var3) if v.get()]
            fx = shared_effects(picks)
            out.configure(state="normal"); out.delete("1.0", "end")
            if not picks:
                out.insert("1.0", "Choose at least two ingredients to see shared effects.")
            else:
                out.insert("1.0", f"Ingredients: {', '.join(picks)}\n\n")
                if fx:
                    out.insert("end", "Shared effects:\n")
                    for e in fx: out.insert("end", f" • {e}\n")
                else:
                    out.insert("end", "No shared effects between selected ingredients.")
            out.configure(state="disabled")

        ctk.CTkButton(top, text="Calculate", command=calc).pack(pady=(0, 10))
        calc()

    def open_ingredient_advisor(self):
        win = ctk.CTkToplevel(self)
        win.title("Ingredient Advisor")
        win.geometry("980x600")
        win.configure(fg_color=self.BG_COLOR)
        try:
            win.iconbitmap("media/skyrim_icon.ico")
        except Exception:
            pass

        self._show_toplevel(win)

        tabs = ctk.CTkTabview(win, fg_color=self.FRAME_COLOR)
        tabs.pack(fill="both", expand=True, padx=12, pady=12)
        t1 = tabs.add("By Effect"); t2 = tabs.add("By Inventory")

        ctk.CTkLabel(t1, text="Choose desired effect:", text_color=self.TEXT_COLOR,
                     font=("Georgia", 15, "bold")).pack(anchor="w", padx=10, pady=(10, 6))
        eff_var = tk.StringVar(value=ALL_EFFECTS[0] if ALL_EFFECTS else "")
        eff_pick = PickerButton(t1, ALL_EFFECTS, eff_var, width=320, text_when_empty="Select an effect…")
        eff_pick.pack(anchor="w", padx=10, pady=(0, 10))

        out1 = ctk.CTkTextbox(t1, wrap="word", fg_color=self.ENTRY_COLOR, text_color=self.TEXT_COLOR)
        out1.pack(fill="both", expand=True, padx=10, pady=(0, 12))

        def run_by_effect():
            effect = eff_var.get()
            recs = recipes_for_effect(effect)
            out1.configure(state="normal"); out1.delete("1.0", "end")
            out1.insert("1.0", f"Recipes for effect: {effect}\n\n")
            if not recs:
                out1.insert("end", "No recipes found in the current ingredient database.")
            else:
                for r in recs:
                    out1.insert("end", " • " + " + ".join(r) + "\n")
            out1.configure(state="disabled")

        ctk.CTkButton(t1, text="Find Recipes", command=run_by_effect).pack(pady=(0, 10))
        run_by_effect()

        ctk.CTkLabel(t2, text="List your ingredients (comma separated):",
                     text_color=self.TEXT_COLOR, font=("Georgia", 15, "bold")).pack(anchor="w", padx=10, pady=(10, 6))
        inv_entry = ctk.CTkEntry(t2)
        inv_entry.pack(fill="x", padx=10, pady=(0, 8))
        inv_entry.insert(0, "Blue Mountain Flower, Wheat, Snowberries, Garlic")
        out2 = ctk.CTkTextbox(t2, wrap="word", fg_color=self.ENTRY_COLOR, text_color=self.TEXT_COLOR)
        out2.pack(fill="both", expand=True, padx=10, pady=(0, 12))

        def run_by_inventory():
            raw = inv_entry.get()
            inventory = [x.strip() for x in raw.split(",")]
            result = recommend_from_inventory(inventory)
            out2.configure(state="normal"); out2.delete("1.0", "end")
            if not result:
                out2.insert("1.0", "No craftable effects with the provided inventory (or unknown names).")
            else:
                for eff, recs in result.items():
                    out2.insert("end", f"\nEffect: {eff}\n")
                    for r in recs:
                        out2.insert("end", "  • " + " + ".join(r) + "\n")
            out2.configure(state="disabled")

        ctk.CTkButton(t2, text="Recommend", command=run_by_inventory).pack(pady=(0, 10))
        run_by_inventory()

# Pure logic helpers (can be reused or moved to a utils.py)
def shared_effects(ingredients):
    if not ingredients:
        return []
    effect_counts = {}
    for ing in ingredients:
        for eff in INGREDIENTS.get(ing, []):
            effect_counts[eff] = effect_counts.get(eff, 0) + 1
    return sorted([e for e, c in effect_counts.items() if c >= 2])

def recipes_for_effect(effect, max_results=60):
    pool = EFFECT_TO_INGREDIENTS.get(effect, [])
    if len(pool) < 2:
        return []

    results = []
    for r in combinations(pool, 2):
        results.append(tuple(sorted(r)))

    if len(pool) >= 3:
        for r in combinations(pool, 3):
            shared = shared_effects(list(r))
            if effect in shared:
                results.append(tuple(sorted(r)))

    results.sort(key=lambda r: (len(r), r))
    unique_results = sorted(list(set(results)), key=lambda r: (len(r), r))
    return unique_results[:max_results]

def recommend_from_inventory(inventory, max_results=40):
    inv = [i.strip() for i in inventory if i.strip() in INGREDIENTS]
    if not inv:
        return {}
    effect_counts = {}
    for ing in inv:
        for eff in INGREDIENTS[ing]:
            effect_counts[eff] = effect_counts.get(eff, 0) + 1
    craftable = {e for e, c in effect_counts.items() if c >= 2}

    recipes = {}
    for eff in sorted(craftable):
        rs = []
        for i in range(len(inv)):
            for j in range(i + 1, len(inv)):
                a, b = inv[i], inv[j]
                if eff in set(INGREDIENTS[a]).intersection(INGREDIENTS[b]):
                    rs.append((a, b))
        for i in range(len(inv)):
            for j in range(i + 1, len(inv)):
                for k in range(j + 1, len(inv)):
                    a, b, c = inv[i], inv[j], inv[k]
                    if eff in set(INGREDIENTS[a]).intersection(INGREDIENTS[b], INGREDIENTS[c]):
                        rs.append((a, b, c))
        if rs:
            recipes[eff] = sorted(rs, key=lambda r: (len(r), r))[:max_results]
    return recipes
