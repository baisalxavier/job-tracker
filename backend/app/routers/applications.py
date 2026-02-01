from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.db.models import Application as ApplicationModel
from app.schemas.application import ApplicationCreate, ApplicationOut, ApplicationStatus
from app.schemas.common import PaginatedResponse

router = APIRouter(prefix="/applications", tags=["applications"])

# ----------------------------
# In-memory "database"
# ----------------------------
# applications_db = []
# current_id = 1


# ----------------------------
# Pydantic Schemas
# ----------------------------

# ----------------------------
# CREATE
# ----------------------------
@router.post("/", response_model=ApplicationOut)
def create_application(app: ApplicationCreate, db: Session = Depends(get_db)):
    db_app = ApplicationModel(
        company=app.company,
        role=app.role,
        status=app.status.value,
    )
    db.add(db_app)
    db.commit()
    db.refresh(db_app)
    return db_app




# ----------------------------
# READ ALL
# ----------------------------
@router.get("/", response_model=PaginatedResponse[ApplicationOut])
def list_applications(
    db: Session = Depends(get_db),
    q: Optional[str] = Query(default=None, min_length=1, max_length=100),
    status: Optional[ApplicationStatus] = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=50),
    sort_by: str = Query(default="id"),
    sort_order: str = Query(default="desc"),
):
    query = db.query(ApplicationModel)

    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                ApplicationModel.company.ilike(like),
                ApplicationModel.role.ilike(like),
            )
        )

    if status:
        query = query.filter(ApplicationModel.status == status.value)

    # =========================
    #  SORTING LOGIC (ADD HERE)
    # =========================
    allowed_sort_fields = {
        "id": ApplicationModel.id,
        "company": ApplicationModel.company,
        "role": ApplicationModel.role,
        "status": ApplicationModel.status,
    }

    sort_column = allowed_sort_fields.get(sort_by)
    if not sort_column:
        raise HTTPException(status_code=400, detail="Invalid sort field")

    if sort_order.lower() == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    total = query.count()

    items = (
        query.order_by(ApplicationModel.id.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    return {"items": items, "total": total, "page": page, "limit": limit}



# ----------------------------
# READ ONE
# ----------------------------
@router.get("/{app_id}", response_model=ApplicationOut)
def get_application(app_id: int, db: Session = Depends(get_db)):
    app = db.query(ApplicationModel).filter(ApplicationModel.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return app




# ----------------------------
# UPDATE
# ----------------------------
@router.put("/{app_id}", response_model=ApplicationOut)
def update_application(app_id: int, updated: ApplicationCreate, db: Session = Depends(get_db)):
    db_app = db.query(ApplicationModel).filter(ApplicationModel.id == app_id).first()
    if not db_app:
        raise HTTPException(status_code=404, detail="Application not found")

    db_app.company = updated.company
    db_app.role = updated.role
    db_app.status = updated.status.value

    db.commit()
    db.refresh(db_app)
    return db_app




# ----------------------------
# DELETE
# ----------------------------
@router.delete("/{app_id}")
def delete_application(app_id: int, db: Session = Depends(get_db)):
    app = db.query(ApplicationModel).filter(ApplicationModel.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    db.delete(app)
    db.commit()
    return {"message": "Deleted"}

