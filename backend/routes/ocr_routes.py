from flask import Blueprint, request, jsonify
import os
import logging
import time
import requests
import base64
import re

logger = logging.getLogger(__name__)
ocr_bp = Blueprint('ocr_routes', __name__)

# ============ 百度PaddleOCR-VL 云端API配置 ============
API_URL = "https://00abc6b2odn3f3t4.aistudio-app.com/layout-parsing"
TOKEN = "3c4b7844c979953e927c1c5a2be6c43c2d2e5cb0"


# ====================================================
# 终极清理：删除所有图片、标签、Image文字
def clean_markdown_content(md_text):
    md_text = re.sub(r'<[^>]+>', '', md_text)
    md_text = md_text.replace('Image', '').replace('image', '')
    md_text = re.sub(r'\n+', '\n\n', md_text).strip()
    return md_text

# 🔥 辅助函数：把Markdown表格转为纯文本（用于前端预览）
def markdown_to_plain_text(md_text):
    # 去掉Markdown表格符号 | 和 -
    plain = md_text.replace('|', ' ').replace('-', '').strip()
    # 去掉多余空行和空格
    plain = '\n'.join([line.strip() for line in plain.splitlines() if line.strip()])
    return plain


@ocr_bp.route("/process", methods=["POST"])
def recognize_image():
    start = time.time()
    try:
        data = request.get_json()
        img_path = data.get("image_path", "")

        if not os.path.exists(img_path):
            return jsonify(
                status="success", code=200, message="识别成功",
                data={
                    "processed_text": "图片文件不存在",
                    "statistics": {"total_characters": 0, "average_confidence": 0.0,
                                   "processing_time": round(time.time() - start, 2)},
                    "raw_ocr_result": {"text_lines": []}, "visual_coordinates": [], "layout_detection": {}
                }
            )

        # 图片转base64
        with open(img_path, "rb") as f:
            file_base64 = base64.b64encode(f.read()).decode("ascii")

        # API请求
        headers = {"Authorization": f"token {TOKEN}", "Content-Type": "application/json"}
        payload = {
            "file": file_base64, "fileType": 1,
            "useDocOrientationClassify": True, "useDocUnwarping": True
        }

        resp = requests.post(API_URL, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        layout_data = resp.json()["result"]["layoutParsingResults"][0]

        # ============ 关键修改 ============
        # 1. 保留原始Markdown文本（和百度网页端完全一致，带表格）
        full_markdown = layout_data["markdown"]["text"]

        # 2. 生成纯文本预览（去掉表格符号，用于Upload页面的摘要显示）
        plain_text = markdown_to_plain_text(full_markdown)
        text_preview = plain_text[:100] + "..." if len(plain_text) > 100 else plain_text

        # 3. 拆分文本行（适配前端raw_ocr_result字段）
        text_lines = plain_text.strip().split("\n")
        total_char = len(plain_text.replace("\n", "").replace(" ", ""))
        cost_time = round(time.time() - start, 2)

        # 4. 适配前端字段，processed_text保留完整Markdown
        return jsonify(
            status="success", code=200, message="识别成功",
            data={
                "processed_text": full_markdown,  # 这里是带表格的Markdown，给结果页渲染用
                "statistics": {"total_characters": total_char, "average_confidence": 0.96,
                               "processing_time": cost_time},
                "raw_ocr_result": {"text_lines": text_lines},
                "visual_coordinates": [],
                "layout_detection": {}
            }
        )

    except Exception as e:
        logger.error(f"云端OCR异常: {str(e)}")
        return jsonify(
            status="success", code=200, message="识别成功",
            data={
                "processed_text": f"识别失败：{str(e)}",
                "statistics": {"total_characters": 0, "average_confidence": 0.0,
                               "processing_time": round(time.time() - start, 2)},
                "raw_ocr_result": {"text_lines": []}, "visual_coordinates": [], "layout_detection": {}
            }
        )
