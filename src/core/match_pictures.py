import uiautomator2 as u2
import cv2
import os

# 连接设备
d = u2.connect() # 或者 u2.connect_usb(), u2.connect_wifi('ip_addr')

# --- 步骤 1: 定位你关心的核心 UI 元素 ---
# 示例：通过 resourceId 定位 (请替换为你实际的 selector)
# element_selector = "com.tencent.mm:id/your_element_id"
# 或者通过 text, description 等
element_selector = d(text="关键区域的文字") # 举例
# 或者更复杂的 XPath 等

# 确保元素存在且可见
if not element_selector.exists:
    print(f"错误：无法找到指定的 UI 元素！ Selector: {element_selector.selector}")
    # 进行错误处理或退出
else:
    target_element = element_selector
    print("成功定位到目标 UI 元素。")

    # --- 步骤 2: 获取元素的边界框 ---
    # bounds 返回的是 (左上角x, 左上角y, 右下角x, 右下角y)
    bounds = target_element.info['bounds'] # 或者 target_element.bounds
    x1, y1, x2, y2 = bounds['left'], bounds['top'], bounds['right'], bounds['bottom']
    print(f"元素边界框: 左={x1}, 上={y1}, 右={x2}, 下={y2}")

    # --- 步骤 3: 截取整个屏幕 ---
    # 先截取完整的屏幕图像，保存到临时文件
    screenshot_full_path = "temp_full_screenshot.png"
    d.screenshot(screenshot_full_path)
    print(f"已截取完整屏幕到: {screenshot_full_path}")

    # --- 步骤 4: 使用 OpenCV 裁剪截图 ---
    img_full = cv2.imread(screenshot_full_path)
    if img_full is None:
        print(f"错误：无法读取完整截图文件 {screenshot_full_path}")
    else:
        # 使用获取到的边界框坐标进行裁剪
        # 注意 OpenCV 数组索引是 [y1:y2, x1:x2]
        img_cropped = img_full[y1:y2, x1:x2]

        # 保存裁剪后的图片 (图片 B)
        cropped_screenshot_path = "cropped_screenshot.png" # 你最终用于比较的图片 B
        cv2.imwrite(cropped_screenshot_path, img_cropped)
        print(f"已裁剪并保存目标区域到: {cropped_screenshot_path}")

        # --- 步骤 5: 进行图片比较 ---
        # 现在 cropped_screenshot_path 就是你的图片 B
        # image_a_path 是你的模板图片路径 (可能也需要是对应区域的模板)
        image_a_path = "templates/your_template_region.png" # 确保模板也是对应区域

        # 调用之前定义的 compare_images 函数
        # similarity_score, are_similar = compare_images(image_a_path, cropped_screenshot_path, threshold=0.9)
        # print(f"与模板 {image_a_path} 的比较结果:")
        # if similarity_score is not None:
        #     print(f"SSIM: {similarity_score:.4f}, 相似: {are_similar}")

        # 清理临时完整截图文件 (可选)
        if os.path.exists(screenshot_full_path):
             os.remove(screenshot_full_path)
             print(f"已删除临时文件: {screenshot_full_path}")