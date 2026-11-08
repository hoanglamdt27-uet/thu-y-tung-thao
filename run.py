#!/usr/bin/env python3
"""
Launcher — Hệ Thống Quản Lý Thú Y Tùng & Thảo
Giao diện Web App Hiện Đại (Dark Luxury Glassmorphism)
"""

import sys
import os
import subprocess

# Cấm tạo file rác .pyc và __pycache__
sys.dont_write_bytecode = True
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"

def main():
    print("=" * 60)
    print("🚀 ĐANG KHỞI CHẠY HỆ THỐNG QUẢN LÝ THÚ Y TÙNG & THẢO")
    print("Giao diện: Modern Dark Luxury Glassmorphism (@_code_and_chill_)")
    print("=" * 60)
    print("Máy chủ đang hoạt động tại: http://localhost:8000")
    print("Nhấn Ctrl + C để dừng máy chủ.\n")
    try:
        import uvicorn
        uvicorn.run("backend_api:app", host="0.0.0.0", port=8000, reload=True)
    except ImportError:
        subprocess.run([sys.executable, "-m", "uvicorn", "backend_api:app", "--host", "0.0.0.0", "--port", "8000", "--reload"])

if __name__ == "__main__":
    main()
