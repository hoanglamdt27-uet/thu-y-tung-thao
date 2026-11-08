import os
import sys

# Ngăn Python tạo các file rác .pyc và thư mục __pycache__
sys.dont_write_bytecode = True
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"

import json
import time
from datetime import datetime, date, timedelta
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from services.config import AppConfig
from services.supabase_service import SupabaseService
from services.ai_service import AiService
from services.search_service import SearchService
from services.rag_service import RagService

app = FastAPI(
    title="Thú Y Tùng & Thảo — Hệ Thống Quản Lý Cửa Hàng & Phòng Khám",
    description="Backend API cho quản lý kho dược Supabase, hồ sơ bệnh án, doanh thu và Trí tuệ Nhân tạo",
    version="2.2.0"
)

# ── CORS Middleware ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Anti-Caching Middleware (Ensures browser NEVER caches old JS/CSS/HTML) ──
@app.middleware("http")
async def add_no_cache_headers(request: Request, call_next):
    response: Response = await call_next(request)
    # Cấm trình duyệt lưu cache để đảm bảo giao diện luôn nhận code mới nhất
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# ── Data Directories & Persistence ──
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
PATIENTS_FILE = os.path.join(DATA_DIR, "patients.json")
SALES_FILE = os.path.join(DATA_DIR, "sales.json")
GOAL_FILE = os.path.join(DATA_DIR, "goal.json")

try:
    os.makedirs(DATA_DIR, exist_ok=True)
except Exception:
    pass

def load_json(filepath: str, default):
    paths_to_try = [filepath]
    fname = os.path.basename(filepath)
    tmp_path = os.path.join("/tmp", "tytt_data", fname)
    if tmp_path != filepath:
        paths_to_try.append(tmp_path)

    for p in paths_to_try:
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
    return default

def save_json(filepath: str, data):
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except (OSError, PermissionError):
        # Fallback to /tmp in read-only Serverless environments (e.g. Vercel, AWS Lambda)
        try:
            fname = os.path.basename(filepath)
            tmp_dir = os.path.join("/tmp", "tytt_data")
            os.makedirs(tmp_dir, exist_ok=True)
            tmp_path = os.path.join(tmp_dir, fname)
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Fallback save failed for {filepath}: {e}")
            return False
    except Exception as e:
        print(f"Error saving {filepath}: {e}")
        return False

# Session consultation counter
runtime_consultation_count = 0

# ── Schemas ──
class LoginRequest(BaseModel):
    password: str

class ProductCreate(BaseModel):
    ma_sp: str
    ten_sp: str
    so_luong: int = 0
    gia_goc: int = 0
    gia_ban: int = 0

class ProductUpdate(BaseModel):
    ma_sp: Optional[str] = None
    ten_sp: Optional[str] = None
    so_luong: Optional[int] = None
    gia_goc: Optional[int] = None
    gia_ban: Optional[int] = None

class PatientCreate(BaseModel):
    owner_name: str
    phone: Optional[str] = ""
    animal_info: str
    diagnosis: str
    prescription: str
    followup_date: Optional[str] = ""
    status: Optional[str] = "Đang điều trị"
    notes: Optional[str] = ""

class SaleCreate(BaseModel):
    amount: int
    date: Optional[str] = None
    description: str
    category: Optional[str] = "Bán lẻ tại quầy"
    customer: Optional[str] = ""

class GoalUpdate(BaseModel):
    target: int

class ConsultRequest(BaseModel):
    query: str

class ShopeeRequest(BaseModel):
    product_name: str

class KeyUpdateRequest(BaseModel):
    api_key: str

class ModelUpdateRequest(BaseModel):
    model: str
    reasoning_effort: Optional[str] = "high"

# ── API Routes ──

@app.get("/api/health")
def get_health():
    """Kiểm tra trạng thái kết nối CSDL Supabase và AI Engine thực tế"""
    start = time.time()
    supabase_ok = False
    item_count = 0
    try:
        svc = SupabaseService()
        items = svc.get_inventory_records()
        supabase_ok = True
        item_count = len(items)
    except Exception as e:
        print(f"Health check error: {e}")

    latency_ms = int((time.time() - start) * 1000)
    has_ai = AppConfig.has_valid_openrouter_key()

    return {
        "status": "healthy" if (supabase_ok and has_ai) else "degraded",
        "supabase": {
            "connected": supabase_ok,
            "latency_ms": latency_ms,
            "total_items": item_count
        },
        "ai": {
            "has_key": has_ai,
            "model": AppConfig.get_current_model(),
            "reasoning_effort": AppConfig.get_reasoning_effort()
        },
        "timestamp": time.time()
    }

