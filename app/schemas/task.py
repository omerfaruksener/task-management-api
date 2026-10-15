from pydantic import BaseModel, ConfigDict
from typing import Optional

class TaskCreate(BaseModel):
    title : str
    description: Optional[str] = None
    status: str = "todo"
    priority: str = "medium"

# Güncelleme yaparken kullanıcının tüm alanları göndermesi zorunlu olmasın diye
# her alanı Optional yapıyoruz.
class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None


class TaskResponse(TaskCreate):
    id:int

    model_config = ConfigDict(from_attributes=True)

class Task(TaskCreate):
    id : int
