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
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc', 'txt'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def analyze_resume_content(resume):
    """
    基于简历实际内容进行分析
    """
    analysis_result = {
        'score': 0,
        'match_score': 0,
        'overall_score': 0,
        'suggestions': [],
        'strengths': [],
        'areas_for_improvement': []
    }
    
    score = 0
    max_score = 100
    
    # 1. Basic information completeness analysis (25 points)
    basic_info_score = 0
    if resume.name and resume.name.strip():
        basic_info_score += 8
        analysis_result['strengths'].append('Contains name information')
    else:
        analysis_result['areas_for_improvement'].append('Missing name information')
        analysis_result['suggestions'].append('Recommend adding complete name information')
    
    if resume.email and resume.email.strip():
        basic_info_score += 8
        analysis_result['strengths'].append('Contains email contact information')
    else:
        analysis_result['areas_for_improvement'].append('Missing email information')
        analysis_result['suggestions'].append('Recommend adding a valid email address')
    
    if resume.phone and resume.phone.strip():
        basic_info_score += 9
        analysis_result['strengths'].append('Contains phone contact information')
    else:
        analysis_result['areas_for_improvement'].append('Missing phone information')
        analysis_result['suggestions'].append('Recommend adding phone number')
    
    score += basic_info_score
    
    # 2. Skills information analysis (25 points)
    skills_score = 0
    skill_count = len(resume.skills) if resume.skills else 0
    
    if skill_count >= 10:
        skills_score = 25
        analysis_result['strengths'].append(f'Rich skills, contains {skill_count} skills')
    elif skill_count >= 6:
        skills_score = 20
        analysis_result['strengths'].append(f'Comprehensive skills, contains {skill_count} skills')
    elif skill_count >= 3:
        skills_score = 15
        analysis_result['strengths'].append(f'Contains basic skills, total {skill_count} items')
        analysis_result['suggestions'].append('Recommend adding more relevant skills')
    elif skill_count >= 1:
        skills_score = 10
        analysis_result['areas_for_improvement'].append('Limited skill information')
        analysis_result['suggestions'].append('Recommend adding more professional skills')
    else:
        analysis_result['areas_for_improvement'].append('Missing skill information')
        analysis_result['suggestions'].append('Recommend adding professional skills and tool usage experience')
    
    score += skills_score
    
    # 3. Work experience analysis (25 points)
    experience_score = 0
    exp_count = len(resume.experience) if resume.experience else 0
    
    if exp_count >= 3:
        experience_score = 25
        analysis_result['strengths'].append(f'Rich work experience, contains {exp_count} experiences')
    elif exp_count >= 2:
        experience_score = 20
        analysis_result['strengths'].append(f'Has relevant work experience, contains {exp_count} experiences')
    elif exp_count >= 1:
        experience_score = 15
        analysis_result['strengths'].append('Has work experience')
        analysis_result['suggestions'].append('Recommend detailing job responsibilities and achievements')
    else:
        analysis_result['areas_for_improvement'].append('Missing work experience information')
        analysis_result['suggestions'].append('Recommend adding internship or work experience')
    
    score += experience_score
    
    # 4. Educational background analysis (15 points)
    education_score = 0
    if resume.education and len(resume.education) > 0:
        education_score = 15
        analysis_result['strengths'].append('Contains educational background information')
    else:
        analysis_result['areas_for_improvement'].append('Missing educational background information')
        analysis_result['suggestions'].append('Recommend adding education and major information')
    
    score += education_score
    
    # 5. Project experience analysis (10 points)
    project_score = 0
    project_count = len(resume.projects) if resume.projects else 0
    
    if project_count >= 3:
        project_score = 10
        analysis_result['strengths'].append(f'Rich project experience, contains {project_count} projects')
    elif project_count >= 1:
        project_score = 8
        analysis_result['strengths'].append(f'Has project experience, contains {project_count} projects')
    else:
        analysis_result['areas_for_improvement'].append('Missing project experience')
        analysis_result['suggestions'].append('Recommend adding relevant project experience and technical practice')
    
    score += project_score
    
    # Calculate final score
    final_score = basic_info_score + skills_score + experience_score + education_score + project_score
    analysis_result['score'] = final_score
    analysis_result['match_score'] = final_score
    analysis_result['overall_score'] = final_score
    
    # Give overall evaluation based on score
    if final_score >= 80:
        analysis_result['strengths'].append('Overall resume quality is excellent')
    elif final_score >= 60:
        analysis_result['strengths'].append('Overall resume quality is good')
        analysis_result['suggestions'].append('Continue to improve detailed information')
    elif final_score >= 40:
        analysis_result['suggestions'].append('Recommend further improving resume content')
    else:
        analysis_result['suggestions'].append('Resume needs significant improvement, recommend adding key information')
    
    return analysis_result

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
        user_id = int(get_jwt_identity())
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
        current_app.logger.error(f"Failed to get resume list: {str(e)}")
        return error_response("Failed to get resume list", 500)

