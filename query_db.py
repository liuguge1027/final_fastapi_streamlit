from backend.db.database import SessionLocal
from backend.models.role_menu import RoleMenu

db = SessionLocal()
results = db.query(RoleMenu).all()
print(f"Total rows: {len(results)}")
for r in results:
    print(r)
