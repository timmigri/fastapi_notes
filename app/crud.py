from sqlalchemy.orm import Session
from . import models

def create_item(db: Session, item):
    db_item = models.Note(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_item(db: Session, item_id: int):
    return db.query(models.Note).filter(models.Note.id == item_id).first()