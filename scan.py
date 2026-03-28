import streamlit as st
from PIL import Image, ImageOps
import pytesseract
import io
import fitz  # PyMuPDF
import google.generativeai as genai

# --- GIAO DIỆN HỎA & KIM SIÊU CẤP ---
st.set_page_config(page_title="Máy Quét của Linh Linh VIP", page_icon="🔥🚀")

st.markdown("""
    <style>
    .stApp { background-color: #F8F9FA; }
    h1 { color: #D32F2F! important; text-shadow: 2px 2px 4px #FFD700; font-family: 'Arial', sans-serif;}
    div.stButton > button { background-color: #00ff00 !important; color: lime !important; border: 2px solid #008000 !important; font-weight: bold; border-radius: 12px; padding: 10px 24px;}
    
    /* KHUNG ĐEN CHỮ VÀNG VIP */
    .stTextArea textarea { 
        background-color: #f0ffff !important; 
        color: #228b22 !important; 
        border: 2px solid #fff0f5 !important; 
        font-size: 18px !important;
        font-family: 'Courier New', Courier, monospace; 
        line-height: 1.6 !important;
    }
    .stTextArea label { color:#000000 !important; font-weight: bold; font-size: 20px; }
    div.stDownloadButton > button { background-color: #008000 !important; color: #ffa500 !important; border: 2px solid #D32F2F !important; font-weight: bold;}
    </style>
    """, unsafe_allow_html=True)

# --- BỘ NÃO AI "TỰ ĐỘNG DÒ SÓNG" ---
def get_ai_response(content):
    api_key = st.secrets.get("GOOGLE_API_KEY")
    if not api_key:
        return None, "Chưa dán API Key vô Secrets"
    
    genai.configure(api_key=api_key)
    
    try:
        # Tuyệt chiêu: Tự động hỏi Google xem tài khoản này được xài model nào
        target_model = None
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                # Ưu tiên lấy dòng gemini chuyên xử lý văn bản
                if 'gemini' in m.name.lower() and 'vision' not in m.name.lower():
                    target_model = m.name
                    break # Lấy ngay model đầu tiên tìm thấy
        
        if not target_model:
            return None, "Không tìm thấy quyền truy cập model AI trong tài khoản của bà."
            
        # Gọi đúng cái model đã dò được
        model = genai.GenerativeModel(target_model)
        prompt = f"Hãy đóng vai biên tập viên, sửa hết lỗi chính tả, lỗi OCR (như 's j' thành 'số', 't' thành 'thành phố'...) trong văn bản sau. Chỉ trả về kết quả đã sửa sạch đẹp:\n\n{content}"
        response = model.generate_content(prompt)
        return response.text, None
    except Exception as e:
        return None, f"Lỗi hệ thống AI: {str(e)}"

st.title("🔥 Máy Quét VIP (Bản Bất Bại)")
st.write("Phiên bản AI tự dò sóng, quét chữ nhả vàng!")

uploaded_files = st.file_uploader("Kéo thả Ảnh hoặc PDF vào đây", type=["jpg", "jpeg", "png", "pdf"], accept_multiple_files=True)

if uploaded_files:
    if st.button("Kích Hoạt Máy Quét 🚀"):
        all_raw_text = ""
        images_to_show = []

        with st.spinner("Đang 'luyện' chữ, đợi xíu nha..."):
            try:
                for file in uploaded_files:
                    if file.name.lower().endswith('.pdf'):
                        doc = fitz.open(stream=file.read(), filetype="pdf")
                        for page_index in range(len(doc)):
                            page = doc.load_page(page_index)
                            pix = page.get_pixmap()
                            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                            images_to_show.append((img, f"PDF: {file.name} (T{page_index+1})"))
                            text = pytesseract.image_to_string(img, lang='vie+eng')
                            all_raw_text += f"\n--- PDF: {file.name} (T{page_index+1}) ---\n\n{text}"
                    else:
                        img = Image.open(file)
                        img = ImageOps.exif_transpose(img)
                        final_image = img.convert('RGB')
                        images_to_show.append((final_image, f"Ảnh: {file.name}"))
                        text = pytesseract.image_to_string(final_image, lang='vie+eng')
                        all_raw_text += f"\n--- ẢNH: {file.name} ---\n\n{text}"

                # 1. Hiện ảnh
                for pic, cap in images_to_show:
                    st.image(pic, caption=cap, width=500)

                # 2. Hiện bản thô
                st.text_area("📄 Văn bản quét được (Bản thô):", all_raw_text, height=250)

                # 3. AI sửa lỗi
                if all_raw_text.strip():
                    with st.spinner("Đang dò sóng AI để sửa lỗi..."):
                        corrected, error = get_ai_response(all_raw_text)
                        if corrected:
                            st.success("✨ AI ĐÃ SỬA XONG! HÀNG NGON ĐÂY BÀ:")
                            st.text_area("💎 VĂN BẢN HOÀN HẢO (Copy ở đây):", corrected, height=450)
                        else:
                            st.warning(f"AI vẫn dỗi: {error}")
                
            except Exception as e:
                st.error(f"Lỗi: {e}")
