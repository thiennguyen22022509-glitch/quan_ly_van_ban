import os
import json
from flask import Flask, render_template
from google.oauth2 import service_account
from googleapiclient.discovery import build
from pymongo import MongoClient
import certifi
from datetime import datetime

app = Flask(__name__)

# --- CẤU HÌNH ---
SERVICE_ACCOUNT_FILE = 'credentials.json'
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

# THAY LINK MONGODB CỦA BẠN VÀO ĐÂY
MONGO_URI = "mongodb+srv://admin:tn187321@cluster0.abcde.mongodb.net/?retryWrites=true&w=majority"

def get_drive_service():
    with open(SERVICE_ACCOUNT_FILE) as f:
        info = json.load(f)
    # Sửa lỗi chữ ký JWT bằng cách thay thế \n
    if 'private_key' in info:
        info['private_key'] = info['private_key'].replace('\\n', '\n')
    creds = service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
    return build('drive', 'v3', credentials=creds)

@app.route('/')
def trang_chu():
    try:
        # Kết nối MongoDB
        client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
        db = client['DoAn_Cloud']
        collection = db['LichSuTruyCap']

        # Lấy dữ liệu từ Google Drive
        service = get_drive_service()
        results = service.files().list(pageSize=10, fields="files(id, name, webViewLink)").execute()
        items = results.get('files', [])

        # Ghi log vào MongoDB
        collection.insert_one({
            "thoi_gian": datetime.now().strftime("%H:%M:%S - %d/%m/%Y"),
            "hanh_dong": "Xem danh sach van ban",
            "trang_thai": "Thanh cong"
        })
        return render_template('index.html', files=items)
    except Exception as e:
        return f"Đang kết nối Cloud... Lỗi xác thực Drive: {e}. Vui lòng kiểm tra quyền chia sẻ thư mục."

app = app # Dòng này cho Vercel
