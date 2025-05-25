import gc
from sqlalchemy import create_engine
from app.db.connection import DB_PATH, close_connection
from app.db.models import Base

def init_db(reset: bool = False):
    # Explicitly close lingering DB-API connections
    close_connection()

    # Explicitly create and dispose of engine before deletion
    engine = create_engine(f"sqlite:///{DB_PATH}")
    engine.dispose()

    if reset and DB_PATH.exists():
        try:
            DB_PATH.unlink()
        except PermissionError as e:
            print(f"⚠️ Unable to delete {DB_PATH}: {e}")
            print("⚠️ Attempting to force garbage collection.")
            gc.collect()
            DB_PATH.unlink()  # try again after GC

    # Recreate engine after deletion
    engine = create_engine(f"sqlite:///{DB_PATH}")
    Base.metadata.create_all(bind=engine)
    
    return engine
