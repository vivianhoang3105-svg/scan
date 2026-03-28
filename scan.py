import streamlit as st
from PIL import Image, ImageOps
import pytesseract
import io
import fitz  # PyMuPDF
import google.generativeai as genai
from docx import Document # Thư viện làm file Word

# --- GIAO DIỆN VÀNG KEM & XANH LÁ (BẢN MỘC QUYẾT CHIẾN) ---
# Tui đổi cái Icon 🌿 thành 🌿⚔️ cho hợp mệnh mới nha bà!
st.set_page_config(page_title="Máy Quét VIP Linh Linh", page_icon="🌿⚔️")

st.markdown("""
    <style>
    /* Nền vàng kem toàn app */
    .stApp { background-color: #FEFDF5; color: #333333; }
    
    /* Tiêu đề Xanh lá cây đậm nổi bật */
    h1 { 
        color: #2E7D32 !important; 
        text-shadow: 1px 1px 2px white; 
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Text thường cho dễ đọc */
    p, div { color: #444444; }

    /* Nút bấm Xanh lá */
    div.stButton > button { 
        background-color: #2E7D32 !important; 
        color: white !important; 
        border: 2px solid #A5D6A7 !important; /* Viền xanh nhạt */
        font-weight: bold; 
        border-radius: 12px;
        padding: 10px 24px;
        transition: 0.3s;
    }
    div.stButton > button p { color: white !important; }
    div.stButton > button:hover {
        background-color: #1B5E20 !important; /* Xanh đậm hơn khi hover */
        transform: scale(1.05);
    }
    
    /* KHUNG VĂN BẢN NỀN VÀNG KEM CHỮ XANH LÁ */
    .stTextArea textarea { 
        background-color: #FFFDF0 !important; /* Nền kem rất nhạt */
        color: #1A531A !important; /* Chữ Xanh lá cây đậm cực kỳ nổi và dễ đọc */
        border: 2px solid #2E7D32 !important; /* Viền Xanh rực */
        font-size: 17px !important;
        font-family: 'Segoe UI', sans-serif; /* Font chữ văn phòng hiện đại */
        line-height: 1.6 !important;
    }
    
    /* Label tiêu đề khung */
    .stTextArea label { color: #2E7D32 !important; font-weight: bold; font-size: 18px; }
    
    /* NÚT TẢI VỀ MÀU CAM RỰC RỠ DỄ NHÌN */
    div.stDownloadButton > button { 
        background-color: #E65100 !important; 
        color: white !important; 
        border: 2px solid #FFD700 !important; 
        font-weight: bold;
        font-size: 18px !important;
        width: 100%;
        padding: 12px;
    }
    div.stDownloadButton > button:hover {
        background-color: #EF6C00 !important;
    }
    
    /* Ẩn footer */
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- BỘ NÃO AI "TỰ ĐỘNG DÒ SÓNG" (BẤT BẠI) ---
def get_ai_response(content):
    api_key = st.secrets.get("GOOGLE_API_KEY")
    if not api_key:
        return None, "Chưa dán API Key vô Secrets bà ơi!"
    
    genai.configure(api_key=api_key)
    
    try:
        target_model = None
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if 'gemini' in m.name.lower() and 'vision' not in m.name.lower():
                    target_model = m.name
                    break
        
        if not target_model:
            return None, "Không tìm thấy model AI hợp lệ."
            
        model = genai.GenerativeModel(target_model)
        prompt = f"Hãy đóng vai biên tập viên chuyên nghiệp, sửa hết lỗi chính tả và OCR (như 's j' thành 'số', 't' thành 'thành phố'...) trong văn bản sau. Chỉ trả về kết quả đã sửa sạch đẹp, ngay ngắn:\n\n{content}"
        response = model.generate_content(prompt)
        return response.text, None
    except Exception as e:
        return None, f"Lỗi AI: {str(e)}"

# --- HÀM TẠO FILE WORD BIẾN HÌNH ---
def create_word_file(text_content):
    doc = Document()
    # Thêm 1 dòng tiêu đề cho nó "chuyên nghiệp"
    doc.add_heading('VĂN BẢN TRÍCH XUẤT TỪ MÁY QUÉT LINH LINH', 0)
    doc.add_paragraph(text_content)
    
    # Canh lề một xíu cho nó chuyên nghiệp
    for paragraph in doc.paragraphs:
        paragraph.paragraph_format.alignment = 0 # 0 là Left, bà có thể đổi thành 3 cho Justify

    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

# --- TIÊU ĐỀ MỚI CÓ CẢ LÁ VÀ KIẾM ---
st.title("🌿⚔️ Máy Quét VIP Linh Linh")
st.write("Quét xong AI tự sửa lỗi, chữ nghĩa xanh kem dịu mắt, xuất thẳng ra Word luôn!")

uploaded_files = st.file_uploader("Kéo thả Ảnh hoặc PDF vào đây", type=["jpg", "jpeg", "png", "pdf"], accept_multiple_files=True)

if uploaded_files:
    if st.button("Kích Hoạt Máy Quét 🚀"):
        all_raw_text = ""
        images_to_show = []

        with st.spinner("Đang 'luyện' chữ, đợi xíu nha..."):
            try:
                for file in uploaded_files:
                    # PDF
                    if file.name.lower().endswith('.pdf'):
                        doc = fitz.open(stream=file.read(), filetype="pdf")
                        for page_index in range(len(doc)):
                            page = doc.load_page(page_index)
                            pix = page.get_pixmap()
                            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                            images_to_show.append((img, f"PDF: {file.name} (T{page_index+1})"))
                            text = pytesseract.image_to_string(img, lang='vie+eng')
                            all_raw_text += f"\n--- PDF: {file.name} (T{page_index+1}) ---\n\n{text}"
                    # Ảnh
                    else:
                        img = ImageOps.exif_transpose(Image.open(file)).convert('RGB')
                        images_to_show.append((img, f"Ảnh: {file.name}"))
                        text = pytesseract.image_to_string(img, lang='vie+eng')
                        all_raw_text += f"\n--- ẢNH: {file.name} ---\n\n{text}"

                # 1. Hiện ảnh
                for pic, cap in images_to_show:
                    st.image(pic, caption=cap, width=500)

                # 2. Hiện bản thô (Vẫn màu kem chữ xanh)
                st.text_area("📄 Văn bản quét được (Bản thô):", all_raw_text, height=250)

                # 3. AI sửa lỗi chính tả
                if all_raw_text.strip():
                    with st.spinner("Đang nhờ AI Gemini sửa lỗi chính tả..."):
                        corrected, error = get_ai_response(all_raw_text)
                        if corrected:
                            st.success("✨ AI ĐÃ SỬA XONG! HÀNG NGON ĐÂY BÀ:")
                            st.text_area("💎 VĂN BẢN HOÀN HẢO (Copy ở đây):", corrected, height=450)
                            
                            # --- NÚT TẢI WORD THẦN THÁNH ---
                            word_file_bytes = create_word_file(corrected)
                            st.download_button(
                                label="📥 TẢI XUỐNG FILE WORD (.docx)",
                                data=word_file_bytes,
                                file_name="Quet_LinhLinh_Pro.docx",
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                            )
                        else:
                            st.warning(f"AI đang bận: {error}")
                
            except Exception as e:
                st.error(f"Lỗi hệ thống: {e}")
