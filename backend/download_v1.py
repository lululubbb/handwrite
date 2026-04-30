# 官方 ModelScope 下载 PaddleOCR-VL 模型
from modelscope import snapshot_download

# 下载官方模型到你的纯英文路径
model_dir = snapshot_download(
    "PaddlePaddle/PaddleOCR-VL",       # 官方模型名（你文档里的）
    local_dir="E:\\GitHub\\handwrite\\vl_models",  # 纯英文路径
    revision="master"
)

print("✅ 模型下载完成，路径：", model_dir)