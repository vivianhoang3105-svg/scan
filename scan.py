import streamlit as st
from PIL import Image, ImageOps
import pytesseract
import io
from pdf2image import convert_from_bytes

# Cài đặt giao diện
st.set_page_config(page_title="Máy Quét Vạn Năng", page_icon="📑")

st.title("📑 Máy Quét Ảnh & PDF (Bản Đặc Biệt)")
st.write("Bà quăng Ảnh hoặc file PDF vào đây, tui lo hết!")

# Chấp nhận cả ảnh và PDF
uploaded_files = st.file_uploader("Chọn Ảnh (.jpg, .png) hoặc file PDF", 
                                  type=["jpg", "jpeg", "png", "pdf"], 
                                  accept_multiple_files=True)

if uploaded_files:
    if st.button("Bắt đầu quét dữ liệu 🚀"):
        all_text = ""
        images_for_pdf = []

        with st.spinner("Đang đọc dữ liệu, đợi tui xíu nha..."):
            try:
                for file in uploaded_files:
                    # Trường hợp 1: Nếu là file PDF
                    if file.name.lower().endswith('.pdf'):
                        # Chuyển PDF thành danh sách các ảnh (từng trang)
                        pages = convert_from_bytes(file.read())
                        for i, page in enumerate(pages):
                            final_image = page.convert('RGB')
                            images_for_pdf.append(final_image)
                            text = pytesseract.image_to_string(final_image, lang='vie+eng')
                            all_text += f"\n\n--- PDF: {file.name} (Trang {i+1}) ---\n\n{text}"
                    
                    # Trường hợp 2: Nếu là Ảnh
                    else:
                        img = Image.open(file)
                        img = ImageOps.exif_transpose(img) # Sửa lỗi xoay ngang
                        final_image = img.convert('RGB')
                        images_for_pdf.append(final_image)
                        text = pytesseract.image_to_string(final_image, lang='vie+eng')
                        all_text += f"\n\n--- ẢNH: {file.name} ---\n\n{text}"

                # Tạo nút tải PDF tổng hợp nếu có dữ liệu
                if images_for_pdf:
                    pdf_output = io.BytesIO()
                    images_for_pdf[0].save(pdf_output, format='PDF', save_all=True, append_images=images_for_pdf[1:])
                    
                    st.success("Xong rồi nè bà ơi!")
                    st.download_button(label="📥 TẢI FILE PDF TỔNG HỢP", 
                                       data=pdf_output.getvalue(), 
                                       file_name="Ket_Qua_Quet.pdf")
                
                # Hiện text để copy
                st.text_area("Toàn bộ văn bản bóc tách được:", all_text, height=400)
                
            except Exception as e:
                st.error(f"Lỗi rồi bà ơi: {e}")
