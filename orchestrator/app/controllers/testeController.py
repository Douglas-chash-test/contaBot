from sqlalchemy import text
from sqlalchemy.orm import Session


def teste_api() -> dict[str, str]:
    return {"API": "ok"}

def teste_db(db: Session) -> dict[str, str]:
    db.execute(text("SELECT 1"))
    return {"database": "ok"}