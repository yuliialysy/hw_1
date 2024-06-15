# Використовуємо офіційний базовий образ Python
FROM python:3.9-slim

# Встановлюємо робочу директорію всередині контейнера
WORKDIR /app

# Копіюємо файл requirements.txt до робочої директорії
COPY requirements.txt .

# Встановлюємо залежності
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо усі файли проекту до робочої директорії
COPY . .

# Вказуємо команду за замовчуванням для запуску застосунку
CMD ["python", "bot.py"]

