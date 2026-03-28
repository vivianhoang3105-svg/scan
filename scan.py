import streamlit as st
from PIL import Image, ImageOps
import pytesseract
import io

# Cài đặt giao diện
st.set_page_config(page_title="App Quét Chữ Pro Max", page_icon="🚀")

st.title("🚀 Máy Quét Đa Năng (Bản Pro Max)")
st.write("Quăng nhiều ảnh vô đây 1 lúc, ngang dọc gì tui cân hết. Quét xong gom thành 1 file PDF cho bà luôn!")

# Nút tải ảnh (Cho phép chọn nhiều ảnh)
uploaded_files = st.file_uploader("Bấm vào đây để chọn 1 hoặc nhiều ảnh", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if uploaded_files:
    st.write(f"Đã nhận {len(uploaded_files)} trang. Bấm nút dưới để máy chạy nha!")
    
    if st.button("Bắt đầu quét & Tạo PDF 🚀"):
        all_text = ""
        images_for_pdf = []

        with st.spinner("Đang vắt chân lên cổ chạy, đợi tui xíu..."):
            try:
                for idx, file in enumerate(uploaded_files):
                    # 1. Mở ảnh gốc
                    raw_image = Image.open(file)
                    
                    # 2. Xoay ảnh chuẩn xác theo chiều lúc cầm điện thoại chụp
                    fixed_image = ImageOps.exif_transpose(raw_image)
                    
                    # 3. Lột vỏ MPO của iPhone, đưa về chuẩn RGB để tạo PDF
                    final_image = fixed_image.convert('RGB')
                    images_for_pdf.append(final_image)

                    # 4. Quét chữ bằng Tesseract
                    text = pytesseract.image_to_string(final_image, lang='vie+eng')
                    
                    # 5. Gom chữ lại, phân trang rõ ràng
                    all_text += f"\n\n{'='*15} TRANG {idx + 1} {'='*15}\n\n"
                    all_text += text if text.strip() else "(Trang này tui hổng thấy chữ gì ráo)"

                # Tạo file PDF ảo trong bộ nhớ
                if images_for_pdf:
                    pdf_bytes = io.BytesIO()
                    images_for_pdf[0].save(
                        pdf_bytes, 
                        format='PDF', 
                        save_all=True, 
                        append_images=images_for_pdf[1:]
                    )
                    
                    st.success("Xong xui tui lùi! Lấy hàng đi bà ơi:")
                    
                    # Nút tải PDF
                    st.download_button(
                        label="📥 BẤM VÀO ĐÂY ĐỂ TẢI FILE PDF",
                        data=pdf_bytes.getvalue(),
                        file_name="Tai_Lieu_Sieu_Cap.pdf",
                        mime="application/pdf"
                    )
                    
                # Hiện khung text tổng hợp
                st.text_area("Toàn bộ chữ lấy được (Copy paste thoải mái):", all_text, height=400)
                
            except Exception as e:
                st.error(f"Ối, có lỗi rồi: {e}")
