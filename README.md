# HE THONG QUAN TRI NOI BO - THU Y TUNG THAO

## 1. Cau truc thu muc
- `backend.py`: Chua lop `BackendService` xu ly ket noi CSDL Supabase, cào du lieu web (DuckDuckGo), doc/ghi file tri thuc RAG va goi API OpenRouter.
- `app.py`: Giao dien nguoi dung (Frontend) xay dung bang Streamlit ket hop CSS tuy chinh do tuong phan cao, khong su dung icon, khong loi font.
- `knowledge_base.txt`: File luu tru du lieu phac do va thong tin thuoc noi bo.

## 2. Cai dat thu vien
Chay lenh sau tren Terminal:
pip install streamlit pandas openai supabase duckduckgo-search

## 3. Khoi chay ung dung
Chay lenh sau de mo giao dien web:
python -m streamlit run app.py
