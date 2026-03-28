import streamlit as st
from PIL import Image, ImageOps
import pytesseract
import io
import fitz  # PyMuPDF
import google.generativeai as genai

# --- PHONG THỦY HỎA & KIM: SIÊU NỔI BẬT ---
st.set_page_config(page_title="Máy Quét Linh Linh", page_icon="🔥")

st.markdown("""
    <style>
    /* Nền trắng bạc */
    .stApp { background-color: #F8F9FA; }
    
    /* Tiêu đề Đỏ Hỏa */
    h1 { color: #D32F2F !important; text-shadow: 2px 2px 4px #FFD700; font-family: 'Arial'; }
    
    /* Nút bấm Đỏ viền Vàng */
    div.stButton > button { 
        background-color: #D32F2F !important; 
        color: white !important; 
        border: 2px solid #FFD700 !important; 
        font-weight: bold; 
        border-radius: 12px;
        padding: 10px 24px;
    }
    
    /* Khung text "ĐEN NỔI BẬT" - Đây nè bà ơi! */
    .stTextArea textarea { 
        background-color: #1E1E1E !important; /* Nền đen sâu */
        color: #FFD700 !important; /* Chữ Vàng Kim cực nổi */
        border: 2px solid #D32F2F !important; /* Viền đỏ rực */
        font-size: 18px !important; 
        font-family: 'Courier New', Courier, monospace;
    }
    
    /* Label tiêu đề khung */
    .stTextArea label { color: #D32F2F !important; font-weight: bold; font-size: 20px; }
    
    /* Nút Tải file */
    div.stDownloadButton > button { background-color: #FFD700 !important; color: #D32F2F !important; border: 2px solid #D32F2F !important; }
    </style>
    """, unsafe_allow_html=True)

# --- CẤU HÌNH AI: DÙNG MODEL "TÊN CHUẨN" ---
api_key = st.secrets.get("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    # Tui dùng model gemini-1.5-flash (bản ổn định nhất)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    model = None

st.title("🔥 Máy Quét Linh Linh (Bản Siêu Cấp)")
st.write("Quét xong AI tự sửa lỗi, chữ nghĩa nổi bần bật luôn!")

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

                # 1. Hiện ảnh
                st.subheader("🖼️ Ảnh gốc của bà:")
                for pic, cap in images_to_show:
                    st.image(pic, caption=cap, use_column_width=True)

                # 2. Hiện bản quét thô (Nếu AI lỗi thì bà vẫn có cái này xài)
                st.text_area("📄 Văn bản quét được (Bản thô):", all_raw_text, height=250, key="raw")

                # 3. AI sửa lỗi (Bọc trong try-except để nếu lỗi nó không phá app)
                if model and all_raw_text.strip():
                    with st.spinner("Đang nhờ siêu AI Gemini sửa lỗi chính tả..."):
                        try:
                            prompt = f"Sửa hết lỗi chính tả và OCR (như 's j' thành 'số', 't' thành 'thành phố'...) trong đoạn sau. Trả về kết quả sạch đẹp:\n\n{all_raw_text}"
                            response = model.generate_content(prompt)
                            st.success("✨ AI ĐÃ SỬA LỖI XONG!")
                            st.text_area("💎 VĂN BẢN HOÀN HẢO (Copy ở đây):", response.text, height=400, key="ai")
                        except Exception as ai_err:
                            st.error(f"AI đang bận, bà dùng bản thô ở trên nhé! (Lỗi: {ai_err})")
                
            except Exception as e:
                st.error(f"Lỗi hệ thống: {e}")
