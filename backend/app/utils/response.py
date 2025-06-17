from flask import jsonify

def success_response(data=None, message="操作成功", status_code=200):
    """
    成功响应格式
    
    Args:
        data: 响应数据
        message: 响应消息
        status_code: HTTP状态码
        
    Returns:
        Flask Response对象
    """
    response = {
        'success': True,
        'message': message,
        'data': data
    }
    return jsonify(response), status_code

def error_response(message="操作失败", status_code=400, error_code=None):
    """
    错误响应格式
    
    Args:
        message: 错误消息
        status_code: HTTP状态码
        error_code: 错误代码
        
    Returns:
        Flask Response对象
    """
    response = {
        'success': False,
        'message': message,
        'data': None
    }
    
    if error_code:
        response['error_code'] = error_code
        
    return jsonify(response), status_code

def paginated_response(items, pagination, message="获取成功"):
    """
    分页响应格式
    
    Args:
        items: 分页数据
        pagination: 分页信息
        message: 响应消息
        
    Returns:
        Flask Response对象
    """
    data = {
        'items': items,
        'pagination': {
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    }
    
    return success_response(data, message) 