from sqlalchemy import create_engine, text
from backend.core.config import settings

engine = create_engine(settings.DATABASE_URL)
try:
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE role_menus ADD COLUMN module_path VARCHAR(200) DEFAULT NULL AFTER sub_menu"))
        conn.commit()
    print("Column 'module_path' added successfully to 'role_menus' table.")
except Exception as e:
    print(f"Error adding column: {e}")
