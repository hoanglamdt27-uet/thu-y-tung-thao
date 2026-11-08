import sys
import os

# Thêm thư mục gốc vào đường dẫn hệ thống để import backend_api và services
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Import FastAPI instance
from backend_api import app

# Vercel Serverless Function nhận diện biến `app` (ASGI application)

