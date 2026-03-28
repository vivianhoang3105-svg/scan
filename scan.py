import streamlit as st
from PIL import Image, ImageOps
import pytesseract

# Cài đặt giao diện app
st.set_page_config(page_title="App Quét Chữ", page_icon="📝")

st.title("📝 Máy Quét Văn Bản Mini")
st.write("Dùng iPhone chụp ảnh hoặc chọn ảnh từ thư viện để lấy chữ nha!")

# Nút tải ảnh/chụp ảnh
uploaded_file = st.file_uploader("Bấm vào đây để Chọn ảnh / Chụp mới", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # 1. Mở ảnh gốc
    raw_image = Image.open(uploaded_file)
    
    # 2. Xoay ảnh cho đúng chiều (chữa bệnh lật ngang)
    fixed_image = ImageOps.exif_transpose(raw_image)
    
    # 3. Ép kiểu về ảnh tiêu chuẩn (chữa bệnh Unsupported Format của iPhone)
    final_image = fixed_image.convert('RGB')
    
    # Hiển thị ảnh đã sửa
    st.image(final_image, caption='Ảnh đã sẵn sàng', use_container_width=True)
    
    # Nút bấm thực thi
    if st.button("Bắt đầu quét 🚀"):
        with st.spinner("Đang soi chữ, đợi tui xíu..."):
            try:
                # Quét chữ với ảnh đã chuẩn hóa
                text = pytesseract.image_to_string(final_image, lang='vie+eng')
                
                if text.strip():
                    st.success("Thành công! Copy chữ ở khung dưới nhé:")
                    st.text_area("Văn bản lấy được:", text, height=300)
                else:
                    st.warning("Ủa, hổng thấy chữ nào trong ảnh. Bà chụp cho nét lại xem sao.")
            except Exception as e:
                st.error("Có lỗi xảy ra rồi:")
                st.error(str(e))
