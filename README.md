# Custom Authentication & Authorization API (DRF + PostgreSQL)

backend-проект на **Django REST Framework + PostgreSQL** с **собственной** системой аутентификации и авторизации.

Проект специально не построен на стандартных механизмах `django.contrib.auth`/`django.contrib.sessions`/стандартных permissions Django. Вместо этого реализованы:
- собственная таблица пользователей;
- собственная таблица серверных сессий;
- собственная RBAC-модель доступа (roles + permissions);
- собственная DRF-аутентификация по opaque session token;
- собственная логика проверки прав доступа к ресурсам.

Справочно: DRF позволяет реализовать собственную схему аутентификации через `BaseAuthentication`, а проверки прав выполняются до входа в код view. Django официально поддерживает PostgreSQL, а для PostgreSQL требуется драйвер `psycopg` или `psycopg2`. 

---

## 1. Что реализовано

### Аутентификация
- Регистрация пользователя.
- Login по `email + password`.
- Logout.
- Идентификация пользователя при следующих запросах по заголовку:
  - `Authorization: Session <token>`
  - или `X-Session-Token: <token>`
- Мягкое удаление аккаунта:
  - `is_active = false`
  - все активные сессии отзываются
  - повторный login становится невозможен.

### Авторизация
Используется **RBAC**-подход:
- пользователь получает одну или несколько ролей;
- роль содержит набор разрешений;
- разрешение описывается парой `resource + action`.

Пример:
- `projects:read`
- `projects:create`
- `reports:generate`
- `access_rules:manage`

### Mock-бизнес-ресурсы
Реализованы mock-endpoints без отдельных таблиц предметной области:
- проекты;
- отчеты;
- счета.

Если пользователь не аутентифицирован — возвращается **401**.
Если пользователь определен, но права недостаточны — **403 Forbidden**.

### Администрирование правил доступа
Для пользователя с ролью `admin` доступны API для:
- просмотра ролей;
- создания ролей;
- просмотра разрешений;
- создания разрешений;
- привязки разрешений к ролям;
- назначения ролей пользователям;
- удаления ролей/разрешений из назначений.

---

## 2. Схема БД

### Таблица `users`
Хранит учетные записи.

Поля:
- `id`
- `last_name`
- `first_name`
- `middle_name`
- `email` — уникальный
- `password_hash` — хэш пароля
- `is_active`
- `created_at`
- `updated_at`

### Таблица `sessions`
Серверные сессии пользователя.

Поля:
- `id`
- `user_id -> users.id`
- `token_hash` — хранится **хэш токена**, а не токен в открытом виде
- `created_at`
- `expires_at`
- `last_used_at`
- `revoked_at`
- `user_agent`
- `ip_address`

Логика:
- при login создается session record;
- клиент получает raw-token только один раз в ответе login;
- в БД хранится только SHA-256 хэш токена;
- при каждом запросе токен хэшируется и сравнивается с таблицей `sessions`.

### Таблица `roles`
Роли доступа.

Поля:
- `id`
- `name` — уникальное имя роли
- `description`
- `created_at`

### Таблица `permissions`
Разрешения доступа.

Поля:
- `id`
- `resource`
- `action`
- `description`
- `created_at`

Ограничение:
- уникальная пара `(resource, action)`.

### Таблица `user_roles`
Связь many-to-many между пользователями и ролями.

Поля:
- `id`
- `user_id`
- `role_id`
- `assigned_at`

Ограничение:
- уникальная пара `(user_id, role_id)`.

### Таблица `role_permissions`
Связь many-to-many между ролями и разрешениями.

Поля:
- `id`
- `role_id`
- `permission_id`
- `assigned_at`

Ограничение:
- уникальная пара `(role_id, permission_id)`.

---

## 3. Логика проверки доступа

Алгоритм:
1. Клиент отправляет запрос с session token.
2. DRF authentication class читает заголовок.
3. Токен хэшируется и ищется в таблице `sessions`.
4. Проверяется:
   - сессия существует;
   - не отозвана;
   - не истекла;
   - пользователь `is_active = true`.
5. Если все корректно, пользователь считается аутентифицированным.
6. Затем permission layer проверяет, есть ли у пользователя разрешение `(resource, action)` через связи:
   - `users -> user_roles -> roles -> role_permissions -> permissions`
7. При отсутствии пользователя возвращается **401**.
8. При отсутствии нужного permission возвращается **403**.

---

## 4. Тестовые данные

Команда `seed_demo_data` создает:

### Роли
- `admin`
- `viewer`
- `editor`
- `accountant`

### Разрешения
- `access_rules:read`
- `access_rules:manage`
- `projects:read`
- `projects:create`
- `reports:read`
- `reports:generate`
- `invoices:read`

