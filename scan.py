import streamlit as st
from PIL import Image, ImageOps
import pytesseract
import io
import fitz  # PyMuPDF

# --- PHẦN PHONG THỦY:---
st.set_page_config(page_title="Máy Quét Hợp Mệnh", page_icon="🔥")

# Inject CSS để đổi màu giao diện
st.markdown("""
    <style>
    /* Màu nền chính (Kim - Trắng Bạc) */
    .stApp {
        background-color: #F5F5F5;
    }
    /* Tiêu đề (Hỏa - Đỏ Rực) */
    h1 {
        color: #D32F2F !important;
        text-shadow: 1px 1px 2px #FFD700; /* Viền vàng Kim */
    }
    /* Nút bấm (Hỏa - Đỏ) */
    div.stButton > button {
        background-color: #D32F2F !important;
        color: white !important;
        border-radius: 10px;
        border: 2px solid #FFD700 !important; /* Viền vàng Kim */
        font-weight: bold;
    }
    /* Nút download */
    div.stDownloadButton > button {
        background-color: #FFD700 !important; /* Vàng Kim */
        color: #D32F2F !important; /* Chữ đỏ Hỏa */
        border: 2px solid #D32F2F !important;
    }
    /* Khung text */
    .stTextArea textarea {
        border: 2px solid #D32F2F !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🔥 Máy Quét Vạn Năng (Hỏa & Kim)")
st.write("Giao diện đỏ rực may mắn, nền trắng bạc sang trọng dành riêng cho bà Linh!")

# Nút tải file
uploaded_files = st.file_uploader("Chọn Ảnh (.jpg, .png) hoặc file PDF", 
                                  type=["jpg", "jpeg", "png", "pdf"], 
                                  accept_multiple_files=True)

if uploaded_files:
    if st.button("Kích Hoạt Máy Quét 🚀"):
        all_text = ""
        images_for_pdf = []

        with st.spinner("Đang 'luyện' chữ, đợi tui xíu..."):
            try:
                for file in uploaded_files:
                    if file.name.lower().endswith('.pdf'):
                        doc = fitz.open(stream=file.read(), filetype="pdf")
                        for page_index in range(len(doc)):
                            page = doc.load_page(page_index)
                            pix = page.get_pixmap()
                            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                            images_for_pdf.append(img)
                            text = pytesseract.image_to_string(img, lang='vie+eng')
                            all_text += f"\n\n--- PDF: {file.name} (Trang {page_index + 1}) ---\n\n{text}"
                    else:
                        img = Image.open(file)
                        img = ImageOps.exif_transpose(img)
                        final_image = img.convert('RGB')
                        images_for_pdf.append(final_image)
                        text = pytesseract.image_to_string(final_image, lang='vie+eng')
                        all_text += f"\n\n--- ẢNH: {file.name} ---\n\n{text}"

                if images_for_pdf:
                    pdf_output = io.BytesIO()
                    images_for_pdf[0].save(pdf_output, format='PDF', save_all=True, append_images=images_for_pdf[1:])
                    
                    st.success("Luyện xong rồi! Hàng về đây bà!")
                    st.download_button(label="📥 TẢI FILE PDF TỔNG HỢP (VÀNG KIM)", 
                                       data=pdf_output.getvalue(), 
                                       file_name="Ket_Qua_Quet.pdf")
                
                st.text_area("Văn bản bóc tách được:", all_text, height=400)
                
            except Exception as e:
                st.error(f"Ối, có chút trục trặc: {e}")
                       
