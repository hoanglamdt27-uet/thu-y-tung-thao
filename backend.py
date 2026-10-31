import os
import pandas as pd
import streamlit as st
from openai import OpenAI
from supabase import create_client, Client
from duckduckgo_search import DDGS

# LUÔN ĐỌC TỪ SECRETS, TUYỆT ĐỐI KHÔNG DÁN KEY THẬT TRỰC TIẾP VÀO ĐÂY
try:
    OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
except Exception:
    OPENROUTER_API_KEY = "placeholder_key"
    SUPABASE_URL = "https://hduatpmcxlbaqwachhju.supabase.co"
    SUPABASE_KEY = "sb_publishable_Un7ci74dqscf0yEGfmJBkQ_4ZM4LP_B"

MODEL_NAME = "google/gemini-2.5-flash"

class BackendService:
    def __init__(self):
        self.ai_client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API_KEY
        )
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.kb_file = "knowledge_base.txt"

    def load_knowledge_base(self):
        if os.path.exists(self.kb_file):
            with open(self.kb_file, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    return content
        return "Chưa có dữ liệu trong kho tri thức nội bộ."

    def save_to_knowledge_base(self, product_name, web_info):
        if web_info and "Không tìm thấy" not in web_info and "Lỗi" not in web_info:
            with open(self.kb_file, "a", encoding="utf-8") as f:
                f.write(f"\n\n=== SẢN PHẨM: {product_name.upper()} ===\n")
                f.write(web_info)
            return True
        return False

    def consult_rag(self, user_query):
        kb_data = self.load_knowledge_base()
        prompt_rag = (
            f"CƠ SỞ TRI THỨC NỘI BỘ:\n{kb_data}\n\n"
            f"CÂU HỎI KHÁCH HÀNG:\n{user_query}\n\n"
            "Nhiệm vụ: Trả lời chi tiết, rõ ràng bằng tiếng Việt có dấu dựa trên CƠ SỞ TRI THỨC NỘI BỘ. "
            "Nếu thông tin chưa có trong kho tri thức, hãy gợi ý phác đồ thú y tiêu chuẩn và ghi chú rõ cho người dùng biết."
        )
        response = self.ai_client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "Bạn là chuyên gia kỹ thuật thú y của cửa hàng Thú Y Tùng & Thảo."},
                {"role": "user", "content": prompt_rag}
            ],
            max_tokens=1200
        )
        return response.choices[0].message.content

    def fetch_web_data(self, product_name):
        try:
            web_info = ""
            with DDGS() as ddgs:
                results = list(ddgs.text(f"{product_name} thuốc thú y thành phần công dụng liều dùng", max_results=3))
                if results:
                    web_info = "\n\n".join([f"- {r['title']}: {r['body']}" for r in results])
            if not web_info:
                return "Không tìm thấy thông tin trên mạng."
            return web_info
        except Exception as e:
            return f"Lỗi thu thập dữ liệu web: {str(e)}"

    def generate_shopee_content(self, product_name, web_info):
        prompt = (
            f"Thông tin kỹ thuật thu thập từ nhà sản xuất:\n{web_info}\n\n"
            f"Hãy viết một bài mô tả sản phẩm chuẩn SEO trên sàn Shopee cho cửa hàng Thú Y Tùng & Thảo về sản phẩm: {product_name}.\n"
            "YÊU CẦU BẮT BUỘC: Trình bày rõ ràng bằng tiếng Việt có dấu, chia bố cục gồm Tên sản phẩm, Thành phần, Công dụng, Liều lượng và Cam kết của cửa hàng. "
            "Tuyệt đối KHÔNG dùng các từ vi phạm chính sách sàn như: 'đặc trị', 'chữa bệnh', 'kháng sinh', 'cam kết khỏi 100%'. "
            "Hãy thay thế bằng các từ an toàn như: 'hỗ trợ cải thiện', 'bổ trợ sức khỏe', 'chế phẩm sinh học', 'tăng cường sức đề kháng'."
        )
        response = self.ai_client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "Bạn là chuyên gia viết nội dung thương mại điện tử ngành thú y."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1200
        )
        return response.choices[0].message.content

    def get_inventory(self):
        res = self.supabase.table('inventory').select('*').order('id').execute()
        data = res.data
        if not data:
            return pd.DataFrame(columns=["id", "created_at", "ma_sp", "ten_sp", "so_luong", "gia_goc", "gia_ban"])
        return pd.DataFrame(data)

    def sync_inventory(self, original_df, edited_df):
        if not original_df.empty and "id" in original_df.columns:
            original_ids = set(original_df["id"].dropna().astype(int).tolist())
        else:
            original_ids = set()

        if not edited_df.empty and "id" in edited_df.columns:
            current_ids = set(edited_df["id"].dropna().astype(int).tolist())
        else:
            current_ids = set()

        deleted_ids = list(original_ids - current_ids)
        if deleted_ids:
            self.supabase.table('inventory').delete().in_('id', deleted_ids).execute()

        records = edited_df.to_dict('records')
        for row in records:
            clean_row = {k: v for k, v in row.items() if not pd.isna(v)}
            if not clean_row:
                continue
            if "id" in clean_row and clean_row["id"] is not None:
                clean_row["id"] = int(clean_row["id"])
                self.supabase.table('inventory').upsert(clean_row).execute()
            else:
                clean_row.pop("id", None)
                clean_row.pop("created_at", None)
                self.supabase.table('inventory').insert(clean_row).execute()
        return True

    def update_product_quantity(self, product_id, new_quantity):
        self.supabase.table('inventory').update({"so_luong": int(new_quantity)}).eq("id", int(product_id)).execute()
        return True