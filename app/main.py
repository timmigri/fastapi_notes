from typing import List
from fastapi import FastAPI, HTTPException, Depends, status
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger

from .database import engine, get_db
from .models import Base, Note
from .schemas import NoteCreate, NoteResponse
from .logger import setup_logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("DB initialized", source="Init DB")

    yield

    logger.error("App shutting down", source="Init DB")

setup_logger()
app = FastAPI(lifespan=lifespan)

@app.get("/health")
async def health_check():
    logger.debug("Health check called")
    return {"status": "OK"}


@app.post("/notes", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(note: NoteCreate, db: AsyncSession = Depends(get_db)):
    log = logger.bind(source="create_note")
    try:
        log.info("Creating note")
        db_note = Note(**note.model_dump())
        db.add(db_note)
        await db.commit()
        await db.refresh(db_note)
        log.success(f"Note created with ID: {db_note.id} and data: {note.model_dump_json()}")
        return db_note
    except Exception as e:
        await db.rollback()
        log.exception(f"Failed to create note {e}")
        raise HTTPException(status_code=400, detail="Could not create note")


@app.get("/notes", response_model=List[NoteResponse])
async def read_all_notes(db: AsyncSession = Depends(get_db)):
    log = logger.bind(source="read_all_notes")
    log.info("Fetching all notes")
    result = await db.execute(select(Note))
    notes = result.scalars().all()
    log.debug(f"Retrieved {len(notes)} notes")
    return notes


@app.get("/notes/{note_id}", response_model=NoteResponse)
async def read_note(note_id: int, db: AsyncSession = Depends(get_db)):
    log = logger.bind(source=f"read_note {note_id}")
    log.info("Fetching note")
    result = await db.execute(select(Note).where(Note.id == note_id))
    note = result.scalar_one_or_none()
    if not note:
        log.warning("Note not found")
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@app.put("/notes/{note_id}", response_model=NoteResponse)
async def update_note(note_id: int, note: NoteCreate, db: AsyncSession = Depends(get_db)):
    log = logger.bind(source=f"update_note {note_id}")
    log.info("Attempting to update note")
    result = await db.execute(select(Note).where(Note.id == note_id))
    db_note = result.scalar_one_or_none()
    if not db_note:
        log.warning("Note not found")
        raise HTTPException(status_code=404, detail="Note not found")

    try:
        for field, value in note.model_dump(exclude_unset=True).items():
            setattr(db_note, field, value)

        await db.commit()
        await db.refresh(db_note)
        log.success(f"Note updated successfully with data: {note.model_dump_json()}")
        return db_note
    except Exception as e:
        await db.rollback()
        log.exception(f"Failed to update note: {e}")
        raise HTTPException(status_code=500, detail="Error updating note")


@app.delete("/notes/{note_id}", status_code=204)
async def delete_note(note_id: int, db: AsyncSession = Depends(get_db)):
    log = logger.bind(source=f"delete_note {note_id}")
    log.info("Attempting to delete note")
    result = await db.execute(select(Note).where(Note.id == note_id))
    note = result.scalar_one_or_none()
    if not note:
        log.warning("Note not found")
        raise HTTPException(status_code=404, detail="Note not found")

    try:
        await db.delete(note)
        await db.commit()
        log.success("Note deleted")
        return
    except Exception as e:
        await db.rollback()
        log.exception("Failed to delete note")
        raise HTTPException(status_code=400, detail="Error deleting note")