### Пользователи
- `admin@example.com / Admin123`
- `viewer@example.com / Viewer123`
- `editor@example.com / Editor123`
- `inactive@example.com / Inactive123`

Пользователь `inactive@example.com` создается с `is_active = false`.

---

## 5. Установка и запуск на Windows

### Вариант 1. Быстрый запуск
```bat
run_windows.bat
```

Скрипт:
- создает виртуальное окружение;
- устанавливает зависимости;
- применяет миграции;
- заполняет БД тестовыми данными;
- запускает сервер.

По умолчанию используются переменные:
- `POSTGRES_HOST=localhost`
- `POSTGRES_PORT=5432`
- `POSTGRES_DB=custom_auth_db`
- `POSTGRES_USER=postgres`
- `POSTGRES_PASSWORD=postgres`

### Вариант 2. Ручной запуск через cmd
```bat
python -m venv .venv
.venv\Scriptsctivate.bat
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo_data
python manage.py runserver 127.0.0.1:8000
```

Базовый адрес:
```text
http://127.0.0.1:8000/
```

Проверка health:
```text
GET /health/
```

---

## 6. API

## Auth

### Регистрация
```http
POST /api/auth/register/
Content-Type: application/json

{
  "last_name": "Иванов",
  "first_name": "Иван",
  "middle_name": "Иванович",
  "email": "user@example.com",
  "password": "StrongPass123!",
  "password_repeat": "StrongPass123!"
}
```

### Login
```http
POST /api/auth/login/
Content-Type: application/json

{
  "email": "admin@example.com",
  "password": "Admin123!"
}
```

Ответ:
```json
{
  "token_type": "Session",
  "access_token": "<RAW_SESSION_TOKEN>",
  "expires_at": "2026-...",
  "user": { ... }
}
```

### Текущий пользователь
```http
GET /api/auth/me/
Authorization: Session <RAW_SESSION_TOKEN>
```

### Обновление профиля
```http
PATCH /api/auth/me/
Authorization: Session <RAW_SESSION_TOKEN>
Content-Type: application/json

{
  "first_name": "Петр"
}
```

### Logout
```http
POST /api/auth/logout/
Authorization: Session <RAW_SESSION_TOKEN>
```

### Мягкое удаление аккаунта
```http
DELETE /api/auth/me/
Authorization: Session <RAW_SESSION_TOKEN>
```

---

## 7. Mock-ресурсы

### Проекты
```http
GET /api/mock/projects/
Authorization: Session <token>
```
Требуется: `projects:read`

```http
POST /api/mock/projects/
Authorization: Session <token>
```
Требуется: `projects:create`

### Отчеты
```http
GET /api/mock/reports/
Authorization: Session <token>
```
Требуется: `reports:read`

```http
POST /api/mock/reports/
Authorization: Session <token>
```
Требуется: `reports:generate`

### Счета
```http
GET /api/mock/invoices/
Authorization: Session <token>
```
Требуется: `invoices:read`

---

## 8. Админские endpoints

Все endpoints ниже требуют пользователя с правами `access_rules:*` (роль `admin`).

### Получить список разрешений
```http
GET /api/admin/permissions/
Authorization: Session <token>
```

### Создать разрешение
```http
POST /api/admin/permissions/
Authorization: Session <token>
Content-Type: application/json

{
  "resource": "warehouse",
  "action": "read",
  "description": "Просмотр склада"
}
```

### Получить список ролей
```http
GET /api/admin/roles/
Authorization: Session <token>
```

### Создать роль
```http
POST /api/admin/roles/
Authorization: Session <token>
Content-Type: application/json

{
  "name": "warehouse_manager",
  "description": "Менеджер склада"
}
```

### Привязать permission к role
```http
POST /api/admin/roles/1/permissions/
Authorization: Session <token>
Content-Type: application/json

{
  "permission_id": 3
}
```

### Удалить permission из role
```http
DELETE /api/admin/roles/1/permissions/3/
Authorization: Session <token>
```

### Получить список пользователей
```http
GET /api/admin/users/
Authorization: Session <token>
```

### Назначить роль пользователю
```http
POST /api/admin/users/2/roles/
Authorization: Session <token>
Content-Type: application/json

{
  "role_id": 4
}
```

### Удалить роль у пользователя
```http
DELETE /api/admin/users/2/roles/4/
Authorization: Session <token>
```

---

## 9. Тесты mock_api
Для тестов созданны bat-скрипты
Файл:	            Описание:
common.bat	      Общие функции: логин, получение токена
logout.bat	      Выход из системы (logout)
test_admin.bat	  Тесты для администратора (полный доступ)
test_editor.bat	  Тесты для редактора (ограниченный доступ)
test_viewer.bat	  Тесты для наблюдателя (только чтение)
test_inactive.bat	Тест для неактивного пользователя (ошибка логина)

Для тестов используются тестовые данные из seed_demo_data.py