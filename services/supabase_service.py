import pandas as pd
from supabase import create_client, Client
from .config import AppConfig


class SupabaseService:
    """Xử lý giao tiếp CSDL đám mây Supabase tối ưu (Batch processing & Fast API support)"""

    _instance_client = None

    def __init__(self):
        url, key = AppConfig.get_supabase_credentials()
        # Singleton client reuse to avoid repeated TCP handshakes
        if SupabaseService._instance_client is None:
            SupabaseService._instance_client = create_client(url, key)
        self.client: Client = SupabaseService._instance_client

    def get_inventory_records(self) -> list[dict]:
        """Lấy toàn bộ dữ liệu kho hàng dưới dạng list of dicts cho REST API"""
        try:
            res = self.client.table('inventory').select('*').order('id').execute()
            return res.data or []
        except Exception as e:
            print(f"[SupabaseService] Lỗi get_inventory_records: {e}")
            return []

    def get_inventory(self) -> pd.DataFrame:
        """Lấy toàn bộ dữ liệu kho hàng (Dành cho Quản trị viên dạng DataFrame)"""
        data = self.get_inventory_records()
        if not data:
            return pd.DataFrame(columns=["id", "created_at", "ma_sp", "ten_sp", "so_luong", "gia_goc", "gia_ban"])
        return pd.DataFrame(data)

    def get_public_catalog_records(self) -> list[dict]:
        """
        Lấy danh mục sản phẩm công khai dành cho Khách hàng:
        - BẢO MẬT: Ẩn hoàn toàn giá gốc (gia_goc)
        - Chỉ trả về: ma_sp, ten_sp, gia_ban, trang_thai
        """
        raw = self.get_inventory_records()
        public_list = []
        for item in raw:
            qty = item.get("so_luong")
            try:
                q = int(qty) if qty is not None else 0
                if q > 10:
                    status = "Còn hàng"
                elif q > 0:
                    status = "Sắp hết hàng"
                else:
                    status = "Tạm hết hàng"
            except Exception:
                status = "Liên hệ quầy"

            public_list.append({
                "id": item.get("id"),
                "ma_sp": item.get("ma_sp", ""),
                "ten_sp": item.get("ten_sp", ""),
                "gia_ban": int(item.get("gia_ban") or 0),
                "trang_thai": status,
            })
        return public_list

    def get_public_catalog(self) -> pd.DataFrame:
        """Lấy danh mục sản phẩm công khai dưới dạng DataFrame"""
        records = self.get_public_catalog_records()
        if not records:
            return pd.DataFrame(columns=["ma_sp", "ten_sp", "gia_ban", "trang_thai"])
        return pd.DataFrame(records)

    def add_product(self, ma_sp: str, ten_sp: str, so_luong: int = 0, gia_goc: int = 0, gia_ban: int = 0) -> dict:
        """Thêm mới một sản phẩm vào kho"""
        payload = {
            "ma_sp": str(ma_sp).strip(),
            "ten_sp": str(ten_sp).strip(),
            "so_luong": int(so_luong),
            "gia_goc": int(gia_goc),
            "gia_ban": int(gia_ban),
        }
        res = self.client.table('inventory').insert(payload).execute()
        return res.data[0] if res.data else payload

    def update_product(self, product_id: int, updates: dict) -> bool:
        """Cập nhật linh hoạt thông tin sản phẩm theo ID"""
        clean_updates = {}
        for k in ["ma_sp", "ten_sp", "so_luong", "gia_goc", "gia_ban"]:
            if k in updates:
                val = updates[k]
                if k in ["so_luong", "gia_goc", "gia_ban"]:
                    clean_updates[k] = int(val) if val is not None else 0
                else:
                    clean_updates[k] = str(val).strip()

        if not clean_updates:
            return False

        res = self.client.table('inventory').update(clean_updates).eq("id", int(product_id)).execute()
        return bool(res.data)

    def delete_product(self, product_id: int) -> bool:
        """Xóa một sản phẩm khỏi kho theo ID"""
        res = self.client.table('inventory').delete().eq("id", int(product_id)).execute()
        return bool(res.data)

    def batch_sync_inventory(self, original_df: pd.DataFrame, edited_df: pd.DataFrame) -> dict:
        """
        Đồng bộ kho hàng theo cơ chế BATCH tối ưu
        """
        stats = {"deleted": 0, "upserted": 0, "inserted": 0}

        # 1. Xác định và xóa các sản phẩm bị loại bỏ
        if not original_df.empty and "id" in original_df.columns:
            orig_ids = set(original_df["id"].dropna().astype(int).tolist())
        else:
            orig_ids = set()

        if not edited_df.empty and "id" in edited_df.columns:
            curr_ids = set(edited_df["id"].dropna().astype(int).tolist())
        else:
            curr_ids = set()

        deleted_ids = list(orig_ids - curr_ids)
        if deleted_ids:
            self.client.table('inventory').delete().in_('id', deleted_ids).execute()
            stats["deleted"] = len(deleted_ids)

        if edited_df.empty:
            return stats

        # 2. Phân loại sản phẩm cập nhật (có ID) và sản phẩm mới (chưa có ID)
        records = edited_df.to_dict('records')
        to_upsert = []
        to_insert = []

        for row in records:
            clean_row = {k: v for k, v in row.items() if not pd.isna(v)}
            if not clean_row:
                continue

            if "so_luong" in clean_row:
                clean_row["so_luong"] = int(clean_row["so_luong"])
            if "gia_goc" in clean_row:
                clean_row["gia_goc"] = int(clean_row["gia_goc"])
            if "gia_ban" in clean_row:
                clean_row["gia_ban"] = int(clean_row["gia_ban"])

            if "id" in clean_row and clean_row["id"] is not None:
                clean_row["id"] = int(clean_row["id"])
                to_upsert.append(clean_row)
            else:
                clean_row.pop("id", None)
                clean_row.pop("created_at", None)
                to_insert.append(clean_row)

        if to_upsert:
            self.client.table('inventory').upsert(to_upsert).execute()
            stats["upserted"] = len(to_upsert)

        if to_insert:
            self.client.table('inventory').insert(to_insert).execute()
            stats["inserted"] = len(to_insert)

        return stats

    def update_product_quantity(self, product_id: int, new_quantity: int) -> bool:
        """Cập nhật nhanh số lượng một sản phẩm"""
        try:
            self.client.table('inventory').update({
                "so_luong": int(new_quantity)
            }).eq("id", int(product_id)).execute()
            return True
        except Exception as e:
            print(f"[SupabaseService] Lỗi update_product_quantity: {e}")
            raise e