@resumes_bp.route('', methods=['POST'])
@jwt_required()
def upload_resume():
    """上传简历文件"""
    try:
        user_id = int(get_jwt_identity())
        
        # 检查请求中是否有文件
        if 'file' not in request.files:
            return error_response("Please select a file to upload", 400)
        
        file = request.files['file']
        
        # 检查文件是否为空
        if file.filename == '':
            return error_response("Please select a file to upload", 400)
        
        # 检查文件格式
        if not allowed_file(file.filename):
            return error_response(
                f"Unsupported file format, please upload {', '.join(ALLOWED_EXTENSIONS)} format files", 
                400
            )
        
        # 检查文件大小
        file.seek(0, 2)  # 移到文件末尾
        file_size = file.tell()
        file.seek(0)  # 重置到文件开头
        
        if file_size > MAX_FILE_SIZE:
            return error_response(f"File too large, maximum supported {MAX_FILE_SIZE // 1024 // 1024}MB", 400)
        
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
                # 添加项目经验支持
                resume.projects = parsed_data.get('projects', [])
                
            else:
                resume.status = ResumeStatus.FAILED
                resume.error_message = result['error']
            
            db.session.commit()
            
        except Exception as parse_error:
            current_app.logger.error(f"Resume parsing failed: {str(parse_error)}")
            resume.status = ResumeStatus.FAILED
            resume.error_message = str(parse_error)
            db.session.commit()
        
        return success_response({
            'resume': resume.to_dict(),
            'message': 'Resume uploaded successfully, parsing in progress...'
        }, 201)
        
    except RequestEntityTooLarge:
        return error_response(f"File too large, maximum supported {MAX_FILE_SIZE // 1024 // 1024}MB", 413)
    except Exception as e:
        current_app.logger.error(f"Resume upload failed: {str(e)}")
        return error_response("Resume upload failed", 500)

@resumes_bp.route('/<int:resume_id>', methods=['GET'])
@jwt_required()
def get_resume(resume_id):
    """获取单个简历详情"""
    try:
        user_id = get_jwt_identity()
        
        resume = Resume.query.filter_by(id=resume_id, user_id=user_id).first()
        if not resume:
            return error_response("Resume does not exist", 404)
        
        return success_response({'resume': resume.to_dict()})
        
    except Exception as e:
        current_app.logger.error(f"Failed to get resume details: {str(e)}")
        return error_response("Failed to get resume details", 500)

@resumes_bp.route('/<int:resume_id>', methods=['DELETE'])
@jwt_required()
def delete_resume(resume_id):
    """删除简历"""
    try:
        user_id = get_jwt_identity()
        
        resume = Resume.query.filter_by(id=resume_id, user_id=user_id).first()
        if not resume:
            return error_response("Resume does not exist", 404)
        
        # 删除文件
        try:
            if os.path.exists(resume.file_path):
                os.remove(resume.file_path)
        except Exception as e:
            current_app.logger.warning(f"Failed to delete file: {str(e)}")
        
        # 删除数据库记录
        db.session.delete(resume)
        db.session.commit()
        
        return success_response({'message': 'Resume deleted successfully'})
        
    except Exception as e:
        current_app.logger.error(f"Failed to delete resume: {str(e)}")
        return error_response("Failed to delete resume", 500)

@resumes_bp.route('/<int:resume_id>/reparse', methods=['POST'])
@jwt_required()
def reparse_resume(resume_id):
    """重新解析简历"""
    try:
        user_id = get_jwt_identity()
        
        resume = Resume.query.filter_by(id=resume_id, user_id=user_id).first()
        if not resume:
            return error_response("Resume does not exist", 404)
        
        if not os.path.exists(resume.file_path):
            return error_response("Resume file does not exist", 404)
        
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
            # 添加项目经验支持
            resume.projects = parsed_data.get('projects', [])
            
        else:
            resume.status = ResumeStatus.FAILED
            resume.error_message = result['error']
        
        db.session.commit()
        
        return success_response({
            'resume': resume.to_dict(),
            'message': 'Reparse completed'
        })
        
    except Exception as e:
        current_app.logger.error(f"Failed to reparse resume: {str(e)}")
        return error_response("Failed to reparse resume", 500)

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
        current_app.logger.error(f"Failed to get resume stats: {str(e)}")
        return error_response("Failed to get resume stats", 500)

