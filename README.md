**FastAPI CRUD API для заметок**  

**🚀 Запуск в Docker:**  
`docker-compose up --build`

**📌 Эндпоинты:**  
- `POST /notes`: Создание (структура заметки - `{"name": "...", "description": "..."}`)  
- `GET /notes`: Получение всех заметок 
- `GET /notes/{id}`: Получение одной заметки
- `PUT /notes/{id}`: Обновление заметки 
- `DELETE /notes/{id}`: Удаление заметки
- `GET /health`: Проверка работоспособности сервиса
- `GET /docs`: Swagger документация

**🛠 Технологии:** FastAPI + SQLAlchemy + PostgreSQL