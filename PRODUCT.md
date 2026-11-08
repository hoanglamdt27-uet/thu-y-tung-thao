# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

### Người dùng chính: Chủ cửa hàng (Admin — Tùng & Thảo)
- **Tình huống:** Quản lý toàn bộ hoạt động cửa hàng thuốc thú y từ máy tính bàn (desktop) hoặc cập nhật nhanh tồn kho từ điện thoại khi ở quầy/kho.
- **Công việc hàng ngày:** Tra cứu phác đồ điều trị cho khách qua module RAG, tạo bài đăng sản phẩm Shopee chuẩn SEO, quản lý nhập/xuất/tồn kho trực tuyến, theo dõi đơn hàng và doanh thu.
- **Ưu tiên:** Thao tác nhanh, ít bước bấm, dữ liệu đồng bộ thời gian thực, dễ quét mắt khi bận.

### Người dùng phụ: Khách mua hàng (trực tiếp hoặc online)
- **Tình huống:** Tra cứu thông tin sản phẩm, triệu chứng bệnh, phác đồ điều trị trên web.
- **Lưu ý:** Hiện tại giao diện chưa tách biệt phần dành cho khách; toàn bộ hệ thống là giao diện quản trị (admin). Phần phục vụ khách hàng là kế hoạch mở rộng trong tương lai.

## Product Purpose

Hệ thống quản trị nội bộ tập trung cho cửa hàng thuốc thú y "Thú Y Tùng & Thảo", giúp:

1. **Tra cứu phác đồ thú y bằng AI (RAG):** Truy vấn kho tri thức nội bộ (knowledge_base.txt) kết hợp mô hình ngôn ngữ lớn để tư vấn kỹ thuật cho khách hàng về triệu chứng, phác đồ điều trị gia súc/gia cầm.
2. **Sản xuất nội dung Shopee tự động:** Thu thập dữ liệu kỹ thuật từ web (DuckDuckGo), tạo bài mô tả sản phẩm chuẩn SEO, tự động lọc từ khóa vi phạm chính sách sàn, đồng thời lưu dữ liệu thu thập vào kho tri thức RAG.
3. **Quản lý tồn kho trực tuyến (Supabase Cloud):** Thêm/sửa/xóa sản phẩm, theo dõi giá gốc/giá bán, đồng bộ dữ liệu thời gian thực với cơ sở dữ liệu đám mây.
4. **Chế độ điện thoại (Mobile):** Giao diện tối giản cho nhập/xuất kho nhanh tại quầy mà không cần mở đầy đủ bảng điều khiển.

Thành công = chủ cửa hàng tự vận hành được toàn bộ quy trình kinh doanh (tư vấn kỹ thuật, bán hàng online, quản lý kho) từ một giao diện duy nhất mà không cần kỹ năng IT.

## Positioning

Hệ thống all-in-one cho cửa hàng thuốc thú y nhỏ, tích hợp AI tư vấn phác đồ + tự động hóa nội dung thương mại điện tử + quản lý kho đám mây — khác biệt với các phần mềm quản lý bán hàng phổ thông vì hiểu ngữ cảnh chuyên ngành thú y (thuật ngữ, phác đồ, quy định từ khóa sàn TMĐT).

## Operating Context

- **Thiết bị:** Máy tính bàn/laptop (chế độ quản trị đầy đủ) hoặc điện thoại (cập nhật kho nhanh tại quầy).
- **Quy trình bán hàng:**
  1. Khách hỏi triệu chứng → Admin tra RAG → tư vấn phác đồ + sản phẩm phù hợp.
  2. Bán hàng online → tạo bài Shopee bằng module Content → đăng lên sàn.
  3. Nhập/xuất hàng → cập nhật kho từ desktop hoặc điện thoại → đồng bộ Supabase.
- **Tần suất:** Hàng ngày, nhiều lần trong ngày (đặc biệt module kho).
- **Môi trường:** Cửa hàng thuốc thú y vật lý tại Việt Nam, kết nối internet ổn định, bán song song offline (tại quầy) và online (Shopee).

## Capabilities and Constraints

