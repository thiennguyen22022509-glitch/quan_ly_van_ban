import os
from flask import Flask, render_template
from google.oauth2 import service_account
from googleapiclient.discovery import build
from pymongo import MongoClient
import certifi
from datetime import datetime

app = Flask(__name__)

# --- CẤU HÌNH CLOUD ---

# 1. Google Drive API
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
SERVICE_ACCOUNT_FILE = 'credentials.json'

# 2. MongoDB Atlas (Dán mã kết nối của bạn vào đây)
# NHỚ: Thay <password> bằng mật khẩu thực tế của bạn
MONGO_URI = "mongodb+srv://admin:<tn187321>@cluster0.abcde.mongodb.net/?retryWrites=true&w=majority"

try:
    client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
    db = client['DoAn_Cloud']
    collection = db['LichSuTruyCap']
except Exception as e:
    print(f"Lỗi kết nối MongoDB: {e}")

def get_drive_service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return build('drive', 'v3', credentials=creds)

@app.route('/')
def trang_chu():
    try:
        # 1. Lấy danh sách file từ Google Drive
        service = get_drive_service()
        results = service.files().list(pageSize=10, fields="files(id, name, webViewLink)").execute()
        items = results.get('files', [])

        # 2. Ghi lịch sử vào MongoDB Cloud (Đáp ứng yêu cầu môn học)
        log_data = {
            "thoi_gian": datetime.now().strftime("%H:%M:%S - %d/%m/%Y"),
            "hanh_dong": "Xem danh sach van ban",
            "so_luong": len(items)
        }
        collection.insert_one(log_data)

        return render_template('index.html', files=items)
    except Exception as e:
        return f"Hệ thống đang bảo trì Cloud. Lỗi: {e}"

# Dòng này cực kỳ quan trọng để chạy trên Vercel/Render
if __name__ == '__main__':
    app.run(debug=True)