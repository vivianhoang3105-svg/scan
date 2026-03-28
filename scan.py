import streamlit as st
from PIL import Image, ImageOps
import pytesseract
import io
import fitz  # PyMuPDF
import google.generativeai as genai  # Thư viện Google AI

# --- CẤU HÌNH PHONG THỦY: HỎA & KIM (RESTORE) ---
st.set_page_config(page_title="Máy Quét Linh Linh", page_icon="🔥🚀")

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
    /* Khung text area */
    .stTextArea textarea {
        border: 2px solid #D32F2F !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CẤU HÌNH BỘ NÃO SỬA LỖI GEMINI ---
# Bà phải lấy API Key của Gemini dán vô file bí mật nha (Tui hướng dẫn ở dưới)
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    gemini_model = genai.GenerativeModel('gemini-1.5-flash-latest') # Bản flash cho nhanh
except Exception as e:
    st.error(f"Ối, chưa cấu hình API Key cho Gemini rồi! (Lỗi: {e})")
    st.info("App vẫn quét được chữ nhưng sẽ KHÔNG tự sửa lỗi chính tả được nha.")
    gemini_model = None

st.title("🔥 Máy Quét Linh Linh pro)")
st.write("Phiên bản đặc biệt rực rỡ may mắn, có siêu AI tự động sửa lỗi chính tả cho bà!")

# Chấp nhận cả ảnh và PDF
uploaded_files = st.file_uploader("Kéo thả Ảnh hoặc file PDF vào đây", 
                                  type=["jpg", "jpeg", "png", "pdf"], 
                                  accept_multiple_files=True)

if uploaded_files:
    if st.button("Kích Hoạt Máy Quét & Sửa Lỗi Siêu Tốc 🚀"):
        all_raw_text = ""
        images_for_pdf = []

        with st.spinner("Đang 'luyện' chữ và sửa lỗi, đợi tui xíu..."):
            try:
                # VÒNG LẶP XỬ LÝ QUÉT CHỮ TRƯỚC (Giữ nguyên code cũ)
                for file in uploaded_files:
                    if file.name.lower().endswith('.pdf'):
                        doc = fitz.open(stream=file.read(), filetype="pdf")
                        for page_index in range(len(doc)):
                            page = doc.load_page(page_index)
                            pix = page.get_pixmap()
                            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                            images_for_pdf.append(img)
                            text = pytesseract.image_to_string(img, lang='vie+eng')
                            all_raw_text += f"\n\n--- PDF: {file.name} (Trang {page_index + 1}) ---\n\n{text}"
                    else:
                        img = Image.open(file)
                        img = ImageOps.exif_transpose(img)
                        final_image = img.convert('RGB')
                        images_for_pdf.append(final_image)
                        text = pytesseract.image_to_string(final_image, lang='vie+eng')
                        all_raw_text += f"\n\n--- ẢNH: {file.name} ---\n\n{text}"

                # TẠO NÚT TẢI PDF TỔNG HỢP (Code cũ)
                if images_for_pdf:
                    pdf_output = io.BytesIO()
                    images_for_pdf[0].save(pdf_output, format='PDF', save_all=True, append_images=images_for_pdf[1:])
                    
                    st.success("Tạo xong file PDF rồi nè bà!")
                    st.download_button(label="📥 Tải file PDF tổng hợp (Vàng Kim)", 
                                       data=pdf_output.getvalue(), 
                                       file_name="Ket_Qua_Quet.pdf")
                
                # 🔥 BƯỚC SIÊU CẤP: DÙNG AI SỬA LỖI CHÍNH TẢ 🔥
                if gemini_model and all_raw_text.strip():
                    with st.spinner("Đang nhờ siêu AI Gemini biên tập và sửa lỗi chính tả..."):
                        # Tạo prompt cực gắt cho AI
                        prompt = f"""
                            Nhiệm vụ: Hãy đóng vai một biên tập viên chuyên nghiệp của văn phòng chính phủ Việt Nam.
                            Dưới đây là văn bản được bóc tách từ ảnh quét một công văn chính thức (OCR). Văn bản raw này bị rất nhiều lỗi: hallucination (chữ rác 's j'), sai dấu, thiếu ký tự (như 'thành phố' -> 't'), mất chữ.
                            Em phải:
                            1. Giữ nguyên ngữ cảnh, ý nghĩa và thông tin cốt lõi.
                            2. SỬA HẾT tất cả lỗi chính tả, thêm lại dấu câu và diacritics bị thiếu để tạo thành văn bản tiếng Việt chuẩn mực, mượt mà.
                            3. Không thêm thắt thông tin mới không có trong ngữ cảnh.
                            4. Trả lại định dạng ngay ngắn.
                            5. CHỈ TRẢ VỀ VĂN BẢN ĐÃ SỬA XONG, không giải thích gì thêm.

                            VĂN BẢN RAW (OCR):
                            ---
                            {all_raw_text}
                            ---

                            VĂN BẢN ĐÃ SỬA LỖI CHÍNH TẢ HOÀN CHỈNH:
                        """
                        try:
                            # Send to Gemini
                            response = gemini_model.generate_content(prompt)
                            corrected_text = response.text.strip()
                            st.success("Thành công rực rỡ! AI đã sửa sạch lỗi cho bà nha!")
                            st.text_area("Văn bản ĐÃ SỬA CHÍNH TẢ (Hàng VIP, Copy ở đây):", corrected_text, height=450)
                            st.info("Nếu bà muốn đối chiếu, kéo xuống dưới xem bản raw mờ mờ nhé.")
                        except Exception as gemini_err:
                            st.error(f"Trục trặc khi nhờ AI sửa lỗi rồi: {gemini_err}")
                            st.warning("Đây là bản raw, bà tự sửa tay giùm tui nhé.")
                            st.text_area("Văn bản bóc tách được (Raw):", all_raw_text, height=400)
                else:
                    st.text_area("Văn bản bóc tách được (Raw - Chưa cấu hình AI):", all_raw_text, height=400)
                
            except Exception as e:
                st.error(f"Lỗi rồi bà ơi: {e}")
                           
