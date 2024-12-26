# Deploy django project on server

## Создание пользователя
```bash
adduser username
usermod -aG sudo username
groups username
su username
cd ~ # переключение на директорию нового пользователя
```

---

## Перадача все нужных прав пользователю для работы с nginx и gunicorn:

![image](https://github.com/user-attachments/assets/814dbedf-0ad4-4286-96b5-17f7bd3e1b15)

![image](https://github.com/user-attachments/assets/079afc8d-c171-4196-97ea-56375266cb17)

---

## Обновление и установка необходимых пакетов
```bash
sudo apt-get update
sudo apt-get install -y git python3-dev python3-venv python3-pip supervisor nginx nano libpq-dev

git clone ваш_проект
cd ваш_проект
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

---

## Создание .env файла для записи секретных значений

Создайте файл `.env`:
```bash
nano .env
```

Пример файла `.env`:
```bash
SECRET_KEY=your_secret_key
DEBUG=False
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
```

После этого выполните bash-цикл для экспорта переменных из `.env` и проверки:
```bash
while read file; do
   export "$file"
done < .env

printenv | grep SECRET  # Замените SECRET на название вашей переменной для проверки
```

---

## Установка базы данных PostgreSQL
```bash
sudo apt install postgresql postgresql-contrib
sudo -u postgres psql
```

### Команды для настройки базы данных:
```sql
CREATE DATABASE название_базы_данных;
CREATE USER имя_пользователя_бд WITH PASSWORD 'пароль_для_пользователя';
GRANT ALL PRIVILEGES ON DATABASE название_базы_данных TO имя_пользователя_бд;
\c название_базы_данных
GRANT ALL ON SCHEMA public TO имя_пользователя_бд;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO имя_пользователя_бд;
\q
```

---

## Миграции и загрузка фикстур
```bash
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py loaddata fixtures/goods/categories.json
python3 manage.py loaddata fixtures/goods/products.json
```

> **Примечание:** Если возникают ошибки при миграциях, убедитесь, что у пользователя сервера есть права для внесения изменений в базу данных.

---

## Запуск сервера
```bash
# Запуск сервера разработки Django
python3 manage.py runserver 0.0.0.0:8000

# Запуск сервера через Gunicorn
gunicorn app.wsgi -b 0.0.0.0:8000
```

Перейдите по адресу: `http://ваш_ip_адрес:8000/`

---

## Установка и настройка Nginx

### Установка Nginx
```bash
sudo apt-get install nginx
```

### Настройка конфигурации Nginx
Откройте конфигурационный файл:
```bash
sudo nano /etc/nginx/sites-enabled/default
```

Добавьте следующее содержимое:
```nginx
server {
    listen 80 default_server;
    listen [::]:80 default_server;

    location /static/ {
        alias /home/имя_пользователя/название_проекта/staticfiles/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header X-Forwarded-Host $server_name;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_redirect off;
        add_header P3P 'CP="ALL DSP COR PSAa OUR NOR ONL UNI COM NAV"';
        add_header Access-Control-Allow-Origin *;
    }
}
```

### Настройка статики в `settings.py`
```python
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / "static"
]
STATIC_ROOT = BASE_DIR / 'staticfiles'
```

---

## Сборка статических файлов
```bash
python3 manage.py collectstatic
sudo service nginx restart
sudo chmod o+x /home/имя_пользователя
sudo service nginx restart

# Запуск Gunicorn
gunicorn app.wsgi -b 127.0.0.1:8000
```

---

## Настройка Supervisor

### Создание конфигурационного файла Supervisor
Перейдите в директорию конфигураций:
```bash
cd /etc/supervisor/conf.d/
sudo nano название_проекта.conf
```

Добавьте следующее содержимое:
```ini
[program:название_проекта]
command = /home/имя_пользователя/название_проекта/venv/bin/gunicorn app.wsgi -b 127.0.0.1:8000 -w 4 --timeout 90
autostart=true
autorestart=true
directory=/home/имя_пользователя/название_проекта
stderr_logfile=/var/log/название_проекта.err.log
stdout_logfile=/var/log/название_проекта.out.log
```

### Применение изменений
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl status название_проекта
```


Баг фиксы nginx
-------------------------------------------------------
![Снимок экрана 2024-12-26 114823](https://github.com/user-attachments/assets/ae6eae5e-2dd0-4efa-866a-072e617995c4)

![Снимок экрана 2024-12-26 114842](https://github.com/user-attachments/assets/a98f0554-9d32-4830-b87a-02c2ba24631f)

![Снимок экрана 2024-12-26 114856](https://github.com/user-attachments/assets/24b4af39-5cb0-4e71-a57b-18217555c5f6)


