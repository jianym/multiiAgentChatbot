import cv2
import numpy as np
from PIL import ImageGrab

def getScreenshot():
    # 截屏并转为 OpenCV 格式
    screenshot = np.array(ImageGrab.grab())
    return cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)

    # return cv2.cvtColor(screenshot_rgb, cv2.COLOR_BGR2GRAY)


def color(screenshot_gray,targetImagePath: str):
    # 读取要找的图标（模板）
    template = cv2.imread(targetImagePath)
    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    w, h = template.shape[1], template.shape[0]
    # 匹配模板
    result = cv2.matchTemplate(screenshot_gray, template_gray, cv2.TM_CCOEFF_NORMED)
    # 获取匹配度最高的位置
    threshold = 0.8  # 匹配度阈值
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    if max_val >= threshold:
        top_left = max_loc
        center_x = top_left[0] + w // 2
        center_y = top_left[1] + h // 2
        print(f"图标中心坐标：({center_x}, {center_y})，匹配度：{max_val:.2f}")
    else:
        print("未找到图标")




