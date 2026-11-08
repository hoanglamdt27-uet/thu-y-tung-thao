# Design System: Dark Luxury Glassmorphism & Mesh Glow

<!-- impeccable:design-schema 1 -->

## Purpose & Mode

Hệ thống thiết kế chuẩn **Operate & Experience**, lấy cảm hứng trực tiếp từ phong cách E-commerce Store Admin Dashboard của `@_code_and_chill_` (Glassmorphism, Luminous Mesh Gradients, Dark Obsidian Canvas).

### Nguyên tắc cốt lõi:
1. **Nền Obsidian & Ánh Sáng Tương Phản (Ambient Mesh Glow):** Nền đen sâu thẳm `#070913` kết hợp với 3 khối cầu phát sáng khổng lồ mờ ảo (Amber/Gold `#f59e0b` góc trên phải, Emerald Mint `#10b981` giữa dưới, Electric Cyan `#06b6d4` góc dưới phải) tạo chiều sâu không gian vượt trội.
2. **Kính Mờ Đẳng Cấp (Frosted Glassmorphism):** Thẻ và bảng điều khiển sử dụng `background: rgba(13, 19, 33, 0.7)`, độ mờ `backdrop-filter: blur(24px) saturate(180%)`, đường viền siêu mảnh `1px solid rgba(255, 255, 255, 0.08)` và hiệu ứng phản xạ ánh sáng nổi `inset 0 1px 0 rgba(255, 255, 255, 0.06)`.
3. **Thước Đo Lâm Sàng Động:** Vòng tròn tiến độ doanh thu tháng (SVG Circular Progress), biểu đồ đường cong phát quang (Luminous Curved Area Chart), thanh xung nhịp phòng khám (Animated Live Equalizer).

---

## Bảng Màu & Ánh Sáng

### Nền & Kính Mờ (Surfaces & Glass)
- **Void Background:** `#070913` (Obsidian sâu)
- **Sidebar Surface:** `rgba(9, 14, 26, 0.8)` với `backdrop-filter: blur(28px)`
- **Card Surface:** `rgba(13, 19, 33, 0.72)` với `backdrop-filter: blur(24px)`
- **Border Default:** `rgba(255, 255, 255, 0.08)`
- **Border Hover:** `rgba(255, 255, 255, 0.16)`

### Ánh Sáng Ambient Mesh Glow
- **Amber / Gold Orb (Top Right):** `rgba(245, 158, 11, 0.2)` -> `rgba(234, 88, 12, 0.08)`, blur 130px.
- **Emerald Mint Orb (Bottom Center):** `rgba(16, 185, 129, 0.2)` -> `rgba(6, 182, 212, 0.1)`, blur 140px.
- **Electric Cyan Orb (Bottom Right):** `rgba(6, 182, 212, 0.18)` -> `rgba(59, 130, 246, 0.12)`, blur 120px.

### Điểm Nhấn Tương Tác (Accents)
- **Primary Teal Glow:** `#2dd4bf` (Teal 400), Gradient `#0f766e` -> `#10b981`.
- **Text Headings:** `#ffffff` (White 100%).
- **Text Body:** `#cbd5e1` (Slate 300).
- **Text Muted / Captions:** `#64748b` (Slate 500) hoặc `#94a3b8` (Slate 400).
- **Status Pills:** 
  - Đủ hàng / Online: `#34d399` (Emerald 400) với nền `rgba(16, 185, 129, 0.15)`.
  - Cảnh báo tồn: `#fb7185` (Rose 400) với nền `rgba(244, 63, 94, 0.15)`.

---

## Typography

- **Chữ số & Tiêu đề:** `Plus Jakarta Sans`, `Inter`, font-weight 700 / 800.
- **Mã thuốc & Số liệu tiền tệ:** `JetBrains Mono`, font-weight 600.
- **Tỷ lệ thị giác:** Cân bằng giữa độ rực rỡ của các khối kính và độ tương phản của chữ (đảm bảo chuẩn WCAG AA ≥ 4.5:1).