@app.post("/api/auth/login")
def admin_login(req: LoginRequest):
    """Xác thực mật khẩu Quản trị viên"""
    if AppConfig.verify_admin_password(req.password):
        token = f"admin_session_{int(time.time())}"
        return {"success": True, "token": token, "message": "Đăng nhập thành công"}
    raise HTTPException(status_code=401, detail="Mật khẩu quản trị không chính xác")

# ── Stats & Revenue (100% Real Data, Zero Hallucination) ──

@app.get("/api/stats")
def get_dashboard_stats():
    """
    Tính toán chỉ số thực tế từ Supabase và nhật ký bán hàng:
    - Nếu chưa có hóa đơn bán hàng: doanh thu hiển thị 0 đ (trung thực, không bịa số liệu).
    - Tồn kho và cảnh báo lấy trực tiếp từ Supabase PostgreSQL.
    """
    global runtime_consultation_count

    # 1. Supabase Inventory
    svc = SupabaseService()
    items = svc.get_inventory_records()
    total_products = len(items)
    total_quantity = sum(int(x.get("so_luong") or 0) for x in items)
    total_value = sum(int(x.get("so_luong") or 0) * int(x.get("gia_ban") or 0) for x in items)
    low_stock_items = [x for x in items if int(x.get("so_luong") or 0) <= 5]

    # 2. Real Sales Transactions
    sales = load_json(SALES_FILE, [])
    today_str = date.today().isoformat()
    seven_days_ago = (date.today() - timedelta(days=7)).isoformat()
    first_day_month = date.today().replace(day=1).isoformat()

    today_revenue = 0
    week_revenue = 0
    month_revenue = 0
    daily_sales_map = {}

    for s in sales:
        s_date = s.get("date", "")
        amt = int(s.get("amount") or 0)
        
        if s_date == today_str:
            today_revenue += amt
        if s_date >= seven_days_ago:
            week_revenue += amt
        if s_date >= first_day_month:
            month_revenue += amt

        # Aggregate daily for chart
        daily_sales_map[s_date] = daily_sales_map.get(s_date, 0) + amt

    # Format chart points (EMPTY if no sales!)
    chart_points = []
    if len(sales) > 0:
        sorted_dates = sorted(daily_sales_map.keys())
        for d in sorted_dates:
            chart_points.append({
                "date": d,
                "label": datetime.strptime(d, "%Y-%m-%d").strftime("%d/%m") if len(d) == 10 else d,
                "amount": daily_sales_map[d]
            })

    # 3. Monthly Goal
    goal_data = load_json(GOAL_FILE, {"target": 50000000})
    monthly_target = goal_data.get("target", 50000000)
    goal_percent = min(100, int((month_revenue / monthly_target) * 100)) if monthly_target > 0 else 0

    # 4. Patients
    patients = load_json(PATIENTS_FILE, [])

    # Find top product by quantity in inventory
    top_product_name = items[0]["ten_sp"] if items else "Chưa có sản phẩm"

    return {
        "today_revenue": today_revenue,
        "week_revenue": week_revenue,
        "month_revenue": month_revenue,
        "has_sales_data": len(sales) > 0,
        "chart_points": chart_points,
        "total_products": total_products,
        "total_quantity": total_quantity,
        "total_value": total_value,
        "low_stock_count": len(low_stock_items),
        "low_stock_items": low_stock_items,
        "live_visitors": 1,
        "is_web_analytics_live": False,
        "monthly_goal_target": monthly_target,
        "monthly_goal_recorded": month_revenue,
        "goal_progress_percent": goal_percent,
        "total_patients": len(patients),
        "session_consultations": runtime_consultation_count,
        "top_inventory_product": top_product_name
    }

# ── Sales / Revenue Endpoints ──

