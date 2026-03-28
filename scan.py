import streamlit as st
from PIL import Image, ImageOps
import pytesseract
import io
import fitz  # PyMuPDF

# Cài đặt giao diện chuẩn
st.set_page_config(page_title="Máy Quét Văn Bản Pro", page_icon="📑")

st.title("📑 Máy Quét Văn Bản Linh Linh")
st.write("Hỗ trợ quét chữ từ Ảnh (JPG, PNG) và file PDF. Kết quả sẽ được gom thành 1 file PDF tổng hợp.")

# Nút tải file
uploaded_files = st.file_uploader("Kéo thả Ảnh hoặc file PDF vào đây", 
                                  type=["jpg", "jpeg", "png", "pdf"], 
                                  accept_multiple_files=True)

if uploaded_files:
    if st.button("Bắt đầu quét dữ liệu 🚀"):
        all_text = ""
        images_for_pdf = []

        with st.spinner("Đang xử lý dữ liệu..."):
            try:
                for file in uploaded_files:
                    # Xử lý PDF
                    if file.name.lower().endswith('.pdf'):
                        doc = fitz.open(stream=file.read(), filetype="pdf")
                        for page_index in range(len(doc)):
                            page = doc.load_page(page_index)
                            pix = page.get_pixmap()
                            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                            images_for_pdf.append(img)
                            text = pytesseract.image_to_string(img, lang='vie+eng')
                            all_text += f"\n\n--- PDF: {file.name} (Trang {page_index + 1}) ---\n\n{text}"
                    
                    # Xử lý Ảnh
                    else:
                        img = Image.open(file)
                        img = ImageOps.exif_transpose(img) # Tự xoay đúng chiều
                        final_image = img.convert('RGB')
                        images_for_pdf.append(final_image)
                        text = pytesseract.image_to_string(final_image, lang='vie+eng')
                        all_text += f"\n\n--- ẢNH: {file.name} ---\n\n{text}"

                # Tạo nút tải PDF tổng hợp
                if images_for_pdf:
                    pdf_output = io.BytesIO()
                    images_for_pdf[0].save(pdf_output, format='PDF', save_all=True, append_images=images_for_pdf[1:])
                    
                    st.success("Đã xử lý xong toàn bộ tài liệu!")
                    st.download_button(label="📥 Tải file PDF tổng hợp", 
                                       data=pdf_output.getvalue(), 
                                       file_name="Ket_Qua_Quet.pdf")
                
                # Hiển thị văn bản để copy
                st.text_area("Văn bản bóc tách được:", all_text, height=400)
                
            except Exception as e:
                st.error(f"Lỗi rồi bà ơi: {e}")

                     
