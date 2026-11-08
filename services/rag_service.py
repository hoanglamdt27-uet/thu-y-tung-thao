import os
import re

class RagService:
    """Quản lý kho tri thức nội bộ và truy xuất tài liệu phác đồ (RAG with Synonym Expansion)"""

    KB_FILE = "knowledge_base.txt"

    # Từ điển đồng nghĩa thú y để mở rộng truy vấn thông minh
    SYNONYMS = {
        "khò khè": ["hen", "crd", "ccrd", "thở gấp", "viêm phổi", "ngáp", "bromhexine"],
        "hen": ["khò khè", "crd", "hô hấp", "viêm phế quản"],
        "tiêu chảy": ["phân trắng", "phân xanh", "ỉa chảy", "mất nước", "viêm ruột", "fer b12"],
        "vịt": ["ngan", "bại huyết", "bơi xoay vòng", "lắc đầu"],
        "heo": ["lợn", "heo con", "cai sữa", "thiếu máu", "fer b12"],
        "chó": ["parvo", "care", "nôn", "ói mửa", "đi cầu ra máu"],
        "ruồi": ["nhặng", "muỗi", "côn trùng", "sakan"],
        "sát trùng": ["povidine", "tiêu độc", "sát khuẩn", "khử trùng"],
        "chống nóng": ["gluco k-c", "điện giải", "hạ sốt", "mất nước"],
    }

    @classmethod
    def load_all_knowledge(cls) -> str:
        """Đọc toàn bộ file tri thức nội bộ"""
        if os.path.exists(cls.KB_FILE):
            try:
                with open(cls.KB_FILE, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        return content
            except Exception as e:
                print(f"[RagService] Lỗi đọc file tri thức: {e}")
        return "Kho tri thức nội bộ hiện chưa có dữ liệu."

    @classmethod
    def find_relevant_context(cls, user_query: str) -> str:
        """
        Trích xuất ngữ cảnh liên quan đến câu hỏi:
        - Tách các khối sản phẩm / phác đồ bắt đầu bằng '==='
        - Mở rộng từ khóa thông qua từ điển đồng nghĩa thú y
        - Tính điểm tương quan và chọn các khối sát nhất
        """
        all_content = cls.load_all_knowledge()
        if "Chưa có dữ liệu" in all_content:
            return all_content

        blocks = re.split(r"(?====\s*(?:SẢN PHẨM|PHÁC ĐỒ):)", all_content)
        cleaned_blocks = [b.strip() for b in blocks if b.strip()]

        if not cleaned_blocks:
            return all_content

        # Tách từ khóa và mở rộng đồng nghĩa
        query_lower = user_query.lower()
        query_words = set(re.findall(r"\w+", query_lower))
        expanded_keywords = set(query_words)

        for key, syns in cls.SYNONYMS.items():
            if key in query_lower:
                expanded_keywords.update(syns)
            for syn in syns:
                if syn in query_lower:
                    expanded_keywords.add(key)
                    expanded_keywords.update(syns)

        matched_blocks = []
        for block in cleaned_blocks:
            block_lower = block.lower()
            score = 0
            for w in expanded_keywords:
                if len(w) > 2 and w in block_lower:
                    # Tăng trọng số nếu từ khóa gốc của người dùng xuất hiện
                    weight = 2 if w in query_words else 1
                    score += weight

            if score > 0:
                matched_blocks.append((score, block))

        if matched_blocks:
            matched_blocks.sort(key=lambda x: x[0], reverse=True)
            return "\n\n".join([b[1] for b in matched_blocks[:3]])

        return "\n\n".join(cleaned_blocks[:2])

    @classmethod
    def save_product_knowledge(cls, product_name: str, technical_info: str) -> bool:
        """Lưu trữ thông tin sản phẩm mới vào kho tri thức"""
        if not technical_info or "Không tìm thấy" in technical_info or "Không thể tra cứu" in technical_info:
            return False

        header = f"=== SẢN PHẨM: {product_name.strip().upper()} ==="
        all_content = cls.load_all_knowledge()

        if header in all_content:
            return False

        try:
            with open(cls.KB_FILE, "a", encoding="utf-8") as f:
                f.write(f"\n\n{header}\n{technical_info.strip()}\n")
            return True
        except Exception as e:
            print(f"[RagService] Lỗi lưu tri thức: {e}")
            return False
