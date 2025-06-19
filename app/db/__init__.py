from app.db.connection import DB_FILENAME, close_connection, get_file_manager, FILETYPE
from sqlalchemy import create_engine
from app.db.models import Base

def init_db(reset: bool = False):
    close_connection()

    DB_PATH = get_file_manager()._resolve(FILETYPE.DATABASE, DB_FILENAME)

    engine = create_engine(f"sqlite:///{DB_PATH}")
    engine.dispose()

    if reset and DB_PATH.exists():
        try:
            get_file_manager().delete(FILETYPE.DATABASE, DB_FILENAME)
        except PermissionError as e:
            print(f"⚠️ Unable to delete {DB_FILENAME}: {e}")
            print("⚠️ Attempting to force garbage collection.")
            gc.collect()
            get_file_manager().delete(FILETYPE.DATABASE, DB_FILENAME)

    engine = create_engine(f"sqlite:///{DB_PATH}")
    Base.metadata.create_all(bind=engine)
    
    return engine
