from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class TodoCreate(BaseModel):
    text: str = Field(..., min_length=1, max_length=160)
    notes: str = ""

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
    text: str | None = Field(default=None, min_length=1, max_length=160)
    notes: str | None = None
    completed: bool | None = None

    @model_validator(mode="after")
    def validate_update(self) -> "TodoUpdate":
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided.")
        if self.text is not None:
            trimmed = self.text.strip()
            if not trimmed:
                raise ValueError("Text cannot be blank.")
            if len(trimmed) > 160:
                raise ValueError("Text must be 160 characters or fewer.")
            self.text = trimmed
        if self.text is None and self.notes is None and self.completed is None:
            raise ValueError("At least one field must be provided.")
        return self


class TodoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    text: str
    completed: bool
    notes: str