@app.get("/api/sales")
def get_sales():
    """Lấy danh sách các giao dịch bán hàng / đơn thuốc thực tế"""
    return load_json(SALES_FILE, [])

@app.post("/api/sales")
def create_sale(req: SaleCreate):
    """Ghi nhận một đơn bán hàng / doanh thu thực tế"""
    sales = load_json(SALES_FILE, [])
    sale_date = req.date if (req.date and req.date.strip()) else date.today().isoformat()
    new_sale = {
        "id": int(time.time() * 1000),
        "amount": int(req.amount),
        "date": sale_date,
        "description": req.description.strip(),
        "category": req.category or "Bán lẻ tại quầy",
        "customer": req.customer or "Khách lẻ",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    sales.insert(0, new_sale)
    save_json(SALES_FILE, sales)
    return {"success": True, "data": new_sale}

@app.delete("/api/sales/{sale_id}")
def delete_sale(sale_id: int):
    """Xóa một giao dịch bán hàng theo ID"""
    sales = load_json(SALES_FILE, [])
    filtered = [s for s in sales if s.get("id") != sale_id]
    save_json(SALES_FILE, filtered)
    return {"success": True}

# ── Goal Target Endpoints ──

@app.post("/api/goal")
def update_goal(req: GoalUpdate):
    """Cập nhật chỉ tiêu doanh thu tháng"""
    save_json(GOAL_FILE, {"target": int(req.target)})
    return {"success": True, "target": int(req.target)}

# ── Patient Records (Hồ Sơ Bệnh Án Thực Tế) ──

@app.get("/api/patients")
def get_patients():
    """Lấy danh sách hồ sơ bệnh án vật nuôi thực tế (Bắt đầu từ rỗng, không bịa đặt)"""
    return load_json(PATIENTS_FILE, [])

@app.post("/api/patients")
def create_patient(req: PatientCreate):
    """Lập một hồ sơ bệnh án mới cho ca điều trị thực tế"""
    if not req.owner_name.strip() or not req.animal_info.strip():
        raise HTTPException(status_code=400, detail="Vui lòng nhập tên chủ nuôi và thông tin vật nuôi")

    patients = load_json(PATIENTS_FILE, [])
    new_patient = {
        "id": int(time.time() * 1000),
        "owner_name": req.owner_name.strip(),
        "phone": req.phone.strip() if req.phone else "",
        "animal_info": req.animal_info.strip(),
        "diagnosis": req.diagnosis.strip(),
        "prescription": req.prescription.strip(),
        "followup_date": req.followup_date.strip() if req.followup_date else "",
        "status": req.status or "Đang điều trị",
        "notes": req.notes.strip() if req.notes else "",
        "created_at": datetime.now().strftime("%d/%m/%Y %H:%M")
    }
    patients.insert(0, new_patient)
    save_json(PATIENTS_FILE, patients)
    return {"success": True, "data": new_patient}

@app.delete("/api/patients/{patient_id}")
def delete_patient(patient_id: int):
    """Xóa hồ sơ bệnh án theo ID"""
    patients = load_json(PATIENTS_FILE, [])
    filtered = [p for p in patients if p.get("id") != patient_id]
    save_json(PATIENTS_FILE, filtered)
    return {"success": True}

# ── Global Search Endpoint with Smart Keyword & Navigation Matching ──

@app.get("/api/search")
def global_search(q: str):
    """
    Tìm kiếm thông minh toàn hệ thống:
    - Điều hướng phân hệ (ví dụ: gõ "hồ sơ", "bệnh án", "kho", "doanh thu", "bác sĩ")
    - Kho dược Supabase (theo tên hoặc mã SP)
    - Hồ sơ bệnh án (theo tên chủ, vật nuôi, chẩn đoán)
    - Kho tri thức lâm sàng (theo triệu chứng / bệnh học)
    """
    query = (q or "").strip().lower()
    if not query:
        return {"nav": [], "inventory": [], "patients": [], "knowledge": []}

    nav_results = []
    # 1. Navigation intent matches
    if any(k in query for k in ["hồ sơ", "bệnh án", "benh an", "ho so", "ca bệnh"]):
        nav_results.append({
            "type": "nav",
            "target": "patients",
            "title": "Hồ Sơ Bệnh Án Vật Nuôi",
            "subtitle": "Mở phân hệ quản lý lịch sử điều trị và danh sách ca bệnh",
            "icon": "paw-print"
        })
    if any(k in query for k in ["kho", "thuốc", "dược", "san pham", "sản phẩm", "tồn kho"]):
        nav_results.append({
            "type": "nav",
            "target": "inventory",
            "title": "Kho Dược Supabase Cloud",
            "subtitle": "Mở bảng quản lý tồn kho và danh mục thuốc",
            "icon": "package"
        })
    if any(k in query for k in ["doanh thu", "tiền", "sổ quỹ", "bán hàng", "hóa đơn", "so quy"]):
        nav_results.append({
            "type": "nav",
            "target": "sales",
            "title": "Sổ Quỹ & Doanh Thu Bán Hàng",
            "subtitle": "Mở nhật ký giao dịch và lịch sử xuất bán",
            "icon": "dollar-sign"
        })
    if any(k in query for k in ["bác sĩ", "phác đồ", "ai", "tư vấn", "chẩn đoán", "rag"]):
        nav_results.append({
            "type": "nav",
            "target": "rag",
            "title": "Bác Sĩ Ảo & Phác Đồ RAG",
            "subtitle": "Mở trợ lý chẩn đoán và hướng dẫn liều dùng",
            "icon": "bot"
        })
    if any(k in query for k in ["shopee", "seo", "bài đăng", "bài viết"]):
        nav_results.append({
            "type": "nav",
            "target": "shopee",
            "title": "Soạn Bài Đăng Shopee SEO",
            "subtitle": "Mở công cụ tự động viết bài sàn TMĐT",
            "icon": "shopping-bag"
        })

    # 2. Search Inventory
    svc = SupabaseService()
    items = svc.get_inventory_records()
    matched_inventory = [
        item for item in items
        if query in (item.get("ten_sp") or "").lower() or query in (item.get("ma_sp") or "").lower()
    ][:6]

    # 3. Search Patients
    patients = load_json(PATIENTS_FILE, [])
    matched_patients = [
        p for p in patients
        if query in (p.get("owner_name") or "").lower() or 
           query in (p.get("animal_info") or "").lower() or
           query in (p.get("diagnosis") or "").lower() or
           query in (p.get("prescription") or "").lower()
    ][:6]

    # 4. Search Knowledge Base
    kb_context = RagService.find_relevant_context(query)
    matched_kb = []
    if kb_context and "Chưa có dữ liệu" not in kb_context:
        blocks = [b.strip() for b in kb_context.split("===") if b.strip()]
        for b in blocks[:3]:
            lines = b.splitlines()
            title = lines[0].strip() if lines else "Tài liệu phác đồ"
            matched_kb.append({"title": title, "snippet": b[:150] + "..."})

    return {
        "nav": nav_results,
        "inventory": matched_inventory,
        "patients": matched_patients,
        "knowledge": matched_kb
    }

# ── Inventory Endpoints ──

@app.get("/api/inventory")
def get_inventory():
    """Lấy danh sách kho hàng đầy đủ từ Supabase Cloud"""
    svc = SupabaseService()
    return svc.get_inventory_records()

@app.post("/api/inventory")
def create_product(product: ProductCreate):
    """Thêm sản phẩm mới vào Supabase"""
    svc = SupabaseService()
    try:
        new_item = svc.add_product(
            ma_sp=product.ma_sp,
            ten_sp=product.ten_sp,
            so_luong=product.so_luong,
            gia_goc=product.gia_goc,
            gia_ban=product.gia_ban
        )
        return {"success": True, "data": new_item}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/inventory/{product_id}")
def update_product(product_id: int, updates: ProductUpdate):
    """Cập nhật sản phẩm theo ID"""
    svc = SupabaseService()
    try:
        clean = {k: v for k, v in updates.model_dump().items() if v is not None}
        ok = svc.update_product(product_id, clean)
        return {"success": ok}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/inventory/{product_id}")
def delete_product(product_id: int):
    """Xóa sản phẩm theo ID"""
    svc = SupabaseService()
    try:
        ok = svc.delete_product(product_id)
        return {"success": ok}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ── AI Endpoints ──

@app.post("/api/ai/consult")
def ai_consult(req: ConsultRequest):
    """Bác sĩ Thú y AI & RAG tư vấn phác đồ điều trị"""
    global runtime_consultation_count
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Vui lòng nhập triệu chứng")

    runtime_consultation_count += 1
    answer = AiService.consult_rag(req.query.strip())
    context = RagService.find_relevant_context(req.query.strip())

    return {
        "answer": answer,
        "matched_context": context,
        "model": AppConfig.get_current_model(),
        "reasoning_effort": AppConfig.get_reasoning_effort()
    }

@app.post("/api/ai/shopee")
def generate_shopee_post(req: ShopeeRequest):
    """Thu thập thông tin nhà sản xuất & tạo bài đăng Shopee chuẩn SEO an toàn"""
    name = req.product_name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Vui lòng nhập tên sản phẩm")

    web_info = SearchService.fetch_veterinary_info(name)
    content = AiService.generate_shopee_content(name, web_info)
    RagService.save_product_knowledge(name, web_info)

    return {
        "product_name": name,
        "technical_info": web_info,
        "shopee_content": content,
        "saved_to_kb": True
    }

@app.get("/api/settings")
def get_settings():
    """Lấy toàn bộ thông tin cấu hình hiện tại"""
    key = AppConfig.get_openrouter_api_key()
    masked_key = (key[:8] + "..." + key[-4:]) if len(key) > 12 else ("Đã cấu hình" if key else "Chưa cấu hình")
    sb_url, _ = AppConfig.get_supabase_credentials()
    return {
        "supabase_url": sb_url,
        "openrouter_key_masked": masked_key,
        "has_openrouter_key": bool(key),
        "current_model": AppConfig.get_current_model(),
        "reasoning_effort": AppConfig.get_reasoning_effort()
    }

@app.post("/api/settings/key")
def update_api_key(req: KeyUpdateRequest):
    """Cập nhật API Key trong phiên làm việc"""
    if not req.api_key.strip():
        raise HTTPException(status_code=400, detail="Key không được để trống")
    AppConfig.set_runtime_openrouter_key(req.api_key.strip())
    return {"success": True, "message": "Đã lưu API Key cho phiên làm việc"}

@app.post("/api/settings/model")
def update_model(req: ModelUpdateRequest):
    """Chuyển đổi mô hình AI và mức độ suy luận lâm sàng"""
    model_name = req.model.strip()
    if not model_name:
        raise HTTPException(status_code=400, detail="Tên model không được để trống")
    AppConfig.set_current_model(model_name)
    if req.reasoning_effort:
        AppConfig.set_reasoning_effort(req.reasoning_effort)
    return {
        "success": True,
        "model": AppConfig.get_current_model(),
        "reasoning_effort": AppConfig.get_reasoning_effort(),
        "message": f"Đã chuyển sang model: {AppConfig.get_current_model()} ({AppConfig.get_reasoning_effort()})"
    }

# ── Static Web Serving with Dynamic Cache-Buster & Anti-Cache Headers ──
web_dir = os.path.join(os.path.dirname(__file__), "web")
if os.path.exists(web_dir):
    from fastapi.responses import HTMLResponse
    import time
    import mimetypes
    import re

    @app.get("/static/{file_path:path}")
    def serve_static(file_path: str):
        full_path = os.path.join(web_dir, file_path)
        if not os.path.exists(full_path):
            raise HTTPException(status_code=404, detail="File not found")
        mime_type, _ = mimetypes.guess_type(full_path)
        response = FileResponse(full_path, media_type=mime_type or "application/octet-stream")
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

    @app.get("/")
    def serve_frontend():
        index_file = os.path.join(web_dir, "index.html")
        with open(index_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Dynamic cache-buster timestamp: changes on every request
        cache_id = str(int(time.time() * 1000))
        content = re.sub(r'/static/app\.js(\?v=[^"\'\s>]*)?', f'/static/app.js?v={cache_id}', content)
        content = re.sub(r'/static/styles\.css(\?v=[^"\'\s>]*)?', f'/static/styles.css?v={cache_id}', content)

        return HTMLResponse(
            content=content,
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate, max-age=0",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )

    app.mount("/static", StaticFiles(directory=web_dir), name="static")
