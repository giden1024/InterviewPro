import os
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge

from app.extensions import db
from app.models.resume import Resume, ResumeStatus
from app.services.resume_parser import ResumeParser
from app.utils.response import success_response, error_response
from app.utils.validation import validate_file

resumes_bp = Blueprint('resumes', __name__)

# 支持的文件格式
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def allowed_file(filename):
    """检查文件格式是否支持"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_extension(filename):
    """获取文件扩展名"""
    return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''

@resumes_bp.route('', methods=['GET'])
@jwt_required()
def get_resumes():
    """获取用户简历列表"""
    try:
        user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # 限制每页数量
        per_page = min(per_page, 50)
        
        resumes = Resume.query.filter_by(user_id=user_id)\
                            .order_by(Resume.uploaded_at.desc())\
                            .paginate(
                                page=page, 
                                per_page=per_page, 
                                error_out=False
                            )
        
        return success_response({
            'resumes': [resume.to_dict() for resume in resumes.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': resumes.total,
                'pages': resumes.pages,
                'has_next': resumes.has_next,
                'has_prev': resumes.has_prev
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"获取简历列表失败: {str(e)}")
        return error_response("获取简历列表失败", 500)

@resumes_bp.route('', methods=['POST'])
@jwt_required()
def upload_resume():
    """上传简历文件"""
    try:
        user_id = get_jwt_identity()
        
        # 检查请求中是否有文件
        if 'file' not in request.files:
            return error_response("请选择要上传的文件", 400)
        
        file = request.files['file']
        
        # 检查文件是否为空
        if file.filename == '':
            return error_response("请选择要上传的文件", 400)
        
        # 检查文件格式
        if not allowed_file(file.filename):
            return error_response(
                f"不支持的文件格式，请上传 {', '.join(ALLOWED_EXTENSIONS)} 格式的文件", 
                400
            )
        
        # 检查文件大小
        file.seek(0, 2)  # 移到文件末尾
        file_size = file.tell()
        file.seek(0)  # 重置到文件开头
        
        if file_size > MAX_FILE_SIZE:
            return error_response(f"文件太大，最大支持 {MAX_FILE_SIZE // 1024 // 1024}MB", 400)
        
        # 生成安全的文件名
        original_filename = secure_filename(file.filename)
        file_extension = get_file_extension(original_filename)
        filename = f"{uuid.uuid4().hex}.{file_extension}"
        
        # 确保上传目录存在
        upload_dir = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        
        file_path = os.path.join(upload_dir, filename)
        
        # 保存文件
        file.save(file_path)
        
        # 创建简历记录
        resume = Resume(
            user_id=user_id,
            filename=filename,
            original_filename=original_filename,
            file_path=file_path,
            file_size=file_size,
            file_type=file_extension,
            status=ResumeStatus.UPLOADED
        )
        
        db.session.add(resume)
        db.session.commit()
        
        # 异步解析简历（这里先同步处理，后续可以改为异步任务）
        try:
            resume.status = ResumeStatus.PROCESSING
            db.session.commit()
            
            parser = ResumeParser()
            result = parser.parse_resume(file_path, file_extension)
            
            if result['success']:
                # 更新简历信息
                resume.status = ResumeStatus.PROCESSED
                resume.raw_text = result['raw_text']
                resume.parsed_content = result['parsed_data']
                resume.processed_at = datetime.utcnow()
                
                # 提取的关键信息
                parsed_data = result['parsed_data']
                resume.name = parsed_data.get('name')
                resume.email = parsed_data.get('email')
                resume.phone = parsed_data.get('phone')
                resume.skills = parsed_data.get('skills', [])
                resume.experience = parsed_data.get('experience', [])
                resume.education = parsed_data.get('education', [])
                
            else:
                resume.status = ResumeStatus.FAILED
                resume.error_message = result['error']
            
            db.session.commit()
            
        except Exception as parse_error:
            current_app.logger.error(f"简历解析失败: {str(parse_error)}")
            resume.status = ResumeStatus.FAILED
            resume.error_message = str(parse_error)
            db.session.commit()
        
        return success_response({
            'resume': resume.to_dict(),
            'message': '简历上传成功，正在解析中...'
        }, 201)
        
    except RequestEntityTooLarge:
        return error_response(f"文件太大，最大支持 {MAX_FILE_SIZE // 1024 // 1024}MB", 413)
    except Exception as e:
        current_app.logger.error(f"简历上传失败: {str(e)}")
        return error_response("简历上传失败", 500)

@resumes_bp.route('/<int:resume_id>', methods=['GET'])
@jwt_required()
def get_resume(resume_id):
    """获取单个简历详情"""
    try:
        user_id = get_jwt_identity()
        
        resume = Resume.query.filter_by(id=resume_id, user_id=user_id).first()
        if not resume:
            return error_response("简历不存在", 404)
        
        return success_response({'resume': resume.to_dict()})
        
    except Exception as e:
        current_app.logger.error(f"获取简历详情失败: {str(e)}")
        return error_response("获取简历详情失败", 500)

@resumes_bp.route('/<int:resume_id>', methods=['DELETE'])
@jwt_required()
def delete_resume(resume_id):
    """删除简历"""
    try:
        user_id = get_jwt_identity()
        
        resume = Resume.query.filter_by(id=resume_id, user_id=user_id).first()
        if not resume:
            return error_response("简历不存在", 404)
        
        # 删除文件
        try:
            if os.path.exists(resume.file_path):
                os.remove(resume.file_path)
        except Exception as e:
            current_app.logger.warning(f"删除文件失败: {str(e)}")
        
        # 删除数据库记录
        db.session.delete(resume)
        db.session.commit()
        
        return success_response({'message': '简历删除成功'})
        
    except Exception as e:
        current_app.logger.error(f"删除简历失败: {str(e)}")
        return error_response("删除简历失败", 500)

@resumes_bp.route('/<int:resume_id>/reparse', methods=['POST'])
@jwt_required()
def reparse_resume(resume_id):
    """重新解析简历"""
    try:
        user_id = get_jwt_identity()
        
        resume = Resume.query.filter_by(id=resume_id, user_id=user_id).first()
        if not resume:
            return error_response("简历不存在", 404)
        
        if not os.path.exists(resume.file_path):
            return error_response("简历文件不存在", 404)
        
        # 重新解析
        resume.status = ResumeStatus.PROCESSING
        resume.error_message = None
        db.session.commit()
        
        parser = ResumeParser()
        result = parser.parse_resume(resume.file_path, resume.file_type)
        
        if result['success']:
            # 更新简历信息
            resume.status = ResumeStatus.PROCESSED
            resume.raw_text = result['raw_text']
            resume.parsed_content = result['parsed_data']
            resume.processed_at = datetime.utcnow()
            
            # 提取的关键信息
            parsed_data = result['parsed_data']
            resume.name = parsed_data.get('name')
            resume.email = parsed_data.get('email')
            resume.phone = parsed_data.get('phone')
            resume.skills = parsed_data.get('skills', [])
            resume.experience = parsed_data.get('experience', [])
            resume.education = parsed_data.get('education', [])
            
        else:
            resume.status = ResumeStatus.FAILED
            resume.error_message = result['error']
        
        db.session.commit()
        
        return success_response({
            'resume': resume.to_dict(),
            'message': '重新解析完成'
        })
        
    except Exception as e:
        current_app.logger.error(f"重新解析简历失败: {str(e)}")
        return error_response("重新解析简历失败", 500)

@resumes_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_resume_stats():
    """获取简历统计信息"""
    try:
        user_id = int(get_jwt_identity())
        
        # 统计各状态的简历数量
        stats = {
            'total': Resume.query.filter_by(user_id=user_id).count(),
            'uploaded': Resume.query.filter_by(user_id=user_id, status=ResumeStatus.UPLOADED).count(),
            'processing': Resume.query.filter_by(user_id=user_id, status=ResumeStatus.PROCESSING).count(),
            'processed': Resume.query.filter_by(user_id=user_id, status=ResumeStatus.PROCESSED).count(),
            'failed': Resume.query.filter_by(user_id=user_id, status=ResumeStatus.FAILED).count(),
        }
        
        # 最近上传的简历
        recent_resumes = Resume.query.filter_by(user_id=user_id)\
                               .order_by(Resume.uploaded_at.desc())\
                               .limit(5)\
                               .all()
        
        return success_response({
            'stats': stats,
            'recent_resumes': [resume.to_dict() for resume in recent_resumes]
        })
        
    except Exception as e:
        current_app.logger.error(f"获取简历统计失败: {str(e)}")
        return error_response("获取简历统计失败", 500)

@resumes_bp.route('/<int:resume_id>/download', methods=['GET'])
@jwt_required()
def download_resume(resume_id):
    """下载简历文件"""
    try:
        user_id = int(get_jwt_identity())
        
        resume = Resume.query.filter_by(id=resume_id, user_id=user_id).first()
        if not resume:
            return error_response("简历不存在", 404)
        
        if not os.path.exists(resume.file_path):
            return error_response("简历文件不存在", 404)
        
        return send_file(
            resume.file_path,
            as_attachment=True,
            download_name=resume.original_filename,
            mimetype='application/octet-stream'
        )
        
    except Exception as e:
        current_app.logger.error(f"下载简历失败: {str(e)}")
        return error_response("下载简历失败", 500)

@resumes_bp.route('/<int:resume_id>/preview', methods=['GET'])
@jwt_required()
def preview_resume(resume_id):
    """预览简历内容"""
    try:
        user_id = int(get_jwt_identity())
        
        resume = Resume.query.filter_by(id=resume_id, user_id=user_id).first()
        if not resume:
            return error_response("简历不存在", 404)
        
        if resume.status != ResumeStatus.PROCESSED:
            return error_response("简历尚未处理完成，无法预览", 400)
        
        # 格式化简历内容用于预览
        preview_data = {
            'basic_info': {
                'name': resume.name,
                'email': resume.email,
                'phone': resume.phone
            },
            'skills': resume.skills or [],
            'experience': resume.experience or [],
            'education': resume.education or [],
            'raw_text_preview': resume.raw_text[:500] + "..." if resume.raw_text and len(resume.raw_text) > 500 else resume.raw_text
        }
        
        return success_response({
            'resume': resume.to_dict(),
            'preview': preview_data
        })
        
    except Exception as e:
        current_app.logger.error(f"预览简历失败: {str(e)}")
        return error_response("预览简历失败", 500)

@resumes_bp.route('/<int:resume_id>/analyze', methods=['POST'])
@jwt_required()
def analyze_resume(resume_id):
    """智能分析简历"""
    try:
        user_id = int(get_jwt_identity())
        
        resume = Resume.query.filter_by(id=resume_id, user_id=user_id).first()
        if not resume:
            return error_response("简历不存在", 404)
        
        if resume.status != ResumeStatus.PROCESSED:
            return error_response("简历尚未处理完成，无法分析", 400)
        
        from app.services.resume_analyzer import ResumeAnalyzer
        analyzer = ResumeAnalyzer()
        analysis = analyzer.analyze_resume(resume)
        
        return success_response({
            'resume_id': resume_id,
            'analysis': analysis
        })
        
    except Exception as e:
        current_app.logger.error(f"简历分析失败: {str(e)}")
        return error_response("简历分析失败", 500)

@resumes_bp.route('/search', methods=['POST'])
@jwt_required()
def search_resumes():
    """高级搜索简历"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json() or {}
        
        query = Resume.query.filter_by(user_id=user_id)
        
        # 按状态筛选
        if 'status' in data:
            query = query.filter(Resume.status == ResumeStatus(data['status']))
        
        # 按技能搜索
        if 'skills' in data and data['skills']:
            for skill in data['skills']:
                query = query.filter(Resume.skills.contains([skill]))
        
        # 按姓名搜索
        if 'name' in data and data['name']:
            query = query.filter(Resume.name.ilike(f"%{data['name']}%"))
        
        # 按日期范围搜索
        if 'date_from' in data and data['date_from']:
            from datetime import datetime
            date_from = datetime.fromisoformat(data['date_from'])
            query = query.filter(Resume.uploaded_at >= date_from)
        
        if 'date_to' in data and data['date_to']:
            from datetime import datetime
            date_to = datetime.fromisoformat(data['date_to'])
            query = query.filter(Resume.uploaded_at <= date_to)
        
        # 分页
        page = data.get('page', 1)
        per_page = min(data.get('per_page', 20), 100)
        
        resumes = query.order_by(Resume.uploaded_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return success_response({
            'resumes': [resume.to_dict() for resume in resumes.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': resumes.total,
                'pages': resumes.pages,
                'has_next': resumes.has_next,
                'has_prev': resumes.has_prev
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"搜索简历失败: {str(e)}")
        return error_response("搜索简历失败", 500)

@resumes_bp.route('/batch', methods=['POST'])
@jwt_required()
def batch_operations():
    """批量操作简历"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json() or {}
        
        resume_ids = data.get('resume_ids', [])
        operation = data.get('operation')
        
        if not resume_ids or not operation:
            return error_response("请提供简历ID列表和操作类型", 400)
        
        if operation not in ['delete', 'reparse']:
            return error_response("不支持的操作类型", 400)
        
        # 验证所有简历都属于当前用户
        resumes = Resume.query.filter(
            Resume.id.in_(resume_ids),
            Resume.user_id == user_id
        ).all()
        
        if len(resumes) != len(resume_ids):
            return error_response("部分简历不存在或无权限", 400)
        
        results = []
        
        if operation == 'delete':
            for resume in resumes:
                try:
                    # 删除文件
                    if os.path.exists(resume.file_path):
                        os.remove(resume.file_path)
                    
                    # 删除数据库记录
                    db.session.delete(resume)
                    results.append({'id': resume.id, 'success': True})
                except Exception as e:
                    results.append({'id': resume.id, 'success': False, 'error': str(e)})
        
        elif operation == 'reparse':
            from app.services.resume_parser import ResumeParser
            parser = ResumeParser()
            
            for resume in resumes:
                try:
                    if not os.path.exists(resume.file_path):
                        results.append({'id': resume.id, 'success': False, 'error': '文件不存在'})
                        continue
                    
                    resume.status = ResumeStatus.PROCESSING
                    result = parser.parse_resume(resume.file_path, resume.file_type)
                    
                    if result['success']:
                        resume.status = ResumeStatus.PROCESSED
                        resume.raw_text = result['raw_text']
                        resume.parsed_content = result['parsed_data']
                        resume.processed_at = datetime.utcnow()
                        
                        parsed_data = result['parsed_data']
                        resume.name = parsed_data.get('name')
                        resume.email = parsed_data.get('email')
                        resume.phone = parsed_data.get('phone')
                        resume.skills = parsed_data.get('skills', [])
                        resume.experience = parsed_data.get('experience', [])
                        resume.education = parsed_data.get('education', [])
                        
                        results.append({'id': resume.id, 'success': True})
                    else:
                        resume.status = ResumeStatus.FAILED
                        resume.error_message = result['error']
                        results.append({'id': resume.id, 'success': False, 'error': result['error']})
                        
                except Exception as e:
                    results.append({'id': resume.id, 'success': False, 'error': str(e)})
        
        db.session.commit()
        
        return success_response({
            'operation': operation,
            'results': results,
            'summary': {
                'total': len(resume_ids),
                'success': len([r for r in results if r['success']]),
                'failed': len([r for r in results if not r['success']])
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"批量操作失败: {str(e)}")
        return error_response("批量操作失败", 500)

@resumes_bp.route('/export', methods=['POST'])
@jwt_required()
def export_resumes():
    """导出简历数据"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json() or {}
        
        export_format = data.get('format', 'json')  # json, csv
        resume_ids = data.get('resume_ids', [])
        
        if export_format not in ['json', 'csv']:
            return error_response("不支持的导出格式", 400)
        
        # 获取简历数据
        query = Resume.query.filter_by(user_id=user_id)
        if resume_ids:
            query = query.filter(Resume.id.in_(resume_ids))
        
        resumes = query.all()
        
        if export_format == 'json':
            export_data = {
                'export_date': datetime.utcnow().isoformat(),
                'total_resumes': len(resumes),
                'resumes': [resume.to_dict() for resume in resumes]
            }
            
            from flask import jsonify
            response = jsonify(export_data)
            response.headers['Content-Disposition'] = 'attachment; filename=resumes_export.json'
            return response
        
        elif export_format == 'csv':
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # CSV头部
            writer.writerow([
                'ID', '姓名', '邮箱', '电话', '文件名', '状态', '上传时间',
                '技能数量', '工作经历数量', '教育背景数量'
            ])
            
            # 写入数据
            for resume in resumes:
                writer.writerow([
                    resume.id,
                    resume.name or '',
                    resume.email or '',
                    resume.phone or '',
                    resume.original_filename,
                    resume.status.value,
                    resume.uploaded_at.strftime('%Y-%m-%d %H:%M:%S') if resume.uploaded_at else '',
                    len(resume.skills) if resume.skills else 0,
                    len(resume.experience) if resume.experience else 0,
                    len(resume.education) if resume.education else 0
                ])
            
            from flask import Response
            output.seek(0)
            return Response(
                output.getvalue(),
                mimetype='text/csv',
                headers={'Content-Disposition': 'attachment; filename=resumes_export.csv'}
            )
        
    except Exception as e:
        current_app.logger.error(f"导出简历失败: {str(e)}")
        return error_response("导出简历失败", 500) 