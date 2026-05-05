import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

# --- Настройки ---
DATA_FILE = "movies.json"

# --- Класс приложения ---
class MovieLibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Movie Library")
        self.movies = []

        # Создание виджетов
        self.create_widgets()
        self.load_movies()
        self.update_table()
        self.update_genre_combobox()

    def create_widgets(self):
        # --- Блок ввода ---
        frame_inputs = tk.Frame(self.root)
        frame_inputs.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        tk.Label(frame_inputs, text="Название").grid(row=0, column=0, padx=5, pady=2)
        self.entry_title = tk.Entry(frame_inputs)
        self.entry_title.grid(row=0, column=1, padx=5, pady=2)

        tk.Label(frame_inputs, text="Жанр").grid(row=1, column=0, padx=5, pady=2)
        self.entry_genre = tk.Entry(frame_inputs)
        self.entry_genre.grid(row=1, column=1, padx=5, pady=2)

        tk.Label(frame_inputs, text="Год выпуска").grid(row=2, column=0, padx=5, pady=2)
        self.entry_year = tk.Entry(frame_inputs)
        self.entry_year.grid(row=2, column=1, padx=5, pady=2)

        tk.Label(frame_inputs, text="Рейтинг (0-10)").grid(row=3, column=0, padx=5, pady=2)
        self.entry_rating = tk.Entry(frame_inputs)
        self.entry_rating.grid(row=3, column=1, padx=5, pady=2)

        # Кнопка добавления
        self.btn_add = tk.Button(self.root, text="Добавить фильм", command=self.add_movie)
        self.btn_add.grid(row=1, column=0, columnspan=2, pady=(0, 10))

        # --- Таблица ---
        self.tree = ttk.Treeview(self.root, columns=("title", "genre", "year", "rating"), show='headings')
        self.tree.heading("title", text="Название")
        self.tree.heading("genre", text="Жанр")
        self.tree.heading("year", text="Год")
        self.tree.heading("rating", text="Рейтинг")
        self.tree.grid(row=2, column=0, columnspan=2, padx=5, pady=(0, 10), sticky="nsew")

        # Настройка сетки для растягивания таблицы
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # --- Блок фильтрации ---
        frame_filter = tk.Frame(self.root)
        frame_filter.grid(row=3, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="ew")

        tk.Label(frame_filter, text="Фильтр по жанру").grid(row=0, column=0, padx=(5, 2), pady=5)
        self.combo_genre = ttk.Combobox(frame_filter, values=["Все"])
        self.combo_genre.current(0) # Выбираем "Все" по умолчанию
        self.combo_genre.grid(row=0, column=1, padx=(2, 5), pady=5)

        tk.Label(frame_filter, text="Фильтр по году").grid(row=1, column=0, padx=(5, 2), pady=(0, 5))
        self.entry_filter_year = tk.Entry(frame_filter)
        self.entry_filter_year.grid(row=1, column=1, padx=(2, 5), pady=(0, 5))

        self.btn_filter = tk.Button(self.root, text="Применить фильтр", command=self.apply_filter)
        self.btn_filter.grid(row=4, column=0, columnspan=2)

    # --- Логика приложения ---
    def add_movie(self):
        title = self.entry_title.get().strip()
        genre = self.entry_genre.get().strip()
        year = self.entry_year.get().strip()
        rating = self.entry_rating.get().strip()

        # Валидация полей
        if not title or not genre or not year or not rating:
            messagebox.showerror("Ошибка ввода", "Пожалуйста, заполните все поля.")
            return

        if not year.isdigit():
            messagebox.showerror("Ошибка ввода", "Год выпуска должен быть целым числом.")
            return

        year_num = int(year)

        try:
            rating_num = float(rating)
            if not (0 <= rating_num <= 10):
                raise ValueError("Рейтинг вне диапазона")
        except ValueError:
            messagebox.showerror("Ошибка ввода", "Рейтинг должен быть числом от 0 до 10.")
            return

        # Создание словаря фильма
        movie = {"title": title.title(), "genre": genre.title(), "year": year_num, "rating": round(rating_num, 1)}
        
        # Добавление в список и обновление интерфейса
        self.movies.append(movie)
        
        # Сохранение данных в файл
        try:
            self.save_movies()
            messagebox.showinfo("Успех", "Фильм успешно добавлен и сохранен!")
            self.update_table() # Обновить всю таблицу (или можно передать [movie] для оптимизации)
            self.update_genre_combobox() # Обновить список жанров в фильтре
            
            # Очистка полей ввода
            self.entry_title.delete(0, tk.END)
            self.entry_genre.delete(0, tk.END)
            self.entry_year.delete(0, tk.END)
            self.entry_rating.delete(0, tk.END)
             
        except Exception as e:
            messagebox.showerror("Ошибка сохранения", f"Не удалось сохранить данные: {e}")

    def apply_filter(self):
        genre_filter = self.combo_genre.get()
        year_text = self.entry_filter_year.get().strip()
        
        filtered_movies = self.movies.copy()

        # Фильтрация по жанру (всегда применяется)
        if genre_filter != "Все":
            filtered_movies = [m for m in filtered_movies if m['genre'] == genre_filter]

        # Фильтрация по году (применяется только если введено число)
        if year_text.isdigit():
            year_num = int(year_text)
            filtered_movies = [m for m in filtered_movies if m['year'] == year_num]
        
        # Обновление таблицы (вынесено за условия)
        self.update_table(filtered_movies)

    def update_table(self, data=None):
        """Очищает и заполняет таблицу данными."""
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        if data is None:
            data_to_show = self.movies
        else:
            data_to_show = data

        for m in data_to_show:
            # Округляем рейтинг для красоты отображения
            rating_display = str(m['rating']) if isinstance(m['rating'], int) else f"{m['rating']:.1f}"
            self.tree.insert("", "end", values=(m['title'], m['genre'], m['year'], rating_display))

    def update_genre_combobox(self):
        """Обновляет список жанров в Combobox на основе текущих данных."""
         genres = sorted({m['genre'] for m in self.movies})
         genre_list = ["Все"] + genres
         self.combo_genre['values'] = genre_list

    def save_movies(self):
        """Сохраняет список фильмов в JSON файл с обработкой ошибок."""
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.movies, f, ensure_ascii=False, indent=4)
        except (IOError, PermissionError) as e:
            raise Exception(f"Ошибка записи в файл: {e.strerror}")
        except TypeError as e:
            raise Exception(f"Ошибка сериализации данных: {e}")

    def load_movies(self):
        """Загружает фильмы из JSON файла с обработкой ошибок."""
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    self.movies = json.load(f)
            except json.JSONDecodeError:
                messagebox.showwarning("Предупреждение", f"Файл {DATA_FILE} поврежден или пуст. Будет создан новый.")
                self.movies = []
            except Exception as e:
                messagebox.showerror("Ошибка загрузки", f"Не удалось прочитать данные: {e}")
                self.movies = []
        else:
            self.movies = []

    def on_closing(self):
        """Действия при закрытии окна."""
        try:
            self.save_movies()
        except Exception as e:
            messagebox.showerror("Ошибка при выходе", f"Не удалось сохранить данные перед закрытием: {e}")
        finally:
            self.root.destroy()


# --- Запуск приложения ---
if __name__ == "__main__":
    root = tk.Tk()
    app = MovieLibraryApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()