@resumes_bp.route('/<int:resume_id>/download', methods=['GET'])
@jwt_required()
def download_resume(resume_id):
    """下载简历文件"""
    try:
        user_id = int(get_jwt_identity())
        
        resume = Resume.query.filter_by(id=resume_id, user_id=user_id).first()
        if not resume:
            return error_response("Resume does not exist", 404)
        
        if not os.path.exists(resume.file_path):
            return error_response("Resume file does not exist", 404)
        
        return send_file(
            resume.file_path,
            as_attachment=True,
            download_name=resume.original_filename,
            mimetype='application/octet-stream'
        )
        
    except Exception as e:
        current_app.logger.error(f"Failed to download resume: {str(e)}")
        return error_response("Failed to download resume", 500)

@resumes_bp.route('/<int:resume_id>/preview', methods=['GET'])
@jwt_required()
def preview_resume(resume_id):
    """预览简历内容"""
    try:
        user_id = int(get_jwt_identity())
        
        resume = Resume.query.filter_by(id=resume_id, user_id=user_id).first()
        if not resume:
            return error_response("Resume does not exist", 404)
        
        if resume.status != ResumeStatus.PROCESSED:
            return error_response("Resume not yet processed, cannot preview", 400)
        
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
        current_app.logger.error(f"Failed to preview resume: {str(e)}")
        return error_response("Failed to preview resume", 500)

@resumes_bp.route('/<int:resume_id>/analyze', methods=['POST'])
@jwt_required()
def analyze_resume(resume_id):
    """智能分析简历"""
    try:
        user_id = int(get_jwt_identity())
        
        resume = Resume.query.filter_by(id=resume_id, user_id=user_id).first()
        if not resume:
            return error_response("Resume does not exist", 404)
        
        # 如果简历状态不是已处理，尝试重新处理
        if resume.status != ResumeStatus.PROCESSED:
            # 如果简历还在处理中，等待一下或重新处理
            if resume.status == ResumeStatus.PROCESSING:
                return error_response("Resume is being processed, please try again later", 202)
            elif resume.status in [ResumeStatus.UPLOADED, ResumeStatus.FAILED]:
                # 尝试重新解析简历
                try:
                    from app.services.resume_parser import ResumeParser
                    parser = ResumeParser()
                    
                    resume.status = ResumeStatus.PROCESSING
                    db.session.commit()
                    
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
                        # 添加项目经验支持
                        resume.projects = parsed_data.get('projects', [])
                        resume.error_message = None
                        
                        db.session.commit()
                    else:
                        resume.status = ResumeStatus.FAILED
                        resume.error_message = result['error']
                        db.session.commit()
                        return error_response(f"Resume parsing failed: {result['error']}", 400)
                        
                except Exception as e:
                    resume.status = ResumeStatus.FAILED
                    resume.error_message = str(e)
                    db.session.commit()
                    return error_response(f"Failed to reparse resume: {str(e)}", 500)
        
        # 进行简历分析
        try:
            # 基于简历实际内容进行分析
            analysis_result = analyze_resume_content(resume)
            
            return success_response({
                'resume_id': resume_id,
                'analysis': analysis_result,
                'data': analysis_result  # 为了兼容前端
            })
            
        except Exception as e:
            current_app.logger.error(f"Failed to analyze resume: {str(e)}")
            return error_response(f"Failed to analyze resume: {str(e)}", 500)
        
    except Exception as e:
        current_app.logger.error(f"Analysis resume API failed: {str(e)}")
        return error_response("Analysis resume failed", 500)

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
        current_app.logger.error(f"Failed to search resumes: {str(e)}")
        return error_response("Failed to search resumes", 500)

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
            return error_response("Please provide a list of resume IDs and operation type", 400)
        
        if operation not in ['delete', 'reparse']:
            return error_response("Unsupported operation type", 400)
        
        # 验证所有简历都属于当前用户
        resumes = Resume.query.filter(
            Resume.id.in_(resume_ids),
            Resume.user_id == user_id
        ).all()
        
        if len(resumes) != len(resume_ids):
            return error_response("Some resumes do not exist or do not have permission", 400)
        
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
                        results.append({'id': resume.id, 'success': False, 'error': 'File does not exist'})
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
                        # 添加项目经验支持
                        resume.projects = parsed_data.get('projects', [])
                        
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
        current_app.logger.error(f"Batch operation failed: {str(e)}")
        return error_response("Batch operation failed", 500)

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
            return error_response("Unsupported export format", 400)
        
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
                'ID', 'Name', 'Email', 'Phone', 'Filename', 'Status', 'Upload Time',
                'Skill Count', 'Experience Count', 'Education Count'
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
        current_app.logger.error(f"Failed to export resumes: {str(e)}")
        return error_response("Failed to export resumes", 500) 