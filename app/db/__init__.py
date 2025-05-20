from app.db.connection import get_connection
from app.db.models import Base

def init_db():
    conn = get_connection()
    Base.metadata.create_all(bind=conn)