### Đã có
- Module RAG tư vấn phác đồ kỹ thuật thú y (Gemini 2.5 Flash qua OpenRouter + knowledge_base.txt)
- Module sản xuất nội dung Shopee chuẩn SEO, lọc từ vi phạm, tự học tri thức
- Module quản lý tồn kho CRUD với Supabase (thêm/sửa/xóa/đồng bộ đám mây)
- Chế độ Mobile riêng (cập nhật kho nhanh: nhập thêm / xuất bán / đặt lại số lượng)
- Hai chế độ điều hướng: Tab ngang (xem tất cả) hoặc nhảy nhanh tới từng phân hệ

### Kế hoạch mở rộng (đã xác nhận)
- Quản lý đơn hàng / hóa đơn từng đơn hàng bán online
- Báo cáo doanh thu / thống kê bán hàng

### Ràng buộc kỹ thuật
- Stack: Streamlit (Python) — giới hạn khả năng tuỳ biến giao diện so với framework frontend thuần
- Backend: Supabase (PostgreSQL hosted) — dữ liệu tồn kho, xác thực qua API key
- AI: OpenRouter API (model Google Gemini 2.5 Flash)
- Web scraping: DuckDuckGo Search
- Ngôn ngữ giao diện: Tiếng Việt hoàn toàn

### Thuật ngữ chuyên ngành
- **Phác đồ:** Hướng dẫn điều trị chuẩn cho từng loại bệnh/triệu chứng ở vật nuôi
- **RAG (Retrieval-Augmented Generation):** Truy xuất kho tri thức nội bộ kết hợp AI để trả lời
- **Chế phẩm sinh học:** Từ thay thế an toàn cho "kháng sinh" trên sàn TMĐT
- **Mã SP / Tên SP:** Mã sản phẩm nội bộ và tên hiển thị trong hệ thống kho

## Brand Commitments

- **Tên thương hiệu:** Thú Y Tùng & Thảo
- **Giọng nói:** Chuyên nghiệp, đáng tin cậy, thực tiễn — ngôn ngữ kỹ thuật thú y chính xác nhưng dễ hiểu cho nông dân/người chăn nuôi
- **Nguyên tắc nội dung Shopee:** Tuyệt đối không dùng từ vi phạm chính sách sàn (đặc trị, chữa bệnh, kháng sinh, cam kết khỏi 100%), thay bằng từ an toàn (hỗ trợ cải thiện, bổ trợ sức khỏe, chế phẩm sinh học, tăng cường sức đề kháng)
- **Không sử dụng icon/emoji:** Giao diện hiện tại cam kết không dùng icon để tránh lỗi font và đảm bảo tương thích

## Evidence on Hand

- File tri thức nội bộ: `knowledge_base.txt` — hiện chứa dữ liệu phác đồ và thông tin thuốc (nội dung đang được bổ sung tự động qua module Content)
- Cơ sở dữ liệu Supabase: bảng `inventory` với các trường `id`, `created_at`, `ma_sp`, `ten_sp`, `so_luong`, `gia_goc`, `gia_ban`
- Chưa có: logo chính thức, hình ảnh sản phẩm, dữ liệu khách hàng, lịch sử đơn hàng

## Product Principles

1. **Một cửa, một màn hình:** Mọi nghiệp vụ (tư vấn, bán hàng, kho) phải truy cập được từ một giao diện duy nhất, không yêu cầu chuyển đổi ứng dụng.
2. **Nhanh hơn giấy bút:** Thao tác phổ biến nhất (cập nhật kho, tra phác đồ) phải hoàn thành trong ít bước bấm nhất có thể, đặc biệt trên điện thoại.
3. **Đáng tin cậy như sổ sách:** Dữ liệu kho phải chính xác, đồng bộ thời gian thực, không để xảy ra mất mát hoặc sai lệch giữa các thiết bị.
4. **AI phục vụ chuyên môn:** Trợ lý AI phải trả lời dựa trên kho tri thức thực tế của cửa hàng, không bịa đặt phác đồ, và luôn ghi rõ khi thông tin chưa có trong cơ sở.
5. **An toàn trên sàn TMĐT:** Nội dung tạo ra phải tuân thủ chính sách sàn thương mại điện tử, tự động lọc bỏ từ khóa vi phạm.

