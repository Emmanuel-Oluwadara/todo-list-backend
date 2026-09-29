# Daylist API

Base URL for the local backend:

```text
http://127.0.0.1:8000
```

All routes below use the `/api` prefix.

## Get all todos

```http
GET /api/todos
```

Response:

```json
[
  {
    "id": 1,
    "text": "Plan the week",
    "completed": false
  }
]
```

## Create a todo

```http
POST /api/todos
Content-Type: application/json
```

Request body:

```json
{
  "text": "Plan the week"
}
```

Response `201 Created`:

```json
{
  "id": 1,
  "text": "Plan the week",
  "completed": false
}
```

## Update a todo

```http
PATCH /api/todos/{todo_id}
Content-Type: application/json
```

Request body:

```json
{
  "completed": true
}
```

Response:

```json
{
  "id": 1,
  "text": "Plan the week",
  "completed": true
}
```

## Delete all completed todos

```http
DELETE /api/todos/completed
```

Response:

```json
{
  "deleted": 2
}
```

## Delete one todo

```http
DELETE /api/todos/{todo_id}
```

Response status:

```http
204 No Content
```

## Validation rules

- `text` is required
- It is trimmed before saving
- It must be between 1 and 160 characters
- Empty or whitespace-only values are rejected with `422`

## Notes for the frontend

- Use the `id` returned from create/list calls for update and delete requests.
- The app uses SQLite locally, so the database stays on this computer and is not meant to be committed.
- If Vite runs on a different local port, add that exact origin to the CORS list in `app/main.py`.
