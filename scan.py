import streamlit as st
from PIL import Image, ImageOps
import pytesseract
import io
import fitz  # PyMuPDF
import google.generativeai as genai

# --- PHONG THỦY HỎA & KIM ---
st.set_page_config(page_title="Máy Quét Linh Linh^^", page_icon="🔥")

st.markdown("""
    <style>
    .stApp { background-color: #F5F5F5; }
    h1 { color: #D32F2F !important; text-shadow: 1px 1px 2px #FFD700; }
    div.stButton > button { background-color: #D32F2F !important; color: white !important; border: 2px solid #FFD700 !important; font-weight: bold; border-radius: 10px; }
    div.stDownloadButton > button { background-color: #FFD700 !important; color: #D32F2F !important; border: 2px solid #D32F2F !important; }
    .stTextArea textarea { border: 2px solid #D32F2F !important; }
    </style>
    """, unsafe_allow_html=True)

# --- CẤU HÌNH AI (ĐỔI TÊN MODEL CHO CHUẨN) ---
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    # Tui đổi sang tên model ổn định nhất hiện tại
    gemini_model = genai.GenerativeModel('gemini-1.5-flash') 
except Exception as e:
    st.error(f"Lỗi cấu hình AI: {e}")
    gemini_model = None

st.title("🔥 Máy Quét Linh Linh")
st.write("Vừa đẹp vừa khôn, quét chữ xong AI sửa lỗi chính tả luôn nha bà!")

uploaded_files = st.file_uploader("Kéo thả Ảnh hoặc PDF vào đây", type=["jpg", "jpeg", "png", "pdf"], accept_multiple_files=True)

if uploaded_files:
    if st.button("Kích Hoạt Máy Quét & Sửa Lỗi Siêu Tốc 🚀"):
        all_raw_text = ""
        images_to_show = []

        with st.spinner("Đang luyện chữ..."):
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

                # --- HIỆN LẠI ẢNH CHO BÀ XEM NÈ ---
                st.subheader("🖼️ Ảnh bà vừa tải lên:")
                for pic, cap in images_to_show:
                    st.image(pic, caption=cap, width=400)

                # --- NHỜ AI SỬA LỖI ---
                if gemini_model and all_raw_text.strip():
                    prompt = f"Hãy đóng vai biên tập viên, sửa hết lỗi chính tả, lỗi OCR (như 's j' thành 'số', 't' thành 'thành phố'...) trong văn bản sau đây. Chỉ trả về văn bản đã sửa xong:\n\n{all_raw_text}"
                    response = gemini_model.generate_content(prompt)
                    
                    st.success("AI đã sửa lỗi xong! Copy hàng xịn ở đây nha:")
                    st.text_area("Văn bản ĐÃ CHỈNH SỬA ✨:", response.text, height=400)
                else:
                    st.text_area("Văn bản bóc tách (Bản Raw):", all_raw_text, height=400)
                
            except Exception as e:
                st.error(f"Lỗi: {e}")
                           
