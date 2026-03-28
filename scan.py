import streamlit as st
from PIL import Image, ImageOps
import pytesseract
import io
import fitz  # PyMuPDF
import google.generativeai as genai

# --- GIAO DIỆN HỎA & KIM SIÊU CẤP ---
st.set_page_config(page_title="Máy Quét Linh Linh", page_icon="🔥")

st.markdown("""
    <style>
    .stApp { background-color: #F8F9FA; }
    h1 { color: #D32F2F !important; text-shadow: 2px 2px 4px #FFD700; }
    div.stButton > button { background-color: #D32F2F !important; color: white !important; border: 2px solid #FFD700 !important; font-weight: bold; border-radius: 12px; }
    
    /* KHUNG ĐEN CHỮ VÀNG - ĐÚNG GU BÀ THÍCH NÈ */
    .stTextArea textarea { 
        background-color: #121212 !important; 
        color: #FFD700 !important; 
        border: 2px solid #D32F2F !important; 
        font-size: 18px !important;
        line-height: 1.6 !important;
    }
    .stTextArea label { color: #D32F2F !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- BỘ NÃO AI "ĐA NHÂN CÁCH" ---
def get_ai_response(content):
    api_key = st.secrets.get("GOOGLE_API_KEY")
    if not api_key:
        return None, "Chưa dán API Key vô Secrets bà ơi!"
    
    genai.configure(api_key=api_key)
    
    # Danh sách các "anh" AI, hụt anh này tui gọi anh kia
    model_names = ['gemini-1.5-flash', 'gemini-1.5-flash-latest', 'gemini-pro']
    
    for name in model_names:
        try:
            model = genai.GenerativeModel(name)
            prompt = f"Hãy sửa lỗi chính tả và OCR cho văn bản sau, giữ nguyên ý nghĩa, chỉ trả về kết quả:\n\n{content}"
            response = model.generate_content(prompt)
            return response.text, None
        except Exception:
            continue # Anh này bận thì gọi anh tiếp theo
    
    return None, "Tất cả các anh AI đều đang đi vắng, bà dùng bản thô nhé!"

st.title("🔥 Máy Quét Linh Linh (Bản Quyết Chiến)")
uploaded_files = st.file_uploader("Kéo thả Ảnh hoặc PDF vào đây", type=["jpg", "jpeg", "png", "pdf"], accept_multiple_files=True)

if uploaded_files:
    if st.button("Kích Hoạt Máy Quét 🚀"):
        all_raw_text = ""
        images_to_show = []

        with st.spinner("Đang 'luyện' chữ..."):
            try:
                for file in uploaded_files:
                    if file.name.lower().endswith('.pdf'):
                        doc = fitz.open(stream=file.read(), filetype="pdf")
                        for i in range(len(doc)):
                            page = doc.load_page(i)
                            pix = page.get_pixmap()
                            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                            images_to_show.append(img)
                            all_raw_text += f"\n{pytesseract.image_to_string(img, lang='vie+eng')}\n"
                    else:
                        img = ImageOps.exif_transpose(Image.open(file)).convert('RGB')
                        images_to_show.append(img)
                        all_raw_text += f"\n{pytesseract.image_to_string(img, lang='vie+eng')}\n"

                # 1. Hiện ảnh
                for pic in images_to_show:
                    st.image(pic, width=500)

                # 2. Hiện bản thô (Luôn luôn có để xài)
                st.text_area("📄 Văn bản quét được (Bản thô):", all_raw_text, height=250)

                # 3. AI sửa lỗi chính tả
                if all_raw_text.strip():
                    with st.spinner("Đang ép AI nhấc máy sửa lỗi..."):
                        corrected, error = get_ai_response(all_raw_text)
                        if corrected:
                            st.success("✨ AI ĐÃ SỬA XONG! HÀNG NGON ĐÂY BÀ:")
                            st.text_area("💎 VĂN BẢN HOÀN HẢO:", corrected, height=450)
                        else:
                            st.warning(f"AI vẫn dỗi: {error}")
                
            except Exception as e:
                st.error(f"Lỗi: {e}")
