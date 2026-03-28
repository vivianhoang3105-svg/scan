import streamlit as st
from PIL import Image, ImageOps
import pytesseract
import io
import fitz  # PyMuPDF
import google.generativeai as genai

# --- PHONG THỦY HỎA & KIM ---
st.set_page_config(page_title="Máy Quét Linh Linh", page_icon="🔥")

st.markdown("""
    <style>
    .stApp { background-color: #F5F5F5; }
    h1 { color: #D32F2F !important; text-shadow: 1px 1px 2px #FFD700; }
    div.stButton > button { background-color: #D32F2F !important; color: white !important; border: 2px solid #FFD700 !important; font-weight: bold; border-radius: 10px; }
    div.stDownloadButton > button { background-color: #FFD700 !important; color: #D32F2F !important; border: 2px solid #D32F2F !important; }
    .stTextArea textarea { border: 2px solid #D32F2F !important; font-size: 16px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- CẤU HÌNH AI ---
api_key = st.secrets.get("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    # Tui dùng tên model cơ bản nhất để tránh lỗi 404
    model = genai.GenerativeModel('models/gemini-1.5-flash')
else:
    model = None

st.title("🔥 Máy Quét Linh Linh (Bản Siêu Cấp)")
st.write("Quét ảnh & PDF. Có AI tự động sửa lỗi chính tả cho bà!")

uploaded_files = st.file_uploader("Kéo thả Ảnh hoặc PDF vào đây", type=["jpg", "jpeg", "png", "pdf"], accept_multiple_files=True)

if uploaded_files:
    if st.button("Kích Hoạt Máy Quét 🚀"):
        all_raw_text = ""
        images_to_show = []

        with st.spinner("Đang đọc chữ, đợi tui xíu..."):
            try:
                for file in uploaded_files:
                    if file.name.lower().endswith('.pdf'):
                        doc = fitz.open(stream=file.read(), filetype="pdf")
                        for i in range(len(doc)):
                            page = doc.load_page(i)
                            pix = page.get_pixmap()
                            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                            images_to_show.append((img, f"PDF: {file.name} - Trang {i+1}"))
                            text = pytesseract.image_to_string(img, lang='vie+eng')
                            all_raw_text += f"\n{text}\n"
                    else:
                        img = Image.open(file)
                        img = ImageOps.exif_transpose(img)
                        final_img = img.convert('RGB')
                        images_to_show.append((final_img, f"Ảnh: {file.name}"))
                        text = pytesseract.image_to_string(final_img, lang='vie+eng')
                        all_raw_text += f"\n{text}\n"

                # 1. HIỆN ẢNH NGAY
                st.subheader("🖼️ Ảnh đã tải lên:")
                for pic, cap in images_to_show:
                    st.image(pic, caption=cap, width=500)

                # 2. HIỆN BẢN QUÉT THÔ NGAY (Đảm bảo bà luôn có chữ để xài)
                st.subheader("📄 Văn bản quét được (Bản thô):")
                st.text_area("Bà copy tạm ở đây nếu AI bận nha:", all_raw_text, height=300, key="raw_text")

                # 3. NHỜ AI SỬA LỖI (Nếu có lỗi thì nó chỉ báo ở đây, không làm mất chữ ở trên)
                if model and all_raw_text.strip():
                    with st.spinner("Đang nhờ AI sửa lỗi chính tả..."):
                        try:
                            prompt = f"Hãy đóng vai biên tập viên văn phòng, sửa hết lỗi chính tả và OCR trong đoạn sau. Chỉ trả về kết quả cuối cùng:\n\n{all_raw_text}"
                            response = model.generate_content(prompt)
                            st.success("✨ AI ĐÃ SỬA LỖI XONG!")
                            st.text_area("Văn bản ĐÃ CHỈNH SỬA (Hàng xịn):", response.text, height=400, key="ai_text")
                        except Exception as ai_err:
                            st.warning(f"AI đang bận một xíu (Lỗi: {ai_err}). Bà dùng tạm bản thô ở trên nha!")
                
            except Exception as e:
                st.error(f"Lỗi hệ thống: {e}")

               
