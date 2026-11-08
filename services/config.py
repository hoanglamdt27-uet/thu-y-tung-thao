import os
import sys
from pathlib import Path

# Built-in toml parser (Python 3.11+)
try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None


class AppConfig:
    """Quản lý cấu hình tập trung và xác thực hệ thống (Decoupled from UI runtime)"""

    # Model AI sử dụng mặc định qua OpenRouter (Gemini 3.8 Flash High Reasoning)
    DEFAULT_MODEL = "google/gemini-3.8-flash"
    DEFAULT_REASONING_EFFORT = "high"

    # Supabase mặc định
    DEFAULT_SUPABASE_URL = "https://hduatpmcxlbaqwachhju.supabase.co"
    DEFAULT_SUPABASE_KEY = "sb_publishable_Un7ci74dqscf0yEGfmJBkQ_4ZM4LP_B"

    # Mật khẩu quản trị mặc định
    DEFAULT_ADMIN_PASSWORD = "admin"

    # Bộ nhớ tạm in-memory cho cấu hình tùy chỉnh
    _runtime_openrouter_key: str = ""
    _runtime_model: str = ""
    _runtime_reasoning_effort: str = ""

    @classmethod
    def get_current_model(cls) -> str:
        """Lấy tên Model AI hiện tại đang kích hoạt"""
        return cls._runtime_model or cls.DEFAULT_MODEL

    @classmethod
    def set_current_model(cls, model_name: str):
        """Chuyển đổi Model AI trong phiên làm việc"""
        cls._runtime_model = (model_name or "").strip()

    @classmethod
    def get_reasoning_effort(cls) -> str:
        """Lấy mức độ suy luận (high / medium / low)"""
        return cls._runtime_reasoning_effort or cls.DEFAULT_REASONING_EFFORT

    @classmethod
    def set_reasoning_effort(cls, effort: str):
        """Đặt mức độ suy luận (high / medium / low)"""
        cls._runtime_reasoning_effort = (effort or "high").strip().lower()

    @classmethod
    def _read_secrets_toml(cls) -> dict:
        """Đọc file secrets.toml cấu hình bảo mật hệ thống"""
        candidate_paths = [
            Path("secrets.toml"),
            Path(__file__).parent.parent / "secrets.toml",
            Path(".streamlit/secrets.toml"),
            Path.home() / ".streamlit" / "secrets.toml",
        ]
        for path in candidate_paths:
            if path.exists() and tomllib:
                try:
                    with open(path, "rb") as f:
                        return tomllib.load(f)
                except Exception:
                    pass
        return {}

    @classmethod
    def set_runtime_openrouter_key(cls, key: str):
        """Đặt API key tùy chỉnh trong phiên làm việc hiện tại"""
        cls._runtime_openrouter_key = (key or "").strip()

    @classmethod
    def get_openrouter_api_key(cls) -> str:
        """
        Lấy OpenRouter API Key theo thứ tự ưu tiên:
        1. Memory cache của ứng dụng (set qua Settings UI)
        2. File secrets.toml
        3. Biến môi trường hệ thống OPENROUTER_API_KEY
        """
        if cls._runtime_openrouter_key:
            return cls._runtime_openrouter_key

        # Đọc từ file secrets.toml trực tiếp
        secrets = cls._read_secrets_toml()
        if "OPENROUTER_API_KEY" in secrets:
            val = str(secrets["OPENROUTER_API_KEY"]).strip()
            if val and val != "placeholder_key":
                return val

        # Đọc từ Environment Variable
        env_key = os.getenv("OPENROUTER_API_KEY", "").strip()
        if env_key and env_key != "placeholder_key":
            return env_key

        return ""

    @classmethod
    def has_valid_openrouter_key(cls) -> bool:
        """Kiểm tra xem hệ thống đã có API Key OpenRouter hợp lệ chưa"""
        key = cls.get_openrouter_api_key()
        return bool(key and len(key) > 10 and key != "placeholder_key")

    @classmethod
    def get_supabase_credentials(cls) -> tuple[str, str]:
        """Lấy URL và Key của Supabase an toàn và độc lập"""
        url = os.getenv("SUPABASE_URL", "")
        key = os.getenv("SUPABASE_KEY", "")

        if not url or not key:
            secrets = cls._read_secrets_toml()
            url = url or secrets.get("SUPABASE_URL", "")
            key = key or secrets.get("SUPABASE_KEY", "")

        return (
            url.strip() if url else cls.DEFAULT_SUPABASE_URL,
            key.strip() if key else cls.DEFAULT_SUPABASE_KEY,
        )

    @classmethod
    def get_admin_password(cls) -> str:
        """Lấy mật khẩu quản trị từ file bí mật hoặc biến môi trường"""
        pwd = os.getenv("ADMIN_PASSWORD", "")
        if not pwd:
            secrets = cls._read_secrets_toml()
            pwd = secrets.get("ADMIN_PASSWORD", "")

        return str(pwd).strip() if pwd else cls.DEFAULT_ADMIN_PASSWORD

    @classmethod
    def verify_admin_password(cls, input_password: str) -> bool:
        """Kiểm tra mật khẩu đăng nhập admin"""
        if not input_password:
            return False
        return input_password.strip() == cls.get_admin_password()
