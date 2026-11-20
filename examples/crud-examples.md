# Примеры CRUD-запросов для `/users`

Примеры используют JSONPlaceholder: `https://jsonplaceholder.typicode.com`.

## Read — получить пользователей

```bash
curl -i https://jsonplaceholder.typicode.com/users
curl -i https://jsonplaceholder.typicode.com/users/1
```

Ожидаемый успешный статус: `200 OK`.

## Create — создать пользователя

```bash
curl -i -X POST https://jsonplaceholder.typicode.com/users \
  -H "Content-Type: application/json" \
  -d '{"name":"Alex Smith","username":"alex","email":"alex@example.com"}'
```

Ожидаемый статус: `201 Created`.

## Update — полностью обновить пользователя

```bash
curl -i -X PUT https://jsonplaceholder.typicode.com/users/1 \
  -H "Content-Type: application/json" \
  -d '{"id":1,"name":"Alex Smith","username":"alex","email":"alex@example.com"}'
```

Обычно успешный статус: `200 OK` или `204 No Content` — зависит от сервера.

## Update — изменить отдельные поля

```bash
curl -i -X PATCH https://jsonplaceholder.typicode.com/users/1 \
  -H "Content-Type: application/json" \
  -d '{"name":"Alex Smith"}'
```

Обычно успешный статус: `200 OK` или `204 No Content`.

## Delete — удалить пользователя

```bash
curl -i -X DELETE https://jsonplaceholder.typicode.com/users/1
```

Обычно успешный статус: `200 OK` или `204 No Content`.

> JSONPlaceholder — тестовый сервис: он возвращает демонстрационные ответы, но не сохраняет изменения на постоянной основе. У разных REST API статусы и формат ответов могут отличаться.
