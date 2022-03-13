from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.auth import oauth2_scheme
from src.database import get_database_session, Condition
from src.models.condition import ConditionRead

router = APIRouter(
    prefix="/conditions",
    tags=["conditions"],
    dependencies=[Depends(oauth2_scheme)]
)


@router.get("/", response_model=List[ConditionRead])
def get_all(
        animal_ids: Optional[List[int]] = Query(None),
        page: int = 0,
        page_size: int = 100,
        sort_order: str = "desc",
        session: Session = Depends(get_database_session)
):
    statement = session.query(Condition)

    if animal_ids is not None and len(animal_ids) > 0:
        statement = statement.where(Condition.animal_id.in_(animal_ids))

    return statement.order_by(Condition.id.asc() if sort_order == "asc" else Condition.id.desc())\
        .limit(page_size)\
        .offset(page * page_size).all()
