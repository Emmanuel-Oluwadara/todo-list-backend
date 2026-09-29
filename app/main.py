from fastapi import FastAPI, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware

from app.database import ensure_db_ready, get_connection
from app.schemas import TodoCreate, TodoResponse, TodoUpdate

app = FastAPI(title="Daylist API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://zedu-todo-list.vercel.app",
    ],
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type"],
    allow_credentials=True,
)


@app.on_event("startup")
def startup_event() -> None:
    ensure_db_ready()


@app.get("/api/todos", response_model=list[TodoResponse])
def list_todos() -> list[TodoResponse]:
    connection = get_connection()
    try:
        rows = connection.execute(
            "SELECT id, text, completed, notes FROM todos ORDER BY id DESC"
        ).fetchall()
    finally:
        connection.close()

    return [
        TodoResponse(
            id=row["id"],
            text=row["text"],
            completed=bool(row["completed"]),
            notes=row["notes"],
        )
        for row in rows
    ]


@app.post("/api/todos", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
def create_todo(todo: TodoCreate) -> TodoResponse:
    connection = get_connection()
    try:
        cursor = connection.execute(
            "INSERT INTO todos (text, notes, completed) VALUES (?, ?, 0)",
            (todo.text, todo.notes),
        )
        connection.commit()
        new_todo_id = cursor.lastrowid
        row = connection.execute(
            "SELECT id, text, completed, notes FROM todos WHERE id = ?",
            (new_todo_id,),
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=500, detail="Unable to load created todo.")
        return TodoResponse(
            id=row["id"],
            text=row["text"],
            completed=bool(row["completed"]),
            notes=row["notes"],
        )
    except HTTPException:
        connection.rollback()
        raise
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


@app.patch("/api/todos/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: int, payload: TodoUpdate) -> TodoResponse:
    connection = get_connection()
    try:
        updates = payload.model_dump(exclude_unset=True, exclude_none=True)
        if "completed" in updates:
            updates["completed"] = int(updates["completed"])
        columns = ("text", "notes", "completed")
        set_clause = ", ".join(
            f"{column} = ?" for column in columns if column in updates
        )
        values = tuple(updates[column] for column in columns if column in updates)
        cursor = connection.execute(
            f"UPDATE todos SET {set_clause} WHERE id = ?",
            (*values, todo_id),
        )
        connection.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Todo not found")

        row = connection.execute(
            "SELECT id, text, completed, notes FROM todos WHERE id = ?",
            (todo_id,),
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Todo not found")

        return TodoResponse(
            id=row["id"],
            text=row["text"],
            completed=bool(row["completed"]),
            notes=row["notes"],
        )
    except HTTPException:
        connection.rollback()
        raise
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


@app.delete("/api/todos/completed")
def delete_completed_todos() -> dict[str, int]:
    connection = get_connection()
    try:
        cursor = connection.execute("DELETE FROM todos WHERE completed = 1")
        connection.commit()
        return {"deleted": cursor.rowcount}
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


@app.delete("/api/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: int) -> Response:
    connection = get_connection()
    try:
        cursor = connection.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
        connection.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Todo not found")
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except HTTPException:
        connection.rollback()
        raise
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
