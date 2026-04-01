import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from backend.core.security import create_access_token
import requests

token = create_access_token({"sub": "admin"})
resp = requests.get("http://127.0.0.1:8000/role-menus", headers={"Authorization": f"Bearer {token}"})
print(resp.status_code)
print(resp.text)
