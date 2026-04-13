import customtkinter as ctk
from tkinter import messagebox
from database import add_recipe, update_recipe, get_recipe_by_id, get_easy_ingredients, add_easy_ingredient, delete_easy_ingredient
from models import Recipe
import json

class AddEditRecipeDialog(ctk.CTkToplevel):
    def __init__(self, parent, recipe_id=None):
        super().__init__(parent)
        self.recipe_id = recipe_id
        self.title("Редактирование рецепта" if recipe_id else "Новый рецепт")
        self.geometry("500x600")
        self.resizable(False, False)

        self.name_var = ctk.StringVar()
        self.output_var = ctk.StringVar()
        self.ingredients = {}  # name -> amount

        # Название
        ctk.CTkLabel(self, text="Название:").pack(pady=(10,0), anchor="w", padx=10)
        self.name_entry = ctk.CTkEntry(self, textvariable=self.name_var, width=400)
        self.name_entry.pack(pady=5, padx=10)

        # Выход за крафт
        ctk.CTkLabel(self, text="Выход за крафт (количество штук):").pack(pady=(10,0), anchor="w", padx=10)
        self.output_entry = ctk.CTkEntry(self, textvariable=self.output_var, width=200)
        self.output_entry.pack(pady=5, padx=10)

        # Ингредиенты
        ctk.CTkLabel(self, text="Ингредиенты (название и количество):").pack(pady=(10,0), anchor="w", padx=10)
        self.ingredients_frame = ctk.CTkScrollableFrame(self, height=300)
        self.ingredients_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Кнопка добавить ингредиент
        ctk.CTkButton(self, text="➕ Добавить ингредиент", command=self.add_ingredient_row).pack(pady=5)

        # Кнопки сохранить/отмена
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=10)
        ctk.CTkButton(btn_frame, text="Сохранить", command=self.save).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Отмена", command=self.destroy).pack(side="left", padx=5)

        if recipe_id:
            self.load_recipe()

        self.ingredient_rows = []
        self.update_ingredients_ui()

    def load_recipe(self):
        recipe = get_recipe_by_id(self.recipe_id)
        if recipe:
            self.name_var.set(recipe.name)
            self.output_var.set(str(recipe.output_amount))
            self.ingredients = recipe.ingredients.copy()
            self.update_ingredients_ui()

    def add_ingredient_row(self, name="", amount=""):
        row_frame = ctk.CTkFrame(self.ingredients_frame)
        row_frame.pack(fill="x", padx=5, pady=2)
        name_entry = ctk.CTkEntry(row_frame, width=200)
        name_entry.insert(0, name)
        name_entry.pack(side="left", padx=2)
        amount_entry = ctk.CTkEntry(row_frame, width=100)
        amount_entry.insert(0, str(amount))
        amount_entry.pack(side="left", padx=2)
        del_btn = ctk.CTkButton(row_frame, text="❌", width=30, command=lambda: self.remove_ingredient_row(row_frame, name_entry, amount_entry))
        del_btn.pack(side="left", padx=2)
        self.ingredient_rows.append((row_frame, name_entry, amount_entry))

    def remove_ingredient_row(self, frame, name_entry, amount_entry):
        # удалить из UI и из self.ingredients
        name = name_entry.get().strip().lower()
        if name in self.ingredients:
            del self.ingredients[name]
        frame.destroy()
        self.ingredient_rows = [r for r in self.ingredient_rows if r[0] != frame]

    def update_ingredients_ui(self):
        # очистить все строки
        for row in self.ingredient_rows:
            row[0].destroy()
        self.ingredient_rows.clear()
        for name, amount in self.ingredients.items():
            self.add_ingredient_row(name, amount)

    def save(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror("Ошибка", "Введите название.")
            return
        try:
            output = int(self.output_var.get().strip())
            if output <= 0:
                raise ValueError
        except:
            messagebox.showerror("Ошибка", "Введите положительное число для выхода.")
            return
        # собрать ингредиенты из полей
        new_ingredients = {}
        for _, name_entry, amount_entry in self.ingredient_rows:
            ing_name = name_entry.get().strip().lower()
            if not ing_name:
                continue
            try:
                ing_amount = int(amount_entry.get().strip())
                if ing_amount <= 0:
                    continue
                new_ingredients[ing_name] = ing_amount
            except:
                pass
        if not new_ingredients:
            messagebox.showerror("Ошибка", "Добавьте хотя бы один ингредиент.")
            return
        recipe = Recipe(id=self.recipe_id or 0, name=name, output_amount=output, ingredients=new_ingredients)
        if self.recipe_id:
            update_recipe(recipe)
        else:
            add_recipe(recipe)
        self.destroy()


class EasyIngredientsDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Легкодоступные ингредиенты")
        self.geometry("400x500")
        self.ingredients = get_easy_ingredients()

        self.listbox = ctk.CTkTextbox(self, height=300)
        self.listbox.pack(fill="both", expand=True, padx=10, pady=10)
        self.update_list()

        # Добавление
        frame = ctk.CTkFrame(self)
        frame.pack(fill="x", padx=10, pady=5)
        self.new_name = ctk.CTkEntry(frame, width=200)
        self.new_name.pack(side="left", padx=5)
        ctk.CTkButton(frame, text="Добавить", command=self.add_ingredient).pack(side="left", padx=5)

        # Удаление выбранного
        ctk.CTkButton(self, text="Удалить выбранный", command=self.delete_selected).pack(pady=5)

    def update_list(self):
        self.ingredients = get_easy_ingredients()
        self.listbox.configure(state="normal")
        self.listbox.delete("1.0", "end")
        for ing in self.ingredients:
            self.listbox.insert("end", ing + "\n")
        self.listbox.configure(state="disabled")

    def add_ingredient(self):
        name = self.new_name.get().strip().lower()
        if name:
            add_easy_ingredient(name)
            self.new_name.delete(0, "end")
            self.update_list()

    def delete_selected(self):
        try:
            index = self.listbox.index("@%d,%d" % (self.listbox.winfo_pointerx() - self.listbox.winfo_rootx(),
                                                   self.listbox.winfo_pointery() - self.listbox.winfo_rooty()))
            line = self.listbox.get(f"{index} linestart", f"{index} lineend")
            name = line.strip()
            if name:
                delete_easy_ingredient(name)
                self.update_list()
        except:
            pass