# HỆ THỐNG QUẢN TRỊ NỘI BỘ — THÚ Y TÙNG & THẢO

Trung tâm quản trị cửa hàng dược thú y và phòng khám lâm sàng hiện đại, tích hợp cơ sở dữ liệu đám mây Supabase Cloud, trợ lý chẩn đoán lâm sàng RAG AI với mô hình **Gemini 3.8 Flash (High Reasoning)**, và công cụ soạn bài đăng Shopee chuẩn SEO thuần Plain Text (không dính ký tự markdown).

---

## 1. Công Nghệ & Kiến Trúc

- **Giao diện người dùng (Frontend):** Modern Dark Luxury Glassmorphism (lấy cảm hứng từ phong cách `@_code_and_chill_`), hiệu ứng Mesh Gradient Glow phát quang, Tailwind CSS, Lucide Icons, Chart.js.
- **Máy chủ ứng dụng (Backend):** FastAPI + Uvicorn Server hiệu năng cao, cơ chế chống cache trình duyệt tự động (Anti-Cache Timestamp Headers).
- **Cơ sở dữ liệu:** Supabase PostgreSQL Cloud (đồng bộ 2 chiều dữ liệu kho dược).
- **Trí tuệ nhân tạo (AI Engine):** Mô hình `google/gemini-3.8-flash` với chế độ suy luận y khoa chuyên sâu `Reasoning Effort: High` qua OpenRouter API.
- **Kho tri thức lâm sàng:** RAG Retrieval-Augmented Generation với từ điển đồng nghĩa thú y chuyên sâu (gia cầm, thủy cầm, heo, chó mèo).

---

## 2. Hướng Dẫn Khởi Chạy Local

Chạy lệnh sau trên Terminal để khởi động hệ thống trên máy tính:

```bash
python run.py
```

- Truy cập ứng dụng tại: **`http://localhost:8000`**
- **Tài khoản Quản trị viên:**
  - Mật khẩu mặc định: `admin` (có thể đổi trong `secrets.toml`, tab Cài đặt hoặc qua biến môi trường `ADMIN_PASSWORD`).

---

## 3. Hướng Dẫn Deploy Lên Cloud Miễn Phí & Tốc Độ Cao (Không dùng Streamlit)

> **Vì sao không dùng Streamlit Cloud?**
> Streamlit Cloud thường bị "ngủ đông" (cold start mất 30–60s), xử lý websocket giật lag và máy chủ đặt ở Mỹ (ping 250–350ms).
> Kiến trúc mới FastAPI + Static Edge của hệ thống cho phép bạn đưa lên các nền tảng đám mây hiện đại với tốc độ mở trang siêu tốc (~20ms tại Việt Nam).

### 🚀 LỰA CHỌN 1: Deploy Vercel Serverless (Khuyên dùng - Nhanh nhất cho Việt Nam, Miễn phí 100%)
Vercel có mạng lưới Edge CDN đặt tại **Singapore** và **Hồng Kông**, ping về Việt Nam chỉ mất 20–35ms. Khởi động 0 giây, không có độ trễ:

1. Đẩy code lên GitHub:
   ```bash
   git add .
   git commit -m "Deploy Thu Y Tung Thao web & admin login"
   git push origin main
   ```
2. Truy cập [vercel.com](https://vercel.com) và đăng nhập bằng tài khoản GitHub.
3. Chọn **Add New...** -> **Project** -> Chọn repository `thu-y-tung-thao`.
4. Trong phần **Environment Variables**, thêm các biến sau:
   - `OPENROUTER_API_KEY`: *(Key OpenRouter của bạn)*
   - `ADMIN_PASSWORD`: `admin` *(hoặc mật khẩu bạn muốn)*
   - `SUPABASE_URL`: `https://hduatpmcxlbaqwachhju.supabase.co`
   - `SUPABASE_KEY`: `sb_publishable_Un7ci74dqscf0yEGfmJBkQ_4ZM4LP_B`
5. Bấm **Deploy**. Sau ~30 giây, website của bạn sẽ hoạt động tại link `https://thu-y-tung-thao.vercel.app` với chứng chỉ SSL miễn phí vĩnh viễn!

---

### 🌐 LỰA CHỌN 2: Deploy Render.com (Miễn phí 100%, Độc lập)
Dành cho máy chủ FastAPI chạy liên tục:

1. Đăng nhập [render.com](https://render.com) bằng tài khoản GitHub.
2. Chọn **New** -> **Web Service** -> Chọn repository `thu-y-tung-thao`.
3. Cấu hình:
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn backend_api:app --host 0.0.0.0 --port $PORT`
4. Trong mục **Advanced** -> Thêm `Environment Variables` (`OPENROUTER_API_KEY`, `ADMIN_PASSWORD`, v.v.).
5. Bấm **Create Web Service**.

---

### 🐳 LỰA CHỌN 3: Deploy Bằng Docker (Koyeb / Railway / Fly.io / VPS)
Dự án đã tích hợp sẵn `Dockerfile` chuẩn Production siêu nhẹ (python:3.11-slim):

```bash
docker build -t thu-y-tung-thao .
docker run -d -p 8000:8000 -e ADMIN_PASSWORD=admin -e OPENROUTER_API_KEY=your_key thu-y-tung-thao
```
Trên **Koyeb.com**, bạn chỉ cần chọn GitHub repo và Koyeb sẽ tự động build từ Dockerfile với datacenter tại Singapore (miễn phí 2 nano container).

---

## 4. Cấu Trúc Thư Mục

```text
thu-y-tung-thao/
│
├── backend_api.py            # FastAPI Server: REST API cho Supabase, AI RAG, Shopee, Sổ quỹ & Tìm kiếm
├── run.py                    # Launcher khởi chạy máy chủ FastAPI (Port 8000)
├── secrets.toml              # File cấu hình bảo mật API Key & Supabase (Không đẩy lên Git)
│
├── web/                      # GIAO DIỆN HIỆN ĐẠI
│   ├── index.html            # Giao diện chính: Dashboard, Kho hàng, Bệnh án, Sổ quỹ, RAG, Shopee, Cài đặt
│   ├── styles.css            # Hiệu ứng kính mờ Glassmorphism, Mesh Glow Orbs, Equalizer animation
│   └── app.js                # Xử lý sự kiện, Modal popups, Tìm kiếm thông minh Enter, Chart.js
│
├── services/                 # CÁC DỊCH VỤ BACKEND ĐỘC LẬP
│   ├── config.py             # Quản lý cấu hình tập trung (Đọc secrets.toml bằng tomllib)
│   ├── supabase_service.py   # Quản lý CSDL Supabase (Batch sync, singleton client, bảo mật giá gốc)
│   ├── ai_service.py         # Kết nối OpenRouter (Gemini 3.8 Flash High Reasoning, bộ lọc Plain Text Shopee)
│   ├── search_service.py     # Tra cứu dữ liệu hoạt chất dược có bộ lọc tạp âm & fallback
│   └── rag_service.py        # Vector / Keyword RAG tìm kiếm triệu chứng bệnh học
│
├── data/                     # DỮ LIỆU CỬA HÀNG THỰC TẾ
│   ├── sales.json            # Nhật ký giao dịch sổ quỹ doanh thu thực
│   ├── patients.json         # Danh sách hồ sơ bệnh án vật nuôi thực
│   └── goal.json             # Chỉ tiêu doanh thu tháng của phòng khám
│
├── knowledge_base.txt        # Dữ liệu phác đồ điều trị và tài liệu sản phẩm nội bộ
└── requirements.txt          # Danh mục thư viện Python yêu cầu
```
