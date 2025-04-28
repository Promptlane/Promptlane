from app.db.database import db
from .openai import openai_models
from .anthropic import anthropic_models

def seed():
    session = db.get_session()
    try:
        models = []
        models += openai_models
        models += anthropic_models
        session.add_all(models)
        session.commit()
    finally:
        db.close_session(session)

if __name__ == '__main__':
    seed()
