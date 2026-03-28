import streamlit as st
from PIL import Image, ImageOps
import pytesseract
import io
import fitz  # PyMuPDF
import google.generativeai as genai

# --- CÀI ĐẶT GIAO DIỆN (HỎA & KIM) ---
st.set_page_config(page_title="Máy Quét Linh Linh", page_icon="🔥")

st.markdown("""
    <style>
    .stApp { background-color: #F5F5F5; }
    h1 { color: #D32F2F !important; text-shadow: 1px 1px 2px #FFD700; }
    div.stButton > button { background-color: #D32F2F !important; color: white !important; border: 2px solid #FFD700 !important; font-weight: bold; border-radius: 10px; }
    div.stDownloadButton > button { background-color: #FFD700 !important; color: #D32F2F !important; border: 2px solid #D32F2F !important; font-weight: bold; border-radius: 10px; }
    .stTextArea textarea { border: 2px solid #D32F2F !important; font-size: 16px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- CẤU HÌNH BỘ NÃO AI (SỬA LỖI TÊN MODEL 404) ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    # CHUẨN XÁC 100% LÀ TÊN NÀY, KHÔNG CÓ LATEST
    gemini_model = genai.GenerativeModel('gemini-1.5-flash') 
except Exception as e:
    st.error("Chưa thấy API Key hoặc lỗi cấu hình AI rồi bà ơi!")
    gemini_model = None

# --- GIAO DIỆN CHÍNH ---
st.title("🔥 Máy Quét Linh Linh (Chốt Hạ)")
st.write("Bản xịn nhất: Quét Ảnh/PDF -> Hiện Ảnh -> Lấy Chữ Thô -> AI Tự Sửa Lỗi!")

uploaded_files = st.file_uploader("Kéo thả Ảnh hoặc PDF vào đây", type=["jpg", "jpeg", "png", "pdf"], accept_multiple_files=True)

if uploaded_files:
    if st.button("Kích Hoạt Máy Quét 🚀"):
        all_raw_text = ""
        images_to_show = []
        images_for_pdf = []

        with st.spinner("Đang vắt chân lên cổ chạy..."):
            try:
                # 1. ĐỌC ẢNH & PDF
                for file in uploaded_files:
                    if file.name.lower().endswith('.pdf'):
                        doc = fitz.open(stream=file.read(), filetype="pdf")
                        for i in range(len(doc)):
                            page = doc.load_page(i)
                            pix = page.get_pixmap()
                            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                            images_to_show.append((img, f"PDF: {file.name} - Trang {i+1}"))
                            images_for_pdf.append(img)
                            text = pytesseract.image_to_string(img, lang='vie+eng')
                            all_raw_text += f"\n{text}\n"
                    else:
                        img = Image.open(file)
                        img = ImageOps.exif_transpose(img)
                        final_img = img.convert('RGB')
                        images_to_show.append((final_img, f"Ảnh: {file.name}"))
                        images_for_pdf.append(final_img)
                        text = pytesseract.image_to_string(final_img, lang='vie+eng')
                        all_raw_text += f"\n{text}\n"

                # 2. HIỆN ẢNH CHO BÀ NGẮM
                st.subheader("🖼️ Ảnh đã tải lên:")
                for pic, cap in images_to_show:
                    st.image(pic, caption=cap, use_container_width=True)

                # 3. TẠO NÚT TẢI PDF TỔNG HỢP
                if images_for_pdf:
                    pdf_output = io.BytesIO()
                    images_for_pdf[0].save(pdf_output, format='PDF', save_all=True, append_images=images_for_pdf[1:])
                    st.download_button(label="📥 Tải file PDF tổng hợp (Vàng Kim)", data=pdf_output.getvalue(), file_name="Ket_Qua_Quet.pdf")

                # 4. HIỆN BẢN THÔ (DỰ PHÒNG CÚP ĐIỆN)
                st.subheader("📄 Văn bản quét được (Bản thô):")
                st.text_area("Bản này chưa sửa lỗi, bà copy tạm nếu AI dỗi nha:", all_raw_text, height=200)

                # 5. NHỜ AI SỬA LỖI (BẢN VIP)
                if gemini_model and all_raw_text.strip():
                    with st.spinner("Đang nhờ siêu AI sửa lỗi chính tả..."):
                        try:
                            prompt = f"Hãy đóng vai biên tập viên văn phòng. Sửa toàn bộ lỗi chính tả, dấu câu, và lỗi nhận diện chữ (OCR) trong đoạn văn bản sau. Trả về định dạng đẹp, sạch sẽ, tuyệt đối KHÔNG GIẢI THÍCH GÌ THÊM:\n\n{all_raw_text}"
                            response = gemini_model.generate_content(prompt)
                            st.success("✨ AI ĐÃ SỬA LỖI XONG!")
                            st.text_area("Văn bản ĐÃ CHỈNH SỬA (Hàng xịn, Copy ở đây):", response.text, height=400)
                        except Exception as ai_err:
                            st.warning(f"AI đang bận một xíu (Lỗi: {ai_err}). Bà dùng bản thô ở trên nha!")
            except Exception as e:
                st.error(f"Lỗi hệ thống rồi: {e}")
