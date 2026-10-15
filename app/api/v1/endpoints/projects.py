from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.core.security import get_current_user
from app.models.project import Project
from app.models.task import Task
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate

router = APIRouter()

#1.create project
@router.post("/", response_model = ProjectResponse)
def create_project(project_in:ProjectCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    new_project = Project(**project_in.model_dump(), owner_id = current_user.id)
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project

#2.list of project
@router.get("/", response_model= List[ProjectResponse])
def get_projects(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    projects = db.query(Project).filter(Project.pwner_id == current_user.id).all()
    return projects


#3.get a project
@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == project_id, Project.owner_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Proje bulunamadı veya yetkiniz yok")
    return project


#4.update project
@router.patch("/{project_id}", response_model=ProjectResponse)
def update_project(project_id: int, project_in: ProjectUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == project_id, Project.owner_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Proje bulunamadı veya yetkiniz yok")
    
    update_data = project_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(project, key, value)
        
    db.commit()
    db.refresh(project)
    return project

#5.delete project
@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == project_id, Project.owner_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Proje bulunamadı veya yetkiniz yok")
    
    # KURAL: Bu projeye bağlı görev var mı kontrol et
    tasks_in_project = db.query(Task).filter(Task.project_id == project_id).first()
    if tasks_in_project:
        raise HTTPException(
            status_code=400, 
            detail="Bu projeyi silemezsiniz çünkü içinde görevler var. Lütfen önce görevleri silin veya başka projeye taşıyın."
        )
    
    db.delete(project)
    db.commit()
    return {"message": "Proje başarıyla silindi"}