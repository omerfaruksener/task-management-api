from pydantic import BaseModel, ConfigDict
from typing import Optional
from enum import Enum



class TaskStatus(str, Enum):
    todo = "todo"
    in_progress = "in_progress"
    done = "done"

class TaskPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class TaskCreate(BaseModel):
    title : str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.todo
    priority: TaskPriority = TaskPriority.medium
    project_id : Optional[int] = None

# Güncelleme yaparken kullanıcının tüm alanları göndermesi zorunlu olmasın diye
# her alanı Optional yapıyoruz.
class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None


class TaskResponse(TaskCreate):
    id:int
    owner_id: int
    model_config = ConfigDict(from_attributes=True)
    project_id: Optional[int] = None