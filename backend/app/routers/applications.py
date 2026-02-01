from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from sqlalchemy.orm import Session
from fastapi import Depends
from app.db.models import Application
from app.db.deps import get_db
from app.db.models import Application as ApplicationModel


router = APIRouter(prefix="/applications", tags=["applications"])

# ----------------------------
# In-memory "database"
# ----------------------------
# applications_db = []
# current_id = 1


# ----------------------------
# Pydantic Schemas
# ----------------------------
class ApplicationCreate(BaseModel):
    company: str
    role: str
    status: str


class ApplicationOut(ApplicationCreate):
    id: int


# ----------------------------
# CREATE
# ----------------------------
@router.post("/", response_model=ApplicationOut)
def create_application(
    app: ApplicationCreate,
    db: Session = Depends(get_db)
):
    db_app = Application(
        company=app.company,
        role=app.role,
        status=app.status
    )
    db.add(db_app)
    db.commit()
    db.refresh(db_app)
    return db_app



# ----------------------------
# READ ALL
# ----------------------------
@router.get("/")
def get_applications(db: Session = Depends(get_db)):
    return db.query(Application).all()



# ----------------------------
# READ ONE
# ----------------------------
@router.get("/{app_id}")
def get_application(app_id: int, db: Session = Depends(get_db)):
    app = db.query(Application).filter(Application.id == app_id).first()
    if not app:
        raise HTTPException(404, "Not found")
    return app



# ----------------------------
# UPDATE
# ----------------------------
@router.put("/{app_id}")
def update_application(
    app_id: int,
    updated: ApplicationCreate,
    db: Session = Depends(get_db)
):
    app = db.query(Application).filter(Application.id == app_id).first()
    if not app:
        raise HTTPException(404)

    app.company = updated.company
    app.role = updated.role
    app.status = updated.status

    db.commit()
    db.refresh(app)
    return app



# ----------------------------
# DELETE
# ----------------------------
@router.delete("/{app_id}")
def delete_application(app_id: int, db: Session = Depends(get_db)):
    app = db.query(Application).filter(Application.id == app_id).first()
    if not app:
        raise HTTPException(404)

    db.delete(app)
    db.commit()
    return {"message": "Deleted"}

