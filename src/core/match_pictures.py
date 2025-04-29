import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
import uiautomator2 as u2
from pathlib import Path

def capture_screenshot(device,save_path):
    """
    捕获屏幕截图并保存到指定路径。
    """
    screenshot = device.screenshot()
    screenshot.save(save_path)
    return save_path

def preprocess_image(image_path, target_size=(300, 300)):
    """
    读取并预处理图像：灰度化、调整大小。
    """
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"无法读取图像: {image_path}")
    img = cv2.resize(img, target_size)  # 调整大小
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # 转换为灰度图
    return img

def calculate_mse(image1, image2):
    """计算均方误差（MSE）"""
    err = np.sum((image1.astype("float") - image2.astype("float")) ** 2)
    err /= float(image1.shape[0] * image1.shape[1])
    return err

def compare_images(image_path_a, image_path_b):
    """对比两张图片的相似度"""
    # 预处理图片
    img_a = preprocess_image(image_path_a)
    img_b = preprocess_image(image_path_b)

    # 计算 SSIM
    ssim_score, _ = ssim(img_a, img_b, full=True)
    
    # 计算 MSE
    mse_score = calculate_mse(img_a, img_b)

    return ssim_score, mse_score