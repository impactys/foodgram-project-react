# Foodgram

Это проект Foodgram - он позволяет публиковать рецепты, добавлять их в избранное, подписываться на других авторов и создавать список покупок. 

Автор: Илья Корытов (https://github.com/impactys)

ilyafood.bounceme.net

Сервер
-login: yc-user
-passphrase: NRjeSf
-ip: 158.160.77.156

Тестовый пользователь
-maks@mail.ru
-Maks2023

Админ
-Электронная почта: admin@mail.ru
Ник: Admin
Имя: Админ
Фамилия: Админ
Password: admin

### Клонирование проекта

Для клонирования проекта вы можете воспользоваться ссылкой: git@github.com:impactys/foodgram-project-react.git

### Требуемые технологии

Для работы с проектом вам потребуются следующие технологии:

- Docker
- Git
- Postgres
- Django
- Gunicorn
- Nginx

### Функционал

- Пользователи могут добавлять свои рецепты с фотографиями и описанием
- Пользователи могут отмечать рецепты избранными
- Пользователи могут подписываться на других авторов, чтобы видеть их рецепты в ленте
- Пользователи могут создавать список покупок, включающий необходимые ингредиенты для рецептов
- Возможно скачать список покупок в удобном формате
   
#### Клонирование проекта

Сперва клонируйте репозиторий и создайте виртуальное окружение(Venv)

```
git clone git@github.com:impactys/foodgram-project-react.git
cd foodgram-project-react
python -m venv venv
source venv/Scripts/activate
cd backend
python -m pip install --upgrade pip
pip install -r requirements.txt
```

#### Создание .env-файла

```
cd infra
```

```
SECRET_KEY='Секретный ключ Django'
DEBUG=False
ALLOWED_HOSTS= ip_сервера,127.0.0.1,localhost,домен
DB_ENGINE=django.db.backends.postgresql
DB_NAME=foodgram
DB_USER=foodgram_user
DB_PASSWORD=foodgram_password
DB_HOST=db
DB_PORT=5432
```
#### Собираем оркестр
```
docker-compose-local up
```
#### Проводим миграции
```
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate
```
#### Наполняем базу
```
docker-compose exec backend python manage.py load_to_db
```
#### Статика
```
docker-compose exec backend python manage.py collectstatic --no-input
```
#### Создаем суперпользователя
```
docker-compose exec backend python manage.py createsuperuser
```