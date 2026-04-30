# backend/models/ocr_model_loader.py
import os
import sys
import tensorflow as tf
import logging
import numpy as np

# ✅ 修复1：自动添加路径，解决找不到dataset的问题
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

logger = logging.getLogger(__name__)

# 模型配置
TARGET_SIZE = 64
MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "trained_models", "cn_ocr-best.ckpt")

# 加载字符集和模型（和你训练代码完全一致）
from dataset.casia_hwdb import load_characters
from models.cnn_net import build_net_003

characters = load_characters()
num_classes = len(characters)


# 加载模型
def load_ocr_model():
    try:
        model = build_net_003((TARGET_SIZE, TARGET_SIZE, 1), num_classes)
        model.load_weights(MODEL_PATH)
        logger.info("汉字OCR模型加载成功！")
        return model
    except Exception as e:
        logger.error(f"❌ 模型加载失败：{str(e)}")
        raise Exception(f"模型加载失败：{str(e)}")


# 全局加载模型
ocr_model = load_ocr_model()


# ✅ 修复2：补上路由需要的预测函数（解决导入报错）
def ocr_predict(image_array):
    """
    单字符OCR识别核心函数（严格对齐训练预处理）
    :param image_array: 前端预处理后的(H, W)灰度图numpy数组
    :return: 识别出的汉字
    """
    # 1. 加通道维度：(H, W) → (H, W, 1)（适配模型输入要求）
    img = tf.expand_dims(image_array, axis=-1)
    # 2. 缩放到64×64，和训练时完全一致
    img = tf.image.resize(img, (TARGET_SIZE, TARGET_SIZE))
    # 3. 归一化：(x - 128) / 128，和训练预处理100%匹配
    img = (img - 128.0) / 128.0
    # 4. 加Batch维度：(64, 64, 1) → (1, 64, 64, 1)（模型需要Batch输入）
    img = tf.expand_dims(img, axis=0)

    # 5. 模型推理（禁用训练模式，加速预测）
    pred = ocr_model(img, training=False).numpy()
    # 6. 取概率最高的字符
    pred_idx = np.argmax(pred[0])
    return characters[pred_idx]