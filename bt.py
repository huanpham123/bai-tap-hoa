# app.py
import os
import logging
import requests
from flask import Flask, jsonify, render_template

app = Flask(__name__, template_folder="templates")

# Thay URL thật của bạn nếu khác
STT_PING_URL = "https://stt-mu.vercel.app/api/ping"

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("keepalive_app")


@app.route("/")
def index():
    """
    Trả về trang HTML (bt.html) nếu có ai mở trình duyệt.
    Trang này chỉ để hiển thị trạng thái ping lần cuối (tuỳ chọn).
    """
    return render_template("bt.html")


@app.route("/keepalive", methods=["GET"])
def keepalive():
    """
    Khi được gọi (ví dụ qua Cron trên Vercel), hàm này sẽ gửi GET tới STT_PING_URL.
    Trả về JSON để phản hồi ngắn gọn cho cron biết tình trạng.
    """
    try:
        logger.info(f"▶ Gửi ping tới STT server: {STT_PING_URL}")
        resp = requests.get(STT_PING_URL, timeout=15)
        status = resp.status_code

        if status == 200:
            logger.info("✅ STT server đang hoạt động (HTTP 200).")
            return jsonify({
                "ok": True,
                "status_code": 200,
                "message": "STT server is awake"
            })
        else:
            logger.warning(f"⚠️ Ping trả về HTTP {status}. Response: {resp.text[:100]}")
            return jsonify({
                "ok": False,
                "status_code": status,
                "message": f"Ping returned HTTP {status}"
            }), 502

    except Exception as e:
        logger.error(f"❌ Lỗi khi ping STT server: {e}")
        return jsonify({
            "ok": False,
            "status_code": -1,
            "message": f"Exception: {str(e)}"
        }), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"🚀 Keep-Alive Flask server chạy tại 0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port)
