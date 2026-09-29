from pydantic import BaseModel, ConfigDict, Field, field_validator


class TodoCreate(BaseModel):
    text: str = Field(..., min_length=1, max_length=160)

    @field_validator("text")
    @classmethod
    def validate_text(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Text cannot be blank.")
        if len(trimmed) > 160:
            raise ValueError("Text must be 160 characters or fewer.")
        return trimmed


class TodoUpdate(BaseModel):
    completed: bool


class TodoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    text: str
    completed: bool
