import tkinter as tk
from tkinter import ttk, messagebox
import requests
from datetime import datetime
import threading


class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Прогноз погоды и рекомендации")
        self.root.geometry("600x700")
        self.root.resizable(False, False)

        # Заголовок
        title_label = tk.Label(root, text="Погода и рекомендации",
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        # Фрейм для ввода города
        city_frame = tk.Frame(root)
        city_frame.pack(pady=5)

        tk.Label(city_frame, text="Город:", font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=5)
        self.city_entry = tk.Entry(city_frame, width=30, font=("Arial", 12))
        self.city_entry.pack(side=tk.LEFT, padx=5)
        self.city_entry.insert(0, "Воронеж")

        # Кнопка обновления
        self.update_btn = tk.Button(root, text="Обновить прогноз",
                                    command=self.start_update_thread,
                                    font=("Arial", 12), bg="lightblue")
        self.update_btn.pack(pady=10)

        # Прогресс-бар
        self.progress = ttk.Progressbar(root, mode='indeterminate')

        # Основной текст с прогнозом
        self.result_text = tk.Text(root, wrap=tk.WORD, width=65, height=30,
                                   font=("Arial", 10), bg="#f0f0f0")
        self.result_text.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # Полоса прокрутки
        scrollbar = ttk.Scrollbar(root, command=self.result_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.config(yscrollcommand=scrollbar.set)

    def start_update_thread(self):
        """Запуск обновления в отдельном потоке"""
        self.update_btn.config(state=tk.DISABLED)
        self.progress.pack(pady=5)
        self.progress.start()

        thread = threading.Thread(target=self.update_weather)
        thread.daemon = True
        thread.start()

    def update_weather(self):
        """Получение данных о погоде"""
        city = self.city_entry.get().strip()
        if not city:
            city = "Воронеж"

        try:
            # Используем простой формат как в тесте
            url = f"https://wttr.in/{city}?format=%t+%c+%w+%h+%p&m"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                weather_text = response.text.strip()
                report = self.generate_report(weather_text, city)
                self.root.after(0, self.display_report, report)
            else:
                self.root.after(0, self.show_error, f"Ошибка сервера: {response.status_code}")

        except requests.exceptions.ConnectionError:
            self.root.after(0, self.show_error, "Нет подключения к интернету!")
        except Exception as e:
            self.root.after(0, self.show_error, f"Ошибка: {str(e)}")
        finally:
            self.root.after(0, self.stop_progress)

    def generate_report(self, weather_text, city):
        """Генерация отчета из текстового ответа"""
        report = []

        report.append("=" * 50)
        report.append(f"ПРОГНОЗ ПОГОДЫ: {city.upper()}")
        report.append(f"Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
        report.append("=" * 50)
        report.append("")

        # Парсим полученный текст
        parts = weather_text.split()

        report.append("ТЕКУЩАЯ ПОГОДА:")
        report.append("-" * 50)
        report.append(f"{weather_text}")
        report.append("")

        # Пытаемся извлечь температуру
        try:
            temp = weather_text.split('°')[0].replace('+', '')
            temp = float(''.join(c for c in temp if c.isdigit() or c == '-'))
        except:
            temp = 0

        # Магнитные бури (имитация)
        report.append("МАГНИТНЫЕ БУРИ:")
        report.append("-" * 50)
        storm_level = abs(temp) / 10
        if storm_level > 5:
            storm_level = 5
        report.append(f"Уровень геомагнитной активности: {round(storm_level, 1)} баллов")
        if storm_level < 2:
            report.append("Магнитное поле спокойное")
        elif storm_level < 3.5:
            report.append("Небольшие возмущения")
        else:
            report.append("МАГНИТНАЯ БУРЯ! Будьте осторожны")
        report.append("")

        # Рекомендации
        report.append("РЕКОМЕНДАЦИИ:")
        report.append("-" * 50)

        if temp < -10:
            report.append("• Очень холодно! Одевайтесь очень тепло")
        elif temp < 0:
            report.append("• Холодно. Шапка и перчатки обязательны")
        elif temp < 10:
            report.append("• Прохладно. Возьмите куртку")
        elif temp < 20:
            report.append("• Свежо. Легкая куртка не помешает")
        elif temp < 25:
            report.append("• Тепло. Хорошая погода для прогулки")
        else:
            report.append("• Жарко! Пейте больше воды")

        if 'rain' in weather_text.lower() or 'дождь' in weather_text.lower():
            report.append("• Возьмите зонт! Ожидается дождь")
        if 'snow' in weather_text.lower() or 'снег' in weather_text.lower():
            report.append("• На дорогах скользко - будьте осторожны")

        if storm_level > 3:
            report.append("• Метеозависимым: возьмите таблетку от головы")

        return "\n".join(report)

    def display_report(self, report):
        """Отображение отчета"""
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(1.0, report)

    def show_error(self, error_msg):
        """Показ ошибки"""
        messagebox.showerror("Ошибка", error_msg)
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(1.0, f"Ошибка: {error_msg}")

    def stop_progress(self):
        """Остановка прогресс-бара"""
        self.progress.stop()
        self.progress.pack_forget()
        self.update_btn.config(state=tk.NORMAL)


def main():
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()