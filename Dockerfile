# Используем Python в качестве базового образа
FROM python:3.11

# Устанавливаем рабочую директорию в /app
WORKDIR /app

# Копируем зависимости проекта и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все файлы проекта в /app
COPY . .

# Запускаем FastAPI приложение
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
