from flask import jsonify

"""自定义异常类"""

class APIError(Exception):
    """API异常基类"""
    def __init__(self, message, status_code=500, payload=None):
        Exception.__init__(self)
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        result = {'error': self.message}
        if self.payload:
            result['details'] = self.payload
        return result

class ValidationError(APIError):
    """数据验证异常"""
    def __init__(self, message, payload=None):
        super().__init__(message, 400, payload)

class NotFoundError(APIError):
    """资源未找到异常"""
    def __init__(self, message, payload=None):
        super().__init__(message, 404, payload)

class AuthenticationError(APIError):
    """认证异常"""
    def __init__(self, message, payload=None):
        super().__init__(message, 401, payload)

class AuthorizationError(APIError):
    """授权异常"""
    def __init__(self, message, payload=None):
        super().__init__(message, 403, payload)

def handle_errors(app):
    """注册错误处理器"""
    
    @app.errorhandler(APIError)
    def handle_api_error(error):
        response = {
            'success': False,
            'error': {
                'code': error.__class__.__name__,
                'message': error.message
            }
        }
        if error.payload:
            response['error']['details'] = error.payload
            
        return jsonify(response), error.status_code
    
    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({
            'success': False,
            'error': {
                'code': 'NOT_FOUND',
                'message': '资源不存在'
            }
        }), 404
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': '服务器内部错误'
            }
        }), 500
    
    @app.errorhandler(422)
    def handle_validation_error(error):
        return jsonify({
            'success': False,
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': '请求参数验证失败',
                'details': getattr(error, 'data', {}).get('messages', {})
            }
        }), 422 