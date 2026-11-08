import re
from openai import OpenAI
from .config import AppConfig
from .rag_service import RagService

class AiService:
    """Tương tác với mô hình trí tuệ nhân tạo (OpenRouter / Gemini 3.8 Flash)"""

    @staticmethod
    def clean_shopee_plain_text(raw_text: str) -> str:
        """
        Loại bỏ triệt để toàn bộ ký tự Markdown (*, **, ***, ###, ---)
        để xuất Plain Text thuần túy, sạch sẽ, không dính dấu sao khi copy dán lên Shopee.
        """
        if not raw_text:
            return ""
        # 1. Bỏ cặp dấu sao in đậm / in nghiêng: ***text***, **text**, *text*
        text = re.sub(r'\*{1,3}(.*?)\*{1,3}', r'\1', raw_text)
        # 2. Thay thế dấu sao đầu dòng liệt kê thành gạch đầu dòng chuẩn Shopee
        text = re.sub(r'^[ \t]*\*[ \t]+', '- ', text, flags=re.MULTILINE)
        # 3. Loại bỏ toàn bộ dấu sao đơn lẻ còn sót lại
        text = text.replace('*', '')
        # 4. Loại bỏ các ký tự tiêu đề markdown (#, ##, ###)
        text = re.sub(r'^[ \t]*#{1,6}[ \t]*', '', text, flags=re.MULTILINE)
        # 5. Loại bỏ đường kẻ ngang markdown (---, ===, ___)
        text = re.sub(r'^[ \t]*[-=_]{3,}[ \t]*$', '', text, flags=re.MULTILINE)
        # 6. Rút gọn khoảng trống dòng liên tiếp thừa
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()

    @classmethod
    def get_client(cls):
        """Khởi tạo OpenAI Client kết nối tới OpenRouter"""
        api_key = AppConfig.get_openrouter_api_key()
        if not api_key:
            raise ValueError(
                "Chưa tìm thấy OpenRouter API Key hợp lệ. "
                "Quản trị viên vui lòng cấu hình trong file secrets.toml hoặc mục Cài đặt hệ thống."
            )
        return OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )

    @classmethod
    def consult_rag(cls, user_query: str) -> str:
        """
        Tư vấn phác đồ điều trị và cách dùng thuốc dựa trên kho tri thức nội bộ
        """
        try:
            client = cls.get_client()
            context = RagService.find_relevant_context(user_query)
            model_name = AppConfig.get_current_model()

            prompt = (
                f"TÀI LIỆU KHO TRI THỨC CỬA HÀNG:\n{context}\n\n"
                f"CÂU HỎI / TRIỆU CHỨNG CỦA KHÁCH HÀNG:\n{user_query}\n\n"
                "NHIỆM VỤ:\n"
                "1. Trả lời chi tiết, ân cần, dùng tiếng Việt chuẩn mực.\n"
                "2. Nếu có thuốc trong kho tri thức, hãy chỉ định tên thuốc, liều lượng và cách dùng cụ thể.\n"
                "3. Nếu triệu chứng chưa có trong kho tri thức, hãy gợi ý phác đồ thú y chuẩn mực và dặn dò khách hàng theo dõi sát tình trạng vật nuôi.\n"
                "4. Luôn ghi rõ lưu ý an toàn sinh học và vệ sinh chuồng trại."
            )

            extra_body = {}
            if "gemini-3.8" in model_name or "reasoning" in model_name:
                extra_body["reasoning"] = {"effort": AppConfig.get_reasoning_effort()}

            call_kwargs = {
                "model": model_name,
                "messages": [
                    {
                        "role": "system",
                        "content": "Bạn là Bác sĩ Thú y & Chuyên gia Kỹ thuật điều trị của phòng khám Thú Y Tùng & Thảo."
                    },
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 2500,
                "temperature": 0.4
            }
            if extra_body:
                call_kwargs["extra_body"] = extra_body

            response = client.chat.completions.create(**call_kwargs)
            return response.choices[0].message.content

        except ValueError as ve:
            return f"⚠️ {str(ve)}"
        except Exception as e:
            error_str = str(e)
            if "401" in error_str or "Authentication" in error_str:
                return (
                    "⚠️ Lỗi xác thực (401): API Key của OpenRouter không hợp lệ hoặc chưa được nạp. "
                    "Quản trị viên vui lòng vào mục 'Cài đặt hệ thống' trên menu để nhập Key hoặc kiểm tra file secrets.toml."
                )
            elif "429" in error_str:
                return "⚠️ Hệ thống đang quá tải hoặc tài khoản OpenRouter đã hết hạn mức (429). Vui lòng thử lại sau giây lát."
            else:
                return f"⚠️ Lỗi kết nối mô hình AI: {error_str}"

    @classmethod
    def generate_shopee_content(cls, product_name: str, technical_info: str) -> str:
        """
        Soạn bài mô tả sản phẩm Shopee chuẩn SEO, định dạng PLAIN TEXT 100% không dấu sao (*),
        tự động loại trừ từ khóa vi phạm chính sách sàn.
        """
        try:
            client = cls.get_client()
            model_name = AppConfig.get_current_model()
            
            prompt = (
                f"TÀI LIỆU KỸ THUẬT SẢN PHẨM:\n{technical_info}\n\n"
                f"SẢN PHẨM CẦN VIẾT BÀI ĐĂNG SHOPEE: {product_name}\n\n"
                "QUY ĐỊNH ĐỊNH DẠNG BẮT BUỘC (VÌ ĐÂY LÀ KHUNG MÔ TẢ PLAIN TEXT SHOPEE):\n"
                "1. TUYỆT ĐỐI KHÔNG DÙNG KÝ TỰ MARKDOWN: KHÔNG dùng dấu hoa thị (*, **, ***), KHÔNG dùng dấu thăng (#, ##, ###), KHÔNG dùng đường kẻ ngang (---).\n"
                "2. DÙNG CHỮ IN HOA cho tên từng đề mục (Ví dụ: 1. THÔNG TIN SẢN PHẨM, 2. THÀNH PHẦN HOẠT CHẤT, 3. CÔNG DỤNG NỔI BẬT, 4. HƯỚNG DẪN SỬ DỤNG, 5. CAM KẾT CHÍNH HÃNG).\n"
                "3. Dùng dấu gạch đầu dòng '- ' hoặc dấu chấm '• ' hoặc số thứ tự '1.', '2.' cho các dòng liệt kê.\n"
                "4. Toàn bộ văn bản phải là Plain Text thuần túy, sạch sẽ để người bán copy dán trực tiếp vào Shopee mà không phải xóa sửa bất kỳ ký tự thừa nào.\n\n"
                "QUY ĐỊNH BẢO MẬT & CHÍNH SÁCH Y TẾ SÀN SHOPEE:\n"
                "- Tuyệt đối KHÔNG dùng các từ cấm/bị quét như: 'đặc trị', 'chữa khỏi bệnh', 'kháng sinh', 'cam kết khỏi 100%'.\n"
                "- THAY THẾ BẰNG: 'hỗ trợ cải thiện', 'chế phẩm sinh học', 'tăng sức đề kháng', 'bảo vệ đường ruột/hô hấp'."
            )

            extra_body = {}
            if "gemini-3.8" in model_name or "reasoning" in model_name:
                extra_body["reasoning"] = {"effort": AppConfig.get_reasoning_effort()}

            call_kwargs = {
                "model": model_name,
                "messages": [
                    {
                        "role": "system",
                        "content": "Bạn là chuyên gia viết nội dung thương mại điện tử Shopee ngành Dược Thú Y & Chăn Nuôi. Bạn luôn xuất bản văn bản Plain Text sạch sẽ, tuyệt đối không dùng dấu sao (*) hay markdown."
                    },
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 2500,
                "temperature": 0.5
            }
            if extra_body:
                call_kwargs["extra_body"] = extra_body

            response = client.chat.completions.create(**call_kwargs)
            raw_content = response.choices[0].message.content or ""
            # Làm sạch triệt để toàn bộ ký tự markdown/dấu sao trước khi trả về
            return cls.clean_shopee_plain_text(raw_content)

        except ValueError as ve:
            raise ValueError(str(ve))
        except Exception as e:
            error_str = str(e)
            if "401" in error_str or "Authentication" in error_str:
                raise ValueError("Lỗi xác thực (401): API Key không hợp lệ hoặc chưa được cấu hình.")
            raise e

