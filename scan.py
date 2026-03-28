import streamlit as st
from PIL import Image, ImageOps
import pytesseract
import io
import fitz  # PyMuPDF
import google.generativeai as genai
from docx import Document

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(page_title="Máy Quét VIP Linh Linh", page_icon="🌿⚔️")

# --- 2. GIAO DIỆN VÀ MÀU SẮC (CSS) ---
st.markdown("""
    <style>
    /* Nền ứng dụng màu Vàng Kem */
    .stApp { background-color: #FEFDF5; }
    
    /* Tiêu đề chính */
    h1 { color: #2E7D32 !important; text-shadow: 1px 1px 2px white; font-family: 'Segoe UI', sans-serif;}
    
    /* FIX LỖI TÀNG HÌNH: Ép chữ của Nút Gạt và Kéo thả thành Xanh Lá Cây đậm */
    p, label, .stMarkdown p { color: #2E7D32 !important; font-weight: 500; font-size: 16px; }

    /* Nút Kích Hoạt Xanh Lá */
    div.stButton > button { 
        background-color: #2E7D32 !important; 
        border: 2px solid #A5D6A7 !important; 
        border-radius: 12px; 
    }
    /* Chữ bên trong Nút Kích Hoạt là MÀU TRẮNG */
    div.stButton > button p { color: white !important; font-weight: bold; font-size: 16px !important; }
    
    /* Khung text hiển thị văn bản */
    .stTextArea textarea { 
        background-color: #FFFDF0 !important; 
        color: #1A531A !important; 
        border: 2px solid #2E7D32 !important; 
        font-size: 17px !important; 
        font-family: 'Segoe UI', sans-serif;
    }
    .stTextArea label p { color: #2E7D32 !important; font-weight: bold; font-size: 18px !important; }
    
    /* Nút Tải về Màu Cam */
    div.stDownloadButton > button { 
        background-color: #E65100 !important; 
        border: 2px solid #FFD700 !important; 
    }
    /* Chữ bên trong Nút Tải về là MÀU TRẮNG */
    div.stDownloadButton > button p { color: white !important; font-weight: bold; font-size: 18px !important; }
    
    /* Sơn Nút Gạt (Toggle) thành Xanh Lá khi được bật */
    div[data-testid="stWidgetToggle"] label div[data-checked="true"] {
        background-color: #2E7D32 !important;
    }
    
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 3. BỘ NÃO AI GEMINI ---
def get_ai_response(content):
    api_key = st.secrets.get("GOOGLE_API_KEY")
    if not api_key: return None, "Chưa dán API Key vô Secrets"
    genai.configure(api_key=api_key)
    try:
        target_model = None
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if 'gemini' in m.name.lower() and 'vision' not in m.name.lower():
                    target_model = m.name
                    break
        if not target_model: return None, "Không tìm thấy model AI."
        model =
