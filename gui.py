import customtkinter as ctk
from tkinter import messagebox
from database import (
    get_all_recipes, delete_recipe, get_recipe_by_id,
    get_easy_ingredients, add_easy_ingredient, delete_easy_ingredient
)
from dialogs import AddEditRecipeDialog, EasyIngredientsDialog
from calculator import expand_recipe, max_crafts_by_ingredient
from models import Recipe

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class CraftApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Крафт-помощник")
        self.geometry("1100x700")
        self.minsize(1000, 600)

        # Данные
        self.recipes = []               # список всех рецептов
        self.selected_recipe = None     # объект Recipe
        self.recipe_name_to_id = {}     # маппинг для быстрого поиска

        # Основной контейнер: левая панель (список + управление) и правая панель
        self.main_container = ctk.CTkFrame(self)
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Левая панель
        self.left_frame = ctk.CTkFrame(self.main_container, width=350)
        self.left_frame.pack(side="left", fill="both", expand=False, padx=(0, 10))

        # Правая панель
        self.right_frame = ctk.CTkFrame(self.main_container)
        self.right_frame.pack(side="right", fill="both", expand=True)

        # --- Левая панель: список рецептов ---
        self.recipe_listbox = ctk.CTkTextbox(self.left_frame, height=250, state="normal")
        self.recipe_listbox.pack(fill="x", padx=10, pady=(10, 5))
        self.recipe_listbox.configure(state="disabled")

        # Кнопки управления рецептами
        btn_frame = ctk.CTkFrame(self.left_frame)
        btn_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkButton(btn_frame, text="➕ Добавить", command=self.add_recipe).pack(side="left", padx=2, expand=True, fill="x")
        ctk.CTkButton(btn_frame, text="✏️ Ред.", command=self.edit_recipe).pack(side="left", padx=2, expand=True, fill="x")
        ctk.CTkButton(btn_frame, text="🗑 Удалить", command=self.delete_recipe).pack(side="left", padx=2, expand=True, fill="x")

        btn_frame2 = ctk.CTkFrame(self.left_frame)
        btn_frame2.pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(btn_frame2, text="📋 Легкодоступные", command=self.manage_easy).pack(side="left", padx=2, expand=True, fill="x")
        ctk.CTkButton(btn_frame2, text="🔄 Обновить", command=self.load_recipes).pack(side="left", padx=2, expand=True, fill="x")

        # --- Левая панель: управление расчётом ---
        calc_frame = ctk.CTkFrame(self.left_frame)
        calc_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(calc_frame, text="Расчёт по ингредиенту:", anchor="w").pack(fill="x", padx=5, pady=(5,0))
        self.ingredient_combo = ctk.CTkComboBox(calc_frame, values=["Выберите рецепт"], state="readonly")
        self.ingredient_combo.pack(fill="x", padx=5, pady=2)

        ctk.CTkLabel(calc_frame, text="Количество ингредиента:", anchor="w").pack(fill="x", padx=5, pady=(5,0))
        self.ingredient_amount_entry = ctk.CTkEntry(calc_frame)
        self.ingredient_amount_entry.pack(fill="x", padx=5, pady=2)

        ctk.CTkLabel(calc_frame, text="ИЛИ необходимо порций:", anchor="w").pack(fill="x", padx=5, pady=(10,0))
        self.servings_entry = ctk.CTkEntry(calc_frame)
        self.servings_entry.pack(fill="x", padx=5, pady=2)

        ctk.CTkButton(calc_frame, text="🔨 Рассчитать", command=self.calculate).pack(fill="x", padx=5, pady=10)

        # --- Правая панель: информация о рецепте ---
        self.info_frame = ctk.CTkFrame(self.right_frame)
        self.info_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.recipe_title = ctk.CTkLabel(self.info_frame, text="Выберите рецепт", font=ctk.CTkFont(size=18, weight="bold"))
        self.recipe_title.pack(anchor="w", padx=10, pady=(10,5))

        self.recipe_output = ctk.CTkLabel(self.info_frame, text="", font=ctk.CTkFont(size=14))
        self.recipe_output.pack(anchor="w", padx=10, pady=2)

        ctk.CTkLabel(self.info_frame, text="Ингредиенты:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10,0))
        self.ingredients_text = ctk.CTkTextbox(self.info_frame, height=120, state="disabled")
        self.ingredients_text.pack(fill="x", padx=10, pady=5)

        # --- Правая панель: результаты расчёта ---
        ctk.CTkLabel(self.info_frame, text="Результат расчёта:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10,0))
        self.result_text = ctk.CTkTextbox(self.info_frame, height=200)
        self.result_text.pack(fill="both", expand=True, padx=10, pady=5)

        # Привязка событий
        self.recipe_listbox.bind("<ButtonRelease-1>", self.on_recipe_select)

        # Загрузка данных
        self.load_recipes()

    def load_recipes(self):
        """Загружает список рецептов и обновляет интерфейс."""
        self.recipes = get_all_recipes()
        self.recipe_name_to_id = {r.name: r.id for r in self.recipes}

        self.recipe_listbox.configure(state="normal")
        self.recipe_listbox.delete("1.0", "end")

        for r in self.recipes:
            self.recipe_listbox.insert("end", f"{r.name}\n")

        self.recipe_listbox.configure(state="disabled")

        # Если был выбран рецепт, которого больше нет, сбрасываем выделение
        if self.selected_recipe and self.selected_recipe.id not in [r.id for r in self.recipes]:
            self.selected_recipe = None
            self.clear_recipe_info()

    def on_recipe_select(self, event):
        """Обработчик выбора рецепта в списке."""
        try:
            index = self.recipe_listbox.index("@%d,%d" % (event.x, event.y))
            line = self.recipe_listbox.get(f"{index} linestart", f"{index} lineend")
            name = line.strip()
            if name and name in self.recipe_name_to_id:
                recipe_id = self.recipe_name_to_id[name]
                self.selected_recipe = get_recipe_by_id(recipe_id)
                self.update_recipe_info()
                self.highlight_selected_recipe(index)
            else:
                self.selected_recipe = None
                self.clear_recipe_info()
        except:
            pass

    def highlight_selected_recipe(self, index):
        """Визуально выделяет выбранную строку в списке."""
        self.recipe_listbox.tag_remove("selected", "1.0", "end")
        start = f"{index} linestart"
        end = f"{index} lineend"
        self.recipe_listbox.tag_add("selected", start, end)
        self.recipe_listbox.tag_config("selected", background="#3a7ebf", foreground="white")

    def clear_recipe_info(self):
        """Очищает правую панель информации о рецепте."""
        self.recipe_title.configure(text="Выберите рецепт")
        self.recipe_output.configure(text="")
        self.ingredients_text.configure(state="normal")
        self.ingredients_text.delete("1.0", "end")
        self.ingredients_text.configure(state="disabled")
        self.result_text.delete("1.0", "end")
        self.ingredient_combo.configure(values=["Выберите рецепт"])
        self.ingredient_combo.set("")

    def update_recipe_info(self):
        """Обновляет правую панель данными выбранного рецепта."""
        if not self.selected_recipe:
            return

        r = self.selected_recipe
        self.recipe_title.configure(text=r.name)
        self.recipe_output.configure(text=f"Выход за крафт: {r.output_amount} шт.")

        # Список ингредиентов
        ing_lines = []
        for ing, amt in r.ingredients.items():
            ing_lines.append(f"• {ing.capitalize()}: {amt}")
        ing_text = "\n".join(ing_lines)

        self.ingredients_text.configure(state="normal")
        self.ingredients_text.delete("1.0", "end")
        self.ingredients_text.insert("1.0", ing_text)
        self.ingredients_text.configure(state="disabled")

        # Заполняем выпадающий список ингредиентов (только базовые, не составные и не легкодоступные)
        easy = set(get_easy_ingredients())
        all_recipes_dict = {rec.name.lower(): rec for rec in self.recipes}
        available_ingredients = [
            ing for ing in r.ingredients.keys()
            if ing not in easy and ing not in all_recipes_dict
        ]
        if available_ingredients:
            self.ingredient_combo.configure(values=available_ingredients)
            self.ingredient_combo.set(available_ingredients[0])
        else:
            self.ingredient_combo.configure(values=["Нет подходящих"])
            self.ingredient_combo.set("")

        # Очищаем поля ввода и результат
        self.ingredient_amount_entry.delete(0, "end")
        self.servings_entry.delete(0, "end")
        self.result_text.delete("1.0", "end")

    def calculate(self):
        """Выполняет расчёт в зависимости от заполненных полей."""
        if not self.selected_recipe:
            messagebox.showwarning("Нет рецепта", "Сначала выберите рецепт.")
            return

        # Получаем значения из полей
        ing_name = self.ingredient_combo.get().strip().lower()
        ing_amount_str = self.ingredient_amount_entry.get().strip()
        servings_str = self.servings_entry.get().strip()

        # Определяем, какой расчёт выполнять (приоритет: ингредиент, если оба заполнены)
        if ing_name and ing_name != "нет подходящих" and ing_amount_str:
            self.calculate_by_ingredient(ing_name, ing_amount_str)
        elif servings_str:
            self.calculate_by_servings(servings_str)
        else:
            messagebox.showwarning("Нет данных", "Введите количество ингредиента или количество порций.")

    def calculate_by_ingredient(self, ing_name: str, amount_str: str):
        """Расчёт по наличию ингредиента."""
        try:
            amount = int(amount_str)
            if amount <= 0:
                raise ValueError
        except ValueError:
            self.result_text.insert("end", "❌ Ошибка: введите положительное число для количества ингредиента.\n")
            return

        all_recipes = {r.name.lower(): r for r in self.recipes}
        max_crafts = max_crafts_by_ingredient(self.selected_recipe, ing_name, amount)

        if max_crafts == 0:
            result = f"❌ Не хватает {ing_name.capitalize()} даже на один крафт.\n"
        else:
            total_servings = max_crafts * self.selected_recipe.output_amount
            base = expand_recipe(self.selected_recipe, total_servings, all_recipes)
            result = f"📊 Имея {amount} x {ing_name.capitalize()}\n"
            result += f"Можно скрафтить максимум {max_crafts} раз(а) → {total_servings} шт.\n\n"
            result += "Потребуется базовых ингредиентов:\n"
            for name, count in base.items():
                result += f"• {name.capitalize()}: {count}\n"

        self.result_text.delete("1.0", "end")
        self.result_text.insert("1.0", result)

    def calculate_by_servings(self, servings_str: str):
        """Расчёт по требуемому количеству порций."""
        try:
            servings = int(servings_str)
            if servings <= 0:
                raise ValueError
        except ValueError:
            self.result_text.insert("end", "❌ Ошибка: введите положительное число для количества порций.\n")
            return

        all_recipes = {r.name.lower(): r for r in self.recipes}
        try:
            base = expand_recipe(self.selected_recipe, servings, all_recipes)
            crafts = (servings + self.selected_recipe.output_amount - 1) // self.selected_recipe.output_amount
            result = f"Для получения {servings} шт. нужно сделать {crafts} крафтов.\n\n"
            result += "Необходимые базовые ингредиенты:\n"
            for name, count in base.items():
                result += f"• {name.capitalize()}: {count}\n"
            self.result_text.delete("1.0", "end")
            self.result_text.insert("1.0", result)
        except Exception as e:
            self.result_text.delete("1.0", "end")
            self.result_text.insert("1.0", f"Ошибка: {e}\n")

    # Методы для работы с рецептами (без изменений)
    def add_recipe(self):
        dialog = AddEditRecipeDialog(self)
        self.wait_window(dialog)
        self.load_recipes()

    def edit_recipe(self):
        if self.selected_recipe is None:
            messagebox.showwarning("Нет выбора", "Сначала выберите рецепт из списка.")
            return
        dialog = AddEditRecipeDialog(self, recipe_id=self.selected_recipe.id)
        self.wait_window(dialog)
        self.load_recipes()
        # Восстанавливаем выделение
        if self.selected_recipe and self.selected_recipe.id in [r.id for r in self.recipes]:
            self.update_recipe_info()
        else:
            self.selected_recipe = None
            self.clear_recipe_info()

    def delete_recipe(self):
        if self.selected_recipe is None:
            messagebox.showwarning("Нет выбора", "Сначала выберите рецепт.")
            return
        if messagebox.askyesno("Подтверждение", "Удалить рецепт?"):
            delete_recipe(self.selected_recipe.id)
            self.selected_recipe = None
            self.load_recipes()
            self.clear_recipe_info()

    def manage_easy(self):
        EasyIngredientsDialog(self)
        # После закрытия диалога обновляем информацию о рецепте (могли измениться легкодоступные)
        if self.selected_recipe:
            self.update_recipe_info()

if __name__ == "__main__":
    from database import init_db, import_initial_data, DB_NAME
    import os
    init_db()
    app = CraftApp()
    app.mainloop()