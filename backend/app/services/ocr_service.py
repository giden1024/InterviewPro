import os
import cv2
import numpy as np
from PIL import Image
import pytesseract
import logging
from typing import Dict, List, Optional, Tuple
import re

logger = logging.getLogger(__name__)

class OCRService:
    """OCR文字识别服务"""
    
    def __init__(self):
        self.supported_formats = ['png', 'jpg', 'jpeg', 'tiff', 'bmp', 'webp']
        self.max_image_size = 10 * 1024 * 1024  # 10MB
        
    def extract_text_from_image(self, image_path: str, language: str = 'eng+chi_sim') -> Dict:
        """
        从图片中提取文字
        
        Args:
            image_path: 图片文件路径
            language: OCR识别语言，默认英文+简体中文
            
        Returns:
            识别结果字典
        """
        try:
            # 验证文件存在
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"图片文件不存在: {image_path}")
            
            # 验证文件大小
            file_size = os.path.getsize(image_path)
            if file_size == 0:
                raise ValueError("图片文件为空")
            if file_size > self.max_image_size:
                raise ValueError("图片文件过大")
            
            # 预处理图片
            processed_image = self._preprocess_image(image_path)
            
            # 执行OCR识别
            text = self._perform_ocr(processed_image, language)
            
            # 后处理文本
            cleaned_text = self._clean_text(text)
            
            if not cleaned_text or len(cleaned_text.strip()) < 5:
                return {
                    'success': False,
                    'text': '',
                    'error': '未能从图片中识别到有效文字内容'
                }
            
            return {
                'success': True,
                'text': cleaned_text,
                'original_text': text,
                'language': language,
                'error': None
            }
            
        except Exception as e:
            error_msg = f"OCR识别失败: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'text': '',
                'error': error_msg
            }
    
    def _preprocess_image(self, image_path: str) -> np.ndarray:
        """预处理图片以提高OCR识别准确率"""
        try:
            # 使用PIL加载图片
            pil_image = Image.open(image_path)
            
            # 转换为RGB模式
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            # 转换为OpenCV格式
            opencv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            
            # 转换为灰度图
            gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
            
            # 应用高斯滤波减少噪声
            gray = cv2.GaussianBlur(gray, (3, 3), 0)
            
            # 自适应阈值化
            thresh = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            
            # 形态学操作去除噪声
            kernel = np.ones((1, 1), np.uint8)
            thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
            
            return thresh
            
        except Exception as e:
            logger.warning(f"图片预处理失败，使用原图: {e}")
            # 如果预处理失败，返回原图的灰度版本
            opencv_image = cv2.imread(image_path)
            return cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
    
    def _perform_ocr(self, image: np.ndarray, language: str) -> str:
        """执行OCR识别"""
        # 配置OCR参数
        config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!"#$%&\'()*+,-./:;<=>?@[\]^_`{|}~ 。，、；：？！""''（）【】《》〈〉…—·'
        
        try:
            # 使用pytesseract进行OCR识别
            text = pytesseract.image_to_string(image, lang=language, config=config)
            return text
        except Exception as e:
            logger.error(f"OCR识别过程失败: {e}")
            # 尝试使用默认配置
            try:
                text = pytesseract.image_to_string(image, lang=language)
                return text
            except Exception as e2:
                logger.error(f"OCR识别完全失败: {e2}")
                raise e2
    
    def _clean_text(self, text: str) -> str:
        """清理和格式化识别的文本"""
        if not text:
            return ""
        
        # 移除多余的空白字符
        text = re.sub(r'\s+', ' ', text)
        
        # 移除行首行尾空白
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        text = '\n'.join(lines)
        
        # 移除特殊字符（保留常见标点）
        text = re.sub(r'[^\w\s\u4e00-\u9fff.,;:!?()[\]{}"\'-]', '', text)
        
        return text.strip()
    
    def validate_image_file(self, file_path: str) -> Tuple[bool, str]:
        """验证图片文件是否有效"""
        try:
            if not os.path.exists(file_path):
                return False, "文件不存在"
            
            # 检查文件扩展名
            _, ext = os.path.splitext(file_path.lower())
            if ext[1:] not in self.supported_formats:
                return False, f"不支持的图片格式，支持: {', '.join(self.supported_formats)}"
            
            # 尝试打开图片
            with Image.open(file_path) as img:
                # 检查图片尺寸
                width, height = img.size
                if width < 50 or height < 50:
                    return False, "图片尺寸太小"
                if width > 10000 or height > 10000:
                    return False, "图片尺寸太大"
            
            return True, "验证通过"
            
        except Exception as e:
            return False, f"图片文件无效: {str(e)}" 