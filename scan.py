import streamlit as st
from PIL import Image
import pytesseract

# Thiết lập giao diện cho App
st.set_page_config(page_title="Scanner Của Tui", page_icon="📸")

st.title("📸 App Quét Văn Bản (Không Tốn Tiền)")
st.write("Chụp ảnh hoặc tải ảnh lên đây để lấy chữ nha!")

# Nút tải ảnh lên (Khi mở trên iPhone, nó sẽ hỏi mở Camera hoặc Thư viện)
uploaded_file = st.file_uploader("Chọn ảnh...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Hiển thị ảnh đã chọn
    image = Image.open(uploaded_file)
    st.image(image, caption='Ảnh đang xử lý', use_column_width=True)
    
    # Nút bấm để bắt đầu quét
    if st.button("Bắt đầu quét 🚀"):
        with st.spinner("Đang nhìn chữ, đợi tí nha..."):
            try:
                # Quét chữ bằng Tesseract (hỗ trợ tiếng Việt và tiếng Anh)
                # Lưu ý: Server chạy code cần cài đặt data ngôn ngữ tiếng Việt cho Tesseract
                text = pytesseract.image_to_string(image, lang='vie+eng')
                
                if text.strip():
                    st.success("Xong! Copy chữ ở dưới nhé:")
                    st.text_area("Kết quả:", text, height=300)
                else:
                    st.warning("Ủa, không tìm thấy chữ nào trong ảnh cả.")
            except Exception as e:
                st.error(f"Có lỗi xảy ra: {e}")
                
