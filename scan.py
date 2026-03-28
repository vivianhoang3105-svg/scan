import streamlit as st
from PIL import Image, ImageOps
import pytesseract
import io
import fitz  # PyMuPDF
import google.generativeai as genai
from docx import Document  # Thư viện làm file Word nè bà!

# --- GIAO DIỆN VÀNG KEM & XANH LÁ ---
st.set_page_config(page_title="Máy Quét VIP Linh Linh", page_icon="🌿")

st.markdown("""
    <style>
    .stApp { background-color: #FEFDF5; color: #333333; }
    h1 { color: #2E7D32 !important; text-shadow: 1px 1px 2px white; }
    
    .stTextArea textarea { 
        background-color: #FFFDF0 !important; 
        color: #1A531A !important; 
        border: 2px solid #2E7D32 !important; 
        font-size: 17px !important;
        line-height: 1.6 !important;
    }
    .stTextArea label { color: #2E7D32 !important; font-weight: bold; }
    
    div.stButton > button { 
        background-color: #2E7D32 !important; color: white !important; 
        border-radius: 12px; font-weight: bold;
    }
    
    /* NÚT TẢI FILE WORD ĐỔI SANG MÀU CAM CHO DỄ NHÌN */
    div.stDownloadButton > button { 
        background-color: #E65100 !important; 
        color: white !important; 
        border: 2px solid #FFB300 !important; 
        font-weight: bold;
        font-size: 18px !important;
        width: 100%;
        padding: 12px;
    }
    div.stDownloadButton > button:hover {
        background-color: #EF6C00 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- AI DÒ SÓNG ---
def get_ai_response(content):
    api_key = st.secrets.get("GOOGLE_API_KEY")
    if not api_key: return None, "Thiếu API Key"
    genai.configure(api_key=api_key)
    try:
        target_model = None
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if 'gemini' in m.name.lower() and 'vision' not in m.name.lower():
                    target_model = m.name
                    break
        if not target_model: return None, "Không tìm thấy AI"
        model = genai.GenerativeModel(target_model)
        prompt = f"Sửa hết lỗi chính tả và OCR trong văn bản sau, trả về kết quả ngay ngắn, chuẩn văn phong hành chính:\n\n{content}"
        response = model.generate_content(prompt)
        return response.text, None
    except Exception as e: return None, str(e)

# --- HÀM TẠO FILE WORD BIẾN HÌNH ---
def create_word_file(text_content):
    doc = Document()
    # Thêm 1 dòng tiêu đề cho nó "chuyên nghiệp"
    doc.add_heading('VĂN BẢN TRÍCH XUẤT TỪ MÁY QUÉT', 0)
    doc.add_paragraph(text_content)
    
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

st.title("🌿 Máy Quét VIP Linh Linh")
st.write("Phiên bản siêu cấp: Quét xong xuất thẳng ra Microsoft Word!")

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

                # 2. Hiện bản thô
                st.text_area("📄 Văn bản quét được (Bản thô):", all_raw_text, height=200)

                # 3. AI sửa lỗi & Nút tải Word
                if all_raw_text.strip():
                    with st.spinner("Đang nhờ AI sửa lỗi..."):
                        corrected, error = get_ai_response(all_raw_text)
                        if corrected:
                            st.success("✨ AI ĐÃ SỬA XONG! Kéo xuống dưới cùng tải file Word nha bà!")
                            st.text_area("💎 VĂN BẢN HOÀN HẢO:", corrected, height=400)
                            
                            # --- NÚT TẢI WORD THẦN THÁNH ---
                            word_file_bytes = create_word_file(corrected)
                            st.download_button(
                                label="📥 TẢI XUỐNG FILE WORD (.docx)",
                                data=word_file_bytes,
                                file_name="TaiLieu_Quet_VIP.docx",
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                            )
                        else:
                            st.warning(f"AI bận: {error}")
            except Exception as e:
                st.error(f"Lỗi: {e}")
