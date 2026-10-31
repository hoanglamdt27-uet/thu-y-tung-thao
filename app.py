import streamlit as st
import pandas as pd
from backend import BackendService

st.set_page_config(
    page_title="Thú Y Tùng & Thảo - Hệ Thống Quản Trị",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, 'Inter', 'SF Pro Display', 'Segoe UI', Roboto, sans-serif !important;
        color: rgb(29, 29, 31) !important;
        background-color: rgb(245, 245, 247) !important;
        -webkit-font-smoothing: antialiased;
    }

    .stApp {
        background-color: rgb(245, 245, 247) !important;
    }

    section[data-testid="stSidebar"] {
        background-color: rgba(235, 235, 240, 0.85) !important;
        backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgb(210, 210, 215) !important;
    }

    .mac-window {
        background-color: rgb(255, 255, 255);
        border-radius: 14px;
        border: 1px solid rgba(0, 0, 0, 0.08);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.06);
        overflow: hidden;
        margin-bottom: 24px;
    }

    .mac-titlebar {
        background: linear-gradient(180deg, rgb(250, 250, 252) 0%, rgb(240, 240, 244) 100%);
        border-bottom: 1px solid rgb(218, 218, 222);
        padding: 12px 18px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    .mac-dots {
        display: flex;
        gap: 8px;
        align-items: center;
    }

    .mac-dot {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        display: inline-block;
    }

    .mac-dot-close { background-color: rgb(255, 95, 86); border: 1px solid rgb(224, 68, 62); }
    .mac-dot-min { background-color: rgb(255, 189, 46); border: 1px solid rgb(222, 161, 35); }
    .mac-dot-max { background-color: rgb(39, 201, 63); border: 1px solid rgb(26, 171, 41); }

    .mac-window-title {
        font-size: 13px;
        font-weight: 600;
        color: rgb(72, 72, 74);
        letter-spacing: -0.1px;
    }

    .mac-window-body {
        padding: 24px 28px;
    }

    .mac-window-body h1 {
        font-size: 24px !important;
        font-weight: 700 !important;
        color: rgb(29, 29, 31) !important;
        margin: 0 0 6px 0 !important;
        letter-spacing: -0.4px;
    }

    .mac-window-body p {
        font-size: 14px !important;
        color: rgb(110, 110, 115) !important;
        margin: 0 !important;
    }

    .mac-card {
        background-color: rgb(255, 255, 255);
        border-radius: 12px;
        border: 1px solid rgba(0, 0, 0, 0.07);
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.03);
        padding: 20px;
        margin-bottom: 16px;
    }

    .metric-title {
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: rgb(134, 134, 139);
        margin-bottom: 6px;
    }

    .metric-value {
        font-size: 26px;
        font-weight: 700;
        color: rgb(29, 29, 31);
        letter-spacing: -0.5px;
    }

    .stTabs [data-baseweb="tab-list"] {
        background-color: rgb(229, 229, 234) !important;
        padding: 4px !important;
        border-radius: 10px !important;
        gap: 4px !important;
        border-bottom: none !important;
        margin-bottom: 20px !important;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: transparent !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 8px 20px !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        color: rgb(72, 72, 74) !important;
        transition: all 0.2s ease !important;
    }

    .stTabs [aria-selected="true"] {
        background-color: rgb(255, 255, 255) !important;
        color: rgb(29, 29, 31) !important;
        font-weight: 600 !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.12) !important;
        border-top: none !important;
    }

    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > div {
        background-color: rgb(255, 255, 255) !important;
        border: 1px solid rgb(210, 210, 215) !important;
        border-radius: 10px !important;
        color: rgb(29, 29, 31) !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        padding: 10px 12px !important;
        box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.02) !important;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: rgb(0, 113, 227) !important;
        box-shadow: 0 0 0 3px rgba(0, 113, 227, 0.2) !important;
    }

    .stButton > button {
        background-color: rgb(0, 113, 227) !important;
        color: rgb(255, 255, 255) !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        border-radius: 10px !important;
        padding: 10px 22px !important;
        border: none !important;
        box-shadow: 0 2px 6px rgba(0, 113, 227, 0.25) !important;
        transition: all 0.15s ease !important;
    }

    .stButton > button:hover {
        background-color: rgb(0, 119, 237) !important;
        box-shadow: 0 4px 12px rgba(0, 113, 227, 0.35) !important;
    }

    .mac-badge {
        display: inline-block;
        background-color: rgba(0, 113, 227, 0.1);
        color: rgb(0, 113, 227);
        font-size: 12px;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 980px;
        margin-bottom: 10px;
    }

    .sidebar-section-title {
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        color: rgb(134, 134, 139);
        margin: 16px 0 8px 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_backend():
    return BackendService()

backend = get_backend()

try:
    df_global = backend.get_inventory()
    total_products = len(df_global)
    total_items = int(df_global["so_luong"].dropna().sum()) if not df_global.empty else 0
    total_value = int((df_global["so_luong"].fillna(0) * df_global["gia_ban"].fillna(0)).sum()) if not df_global.empty else 0
except Exception:
    df_global = pd.DataFrame()
    total_products = 0
    total_items = 0
    total_value = 0

with st.sidebar:
    st.markdown("""
    <div style="padding: 8px 0 16px 0; border-bottom: 1px solid rgb(210, 210, 215);">
        <div class="mac-dots" style="margin-bottom: 12px;">
            <span class="mac-dot mac-dot-close"></span>
            <span class="mac-dot mac-dot-min"></span>
            <span class="mac-dot mac-dot-max"></span>
        </div>
        <div style="font-size: 17px; font-weight: 700; color: rgb(29, 29, 31);">Thú Y Tùng & Thảo</div>
        <div style="font-size: 12px; color: rgb(110, 110, 115);">Hệ thống quản trị đám mây</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section-title">Chế độ giao diện</div>', unsafe_allow_html=True)
    app_mode = st.selectbox(
        "Chọn thiết bị vận hành:",
        [
            "Hệ thống Quản trị (Máy tính)",
            "Cập nhật Kho nhanh (Điện thoại)"
        ],
        label_visibility="collapsed"
    )

    if app_mode == "Hệ thống Quản trị (Máy tính)":
        st.markdown('<div class="sidebar-section-title">Điều hướng nhanh</div>', unsafe_allow_html=True)
        quick_nav = st.radio(
            "Chọn phân hệ:",
            [
                "Xem toàn bộ theo Tab ngang",
                "1. Tư vấn Kỹ thuật (RAG)",
                "2. Sản xuất Nội dung Shopee",
                "3. Quản lý Tồn kho Cloud"
            ],
            label_visibility="collapsed"
        )
    else:
        quick_nav = "Mobile"

    st.markdown('<div class="sidebar-section-title">Tổng quan kho hàng</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="mac-card" style="padding: 14px; margin-bottom: 10px;">
        <div class="metric-title">Danh mục mặt hàng</div>
        <div class="metric-value" style="font-size: 20px;">{total_products} mã</div>
    </div>
    <div class="mac-card" style="padding: 14px; margin-bottom: 10px;">
        <div class="metric-title">Tổng đơn vị tồn kho</div>
        <div class="metric-value" style="font-size: 20px;">{total_items:,}</div>
    </div>
    <div class="mac-card" style="padding: 14px;">
        <div class="metric-title">Giá trị kho ước tính</div>
        <div class="metric-value" style="font-size: 20px; color: rgb(0, 113, 227);">{total_value:,} đ</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div class="mac-window">
    <div class="mac-titlebar">
        <div class="mac-dots">
            <span class="mac-dot mac-dot-close"></span>
            <span class="mac-dot mac-dot-min"></span>
            <span class="mac-dot mac-dot-max"></span>
        </div>
        <div class="mac-window-title">TungThao_Enterprise_Workspace — macOS Cloud Edition</div>
        <div style="width: 48px;"></div>
    </div>
    <div class="mac-window-body">
        <span class="mac-badge">Phiên bản Trực tuyến 2.0</span>
        <h1>Hệ Thống Quản Trị & Trợ Lý Trí Tuệ Nhân Tạo — Thú Y Tùng & Thảo</h1>
        <p>Tích hợp cơ sở dữ liệu thời gian thực Supabase, tra cứu phác đồ nội bộ RAG và tự động hóa nội dung Shopee</p>
    </div>
</div>
""", unsafe_allow_html=True)

def render_rag_module():
    st.markdown('<div class="mac-card">', unsafe_allow_html=True)
    st.subheader("Tra cứu Phác đồ & Tư vấn Khách hàng (RAG)")
    st.caption("Hệ thống trích xuất trực tiếp dữ liệu từ kho tri thức của cửa hàng để đưa ra hướng dẫn sử dụng và phác đồ chính xác.")
    
    user_query = st.text_area(
        "Nhập triệu chứng vật nuôi hoặc câu hỏi của khách hàng:",
        height=120,
        key="input_rag",
        placeholder="Ví dụ: Gà có biểu hiện khò khè, chướng diều khô chân, tiêu chảy phân xanh trắng thì dùng phác đồ nào?"
    )
    
    if st.button("Phân tích & Tra cứu Phác đồ", key="btn_rag"):
        if user_query.strip():
            with st.spinner("Đang truy xuất kho tri thức và tổng hợp phác đồ..."):
                try:
                    answer = backend.consult_rag(user_query)
                    st.markdown("---")
                    st.markdown("##### Kết quả tư vấn kỹ thuật")
                    st.write(answer)
                except Exception as e:
                    st.error(f"Lỗi kết nối mô hình trí tuệ nhân tạo: {e}")
        else:
            st.warning("Vui lòng nhập triệu chứng hoặc câu hỏi trước khi bấm tra cứu.")
    st.markdown('</div>', unsafe_allow_html=True)

def render_content_module():
    st.markdown('<div class="mac-card">', unsafe_allow_html=True)
    st.subheader("Sản xuất Nội dung Chuẩn SEO Shopee & Tự động Học Tri thức")
    st.caption("Tự động tìm kiếm thông tin từ website hãng sản xuất, lọc bỏ từ khóa vi phạm chính sách y tế và lưu vào bộ nhớ RAG.")
    
    product_name = st.text_input(
        "Nhập tên thuốc hoặc chế phẩm cần viết bài:",
        key="input_product",
        placeholder="Ví dụ: Điện giải thảo dược Gluco K-C Sakan"
    )
    
    if st.button("Thu thập Dữ liệu & Khởi tạo Bài viết", key="btn_content"):
        if product_name.strip():
            with st.spinner("Đang thu thập thông tin kỹ thuật từ nhà sản xuất..."):
                web_info = backend.fetch_web_data(product_name)
            
            with st.spinner("Đang biên tập bài đăng chuẩn SEO và kiểm duyệt từ khóa..."):
                try:
                    content = backend.generate_shopee_content(product_name, web_info)
                    saved = backend.save_to_knowledge_base(product_name, web_info)
                    
                    st.markdown("---")
                    col1, col2 = st.columns([3, 2])
                    with col1:
                        st.markdown("##### Bài viết hoàn chỉnh (Sẵn sàng đăng Shopee)")
                        st.text_area("Sao chép nội dung bên dưới:", value=content, height=360)
                    with col2:
                        st.markdown("##### Dữ liệu kỹ thuật thu thập được")
                        st.info(web_info)
                        if saved:
                            st.success(f"Đã tự động cập nhật dữ liệu của '{product_name}' vào kho tri thức nội bộ.")
                except Exception as e:
                    st.error(f"Lỗi xử lý nội dung: {e}")
        else:
            st.warning("Vui lòng nhập tên sản phẩm cần tạo bài viết.")
    st.markdown('</div>', unsafe_allow_html=True)

def render_inventory_module():
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.markdown(f"""
        <div class="mac-card">
            <div class="metric-title">Tổng số mã sản phẩm</div>
            <div class="metric-value">{total_products} danh mục</div>
        </div>
        """, unsafe_allow_html=True)
    with col_m2:
        st.markdown(f"""
        <div class="mac-card">
            <div class="metric-title">Tổng số lượng tồn kho</div>
            <div class="metric-value">{total_items:,} sản phẩm</div>
        </div>
        """, unsafe_allow_html=True)
    with col_m3:
        st.markdown(f"""
        <div class="mac-card">
            <div class="metric-title">Tổng giá trị hàng tồn</div>
            <div class="metric-value" style="color: rgb(0, 113, 227);">{total_value:,} VNĐ</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="mac-card">', unsafe_allow_html=True)
    st.subheader("Bảng điều khiển Tồn kho Trực tuyến (Supabase Cloud)")
    st.caption("Thêm mới ở dòng cuối cùng, chỉnh sửa trực tiếp các ô hoặc tích chọn đầu dòng và bấm phím Delete để xóa sản phẩm.")
    
    try:
        df_inventory = backend.get_inventory()
        
        edited_df = st.data_editor(
            df_inventory,
            num_rows="dynamic",
            disabled=["id", "created_at"],
            use_container_width=True,
            key="editor_inventory",
            column_config={
                "id": "Mã Định Danh (ID)",
                "created_at": "Thời Gian Tạo",
                "ma_sp": st.column_config.TextColumn("Mã Sản Phẩm", required=True),
                "ten_sp": st.column_config.TextColumn("Tên Sản Phẩm", required=True),
                "so_luong": st.column_config.NumberColumn("Số Lượng Tồn", min_value=0, step=1),
                "gia_goc": st.column_config.NumberColumn("Giá Gốc (VNĐ)", min_value=0, step=1000),
                "gia_ban": st.column_config.NumberColumn("Giá Bán (VNĐ)", min_value=0, step=1000)
            }
        )
        
        if st.button("Lưu thay đổi & Đồng bộ lên Đám mây", key="btn_sync"):
            with st.spinner("Đang đồng bộ hóa dữ liệu với máy chủ Supabase..."):
                backend.sync_inventory(df_inventory, edited_df)
                st.success("Đồng bộ dữ liệu kho hàng thành công.")
                st.rerun()
    except Exception as e:
        st.error(f"Lỗi kết nối cơ sở dữ liệu: {e}")
    st.markdown('</div>', unsafe_allow_html=True)

if app_mode == "Cập nhật Kho nhanh (Điện thoại)":
    st.markdown('<div class="mac-card">', unsafe_allow_html=True)
    st.subheader("Cập nhật Tồn kho Nhanh (Dành cho Điện thoại)")
    st.caption("Giao diện tối giản giúp cập nhật nhanh số lượng hàng nhập vào hoặc xuất bán tại cửa hàng.")

    try:
        df_inv = backend.get_inventory()
        if df_inv.empty:
            st.warning("Kho hàng hiện tại đang trống. Vui lòng thêm sản phẩm ở chế độ Quản trị Máy tính trước.")
        else:
            product_options = {
                f"{row['ten_sp']} (Mã: {row['ma_sp']})": row 
                for _, row in df_inv.iterrows()
            }
            
            selected_label = st.selectbox(
                "1. Chọn sản phẩm cần cập nhật:",
                options=list(product_options.keys())
            )
            
            selected_row = product_options[selected_label]
            current_qty = int(selected_row["so_luong"]) if selected_row["so_luong"] is not None else 0
            product_id = int(selected_row["id"])

            st.markdown(f"""
            <div style="background-color: rgba(0, 113, 227, 0.08); border: 1px solid rgba(0, 113, 227, 0.25); padding: 16px; border-radius: 10px; text-align: center; margin: 14px 0;">
                <div style="font-size: 12px; font-weight: 600; color: rgb(0, 113, 227); text-transform: uppercase;">Số lượng hiện có trong kho</div>
                <div style="font-size: 28px; font-weight: 700; color: rgb(29, 29, 31);">{current_qty}</div>
            </div>
            """, unsafe_allow_html=True)

            action_type = st.radio(
                "2. Chọn hình thức điều chỉnh:",
                [
                    "Nhập thêm hàng vào kho (Cộng thêm)",
                    "Xuất bán hàng cho khách (Trừ đi)",
                    "Đặt lại tổng số lượng tồn thực tế"
                ],
                index=0
            )

            input_qty = st.number_input(
                "3. Nhập số lượng:",
                min_value=0,
                value=1,
                step=1
            )

            if action_type == "Nhập thêm hàng vào kho (Cộng thêm)":
                final_qty = current_qty + input_qty
            elif action_type == "Xuất bán hàng cho khách (Trừ đi)":
                final_qty = max(0, current_qty - input_qty)
            else:
                final_qty = input_qty

            st.markdown(f"**Số lượng tồn kho mới sau khi lưu: `{final_qty}`**")

            if st.button("Xác nhận Lưu vào Kho", key="btn_mobile_save", use_container_width=True):
                with st.spinner("Đang cập nhật dữ liệu lên đám mây..."):
                    backend.update_product_quantity(product_id, final_qty)
                    st.success(f"Đã cập nhật thành công '{selected_row['ten_sp']}' thành {final_qty} sản phẩm.")
                    st.rerun()

    except Exception as e:
        st.error(f"Lỗi truy xuất dữ liệu: {e}")
    st.markdown('</div>', unsafe_allow_html=True)

else:
    if quick_nav == "Xem toàn bộ theo Tab ngang":
        tab1, tab2, tab3 = st.tabs([
            "Tư vấn Kỹ thuật (RAG)",
            "Sản xuất Nội dung Shopee",
            "Quản lý Tồn kho Cloud"
        ])
        with tab1:
            render_rag_module()
        with tab2:
            render_content_module()
        with tab3:
            render_inventory_module()
    elif quick_nav == "1. Tư vấn Kỹ thuật (RAG)":
        render_rag_module()
    elif quick_nav == "2. Sản xuất Nội dung Shopee":
        render_content_module()
    elif quick_nav == "3. Quản lý Tồn kho Cloud":
        render_inventory_module()