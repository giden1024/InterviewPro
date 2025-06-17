import os
from werkzeug.utils import secure_filename

# 尝试导入magic，如果失败则跳过MIME类型检查
try:
    import magic
    HAS_MAGIC = True
except ImportError:
    HAS_MAGIC = False

ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc'}
MIME_TYPES = {
    'pdf': ['application/pdf'],
    'docx': ['application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
    'doc': ['application/msword']
}

def validate_file(file, max_size_mb=10):
    """
    验证上传的文件
    
    Args:
        file: Flask request.files对象
        max_size_mb: 最大文件大小(MB)
    
    Returns:
        tuple: (is_valid, error_message)
    """
    
    if not file or not file.filename:
        return False, "请选择要上传的文件"
    
    # 验证文件名
    filename = secure_filename(file.filename)
    if not filename:
        return False, "文件名无效"
    
    # 验证文件扩展名
    if '.' not in filename:
        return False, "文件必须有扩展名"
    
    extension = filename.rsplit('.', 1)[1].lower()
    if extension not in ALLOWED_EXTENSIONS:
        return False, f"不支持的文件格式，支持的格式: {', '.join(ALLOWED_EXTENSIONS)}"
    
    # 验证文件大小
    file.seek(0, 2)  # 移到文件末尾
    file_size = file.tell()
    file.seek(0)  # 重置到文件开头
    
    max_size_bytes = max_size_mb * 1024 * 1024
    if file_size > max_size_bytes:
        return False, f"文件太大，最大支持 {max_size_mb}MB"
    
    if file_size == 0:
        return False, "文件不能为空"
    
    # 验证MIME类型（如果python-magic可用）
    if HAS_MAGIC:
        try:
            mime_type = magic.from_buffer(file.read(1024), mime=True)
            file.seek(0)  # 重置文件指针
            
            expected_mimes = MIME_TYPES.get(extension, [])
            if expected_mimes and mime_type not in expected_mimes:
                return False, f"文件内容与扩展名不匹配"
                
        except Exception:
            # 如果magic检查失败，跳过MIME检查
            pass
    
    return True, None

def get_safe_filename(filename):
    """
    生成安全的文件名
    
    Args:
        filename: 原始文件名
        
    Returns:
        str: 安全的文件名
    """
    return secure_filename(filename)

def get_file_extension(filename):
    """
    获取文件扩展名
    
    Args:
        filename: 文件名
        
    Returns:
        str: 小写的文件扩展名
    """
    if '.' not in filename:
        return ''
    return filename.rsplit('.', 1)[1].lower()

def is_allowed_file(filename):
    """
    检查文件是否为允许的类型
    
    Args:
        filename: 文件名
        
    Returns:
        bool: 是否允许
    """
    return get_file_extension(filename) in ALLOWED_EXTENSIONS 