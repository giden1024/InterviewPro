from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields, ValidationError as MarshmallowValidationError
from sqlalchemy import or_, and_

from app.extensions import db
from app.models.job import Job, JobType, JobStatus
from app.models.resume import Resume
from app.services.job_parser import JobParser
from app.services.ocr_service import OCRService
from app.utils.exceptions import APIError, ValidationError, NotFoundError
from app.utils.response import success_response, error_response
import os
import time
from werkzeug.utils import secure_filename

jobs_bp = Blueprint('jobs', __name__)

# 验证模式
class CreateJobSchema(Schema):
    title = fields.Str(required=True, validate=lambda x: len(x.strip()) > 0)
    company = fields.Str(allow_none=True)
    description = fields.Str(allow_none=True)
    resume_id = fields.Int(allow_none=True)  # 关联的简历ID
    requirements = fields.List(fields.Str(), allow_none=True)
    responsibilities = fields.List(fields.Str(), allow_none=True)
    salary_range = fields.Str(allow_none=True)
    location = fields.Str(allow_none=True)
    remote_allowed = fields.Bool(allow_none=True)
    job_type = fields.Str(allow_none=True, validate=lambda x: x is None or x in ['full-time', 'part-time', 'contract', 'internship', 'freelance'])
    source_url = fields.Str(allow_none=True)
    skills_required = fields.List(fields.Str(), allow_none=True)
    experience_level = fields.Str(allow_none=True)

class UpdateJobSchema(Schema):
    title = fields.Str()
    company = fields.Str()
    description = fields.Str()
    requirements = fields.List(fields.Str())
    responsibilities = fields.List(fields.Str())
    salary_range = fields.Str()
    location = fields.Str()
    remote_allowed = fields.Bool()
    job_type = fields.Str(validate=lambda x: x in ['full-time', 'part-time', 'contract', 'internship', 'freelance'])
    status = fields.Str(validate=lambda x: x in ['active', 'inactive', 'archived'])
    skills_required = fields.List(fields.Str())
    experience_level = fields.Str()

class AnalyzeUrlSchema(Schema):
    url = fields.Url(required=True)

class ParseTextSchema(Schema):
    job_text = fields.Str(required=True)
    title = fields.Str(allow_none=True)
    company = fields.Str(allow_none=True)

@jobs_bp.route('', methods=['POST'])
@jwt_required()
def create_job():
    """创建职位"""
    try:
        user_id = int(get_jwt_identity())
        
        # 数据验证
        schema = CreateJobSchema()
        data = schema.load(request.get_json() or {})
        
        # 验证关联的简历是否存在
        resume_id = data.get('resume_id')
        if resume_id:
            resume = Resume.query.filter_by(id=resume_id, user_id=user_id).first()
            if not resume:
                return error_response("Associated resume does not exist", 404)
        
        # 创建职位
        job = Job(
            user_id=user_id,
            resume_id=resume_id,
            title=data['title'],
            company=data.get('company', ''),
            description=data.get('description', ''),
            requirements=data.get('requirements', []),
            responsibilities=data.get('responsibilities', []),
            salary_range=data.get('salary_range', ''),
            location=data.get('location', ''),
            remote_allowed=data.get('remote_allowed', False),
            job_type=JobType(data.get('job_type', 'full-time')),
            source_url=data.get('source_url', ''),
            skills_required=data.get('skills_required', []),
            experience_level=data.get('experience_level', ''),
            source_type='manual'
        )
        
        db.session.add(job)
        db.session.commit()
        
        return success_response({
            'job': job.to_dict()
        }, "Job created successfully", 201)
        
    except MarshmallowValidationError as e:
        return error_response("Data validation failed", 422, details=e.messages)
    except Exception as e:
        current_app.logger.error(f"Failed to create job: {str(e)}")
        return error_response("Failed to create job", 500)

@jobs_bp.route('', methods=['GET'])
@jwt_required()
def get_jobs():
    """获取职位列表"""
    try:
        user_id = int(get_jwt_identity())
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        status = request.args.get('status', 'active')
        search = request.args.get('search', '')
        
        # 构建查询
        query = Job.query.filter_by(user_id=user_id)
        
        # 状态过滤
        if status != 'all':
            query = query.filter(Job.status == JobStatus(status))
        
        # 搜索过滤
        if search:
            search_filter = or_(
                Job.title.ilike(f'%{search}%'),
                Job.company.ilike(f'%{search}%'),
                Job.description.ilike(f'%{search}%')
            )
            query = query.filter(search_filter)
        
        # 分页
        jobs_paginated = query.order_by(Job.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return success_response({
            'jobs': [job.to_dict() for job in jobs_paginated.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': jobs_paginated.total,
                'pages': jobs_paginated.pages,
                'has_next': jobs_paginated.has_next,
                'has_prev': jobs_paginated.has_prev
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Failed to get job list: {str(e)}")
        return error_response("Failed to get job list", 500)

@jobs_bp.route('/<int:job_id>', methods=['GET'])
@jwt_required()
def get_job(job_id):
    """获取职位详情"""
    try:
        user_id = int(get_jwt_identity())
        
        job = Job.query.filter_by(id=job_id, user_id=user_id).first()
        if not job:
            return error_response("Job does not exist", 404)
        
        job_data = job.to_dict()
        
        # 如果有关联的简历，添加简历信息
        if job.resume_id and job.resume:
            job_data['resume'] = job.resume.to_dict()
        
        return success_response({
            'job': job_data
        })
        
    except Exception as e:
        current_app.logger.error(f"Failed to get job details: {str(e)}")
        return error_response("Failed to get job details", 500)

@jobs_bp.route('/<int:job_id>', methods=['PUT'])
@jwt_required()
def update_job(job_id):
    """更新职位"""
    try:
        user_id = int(get_jwt_identity())
        
        job = Job.query.filter_by(id=job_id, user_id=user_id).first()
        if not job:
            return error_response("Job does not exist", 404)
        
        # 数据验证
        schema = UpdateJobSchema()
        data = schema.load(request.get_json() or {})
        
        # 更新字段
        for field, value in data.items():
            if field == 'job_type' and value:
                setattr(job, field, JobType(value))
            elif field == 'status' and value:
                setattr(job, field, JobStatus(value))
            else:
                setattr(job, field, value)
        
        db.session.commit()
        
        return success_response({
            'job': job.to_dict()
        }, "Job updated successfully")
        
    except MarshmallowValidationError as e:
        return error_response("Data validation failed", 422, details=e.messages)
    except Exception as e:
        current_app.logger.error(f"Failed to update job: {str(e)}")
        return error_response("Failed to update job", 500)

@jobs_bp.route('/<int:job_id>', methods=['DELETE'])
@jwt_required()
def delete_job(job_id):
    """删除职位"""
    try:
        user_id = int(get_jwt_identity())
        
        job = Job.query.filter_by(id=job_id, user_id=user_id).first()
        if not job:
            return error_response("Job does not exist", 404)
        
        db.session.delete(job)
        db.session.commit()
        
        return success_response(message="Job deleted successfully")
        
    except Exception as e:
        current_app.logger.error(f"Failed to delete job: {str(e)}")
        return error_response("Failed to delete job", 500)

@jobs_bp.route('/analyze-url', methods=['POST'])
@jwt_required()
def analyze_job_url():
    """分析职位URL"""
    try:
        user_id = int(get_jwt_identity())
        
        # 数据验证
        schema = AnalyzeUrlSchema()
        data = schema.load(request.get_json() or {})
        
        # 解析URL
        parser = JobParser()
        result = parser.parse_job_url(data['url'])
        
        if not result['success']:
            return error_response(f"URL parsing failed: {result['error']}", 400)
        
        job_data = result['data']
        
        # 创建职位记录
        job = Job(
            user_id=user_id,
            title=job_data['title'] or '未指定职位',
            company=job_data['company'],
            description=job_data['description'],
            requirements=job_data['requirements'],
            responsibilities=job_data.get('responsibilities', []),
            location=job_data['location'],
            salary_range=job_data['salary_range'],
            job_type=JobType(job_data['job_type']),
            source_url=data['url'],
            source_type='url',
            skills_required=job_data['skills_required'],
            experience_level=job_data['experience_level'],
            parsed_data=job_data['parsed_data']
        )
        
        db.session.add(job)
        db.session.commit()
        
        return success_response({
            'job': job.to_dict(),
            'parsing_result': result
        }, "URL分析完成，职位已创建", 201)
        
    except MarshmallowValidationError as e:
        return error_response("Data validation failed", 422, details=e.messages)
    except Exception as e:
        current_app.logger.error(f"Failed to analyze URL: {str(e)}")
        return error_response("Failed to analyze URL", 500)

@jobs_bp.route('/parse-text', methods=['POST'])
@jwt_required()
def parse_job_text():
    """解析职位描述文本"""
    try:
        user_id = int(get_jwt_identity())
        
        # 数据验证
        schema = ParseTextSchema()
        data = schema.load(request.get_json() or {})
        
        # 解析文本
        parser = JobParser()
        result = parser.parse_job_text(
            data['job_text'],
            data.get('title', ''),
            data.get('company', '')
        )
        
        if not result['success']:
            return error_response(f"Text parsing failed: {result['error']}", 400)
        
        job_data = result['data']
        
        # 创建职位记录
        job = Job(
            user_id=user_id,
            title=job_data['title'] or '未指定职位',
            company=job_data['company'],
            description=job_data['description'],
            requirements=job_data['requirements'],
            responsibilities=job_data['responsibilities'],
            location=job_data['location'],
            salary_range=job_data['salary_range'],
            job_type=JobType(job_data['job_type']),
            source_type='text',
            skills_required=job_data['skills_required'],
            experience_level=job_data['experience_level'],
            parsed_data=job_data['parsed_data']
        )
        
        db.session.add(job)
        db.session.commit()
        
        return success_response({
            'job': job.to_dict(),
            'parsing_result': result
        }, "文本解析完成，职位已创建", 201)
        
    except MarshmallowValidationError as e:
        return error_response("Data validation failed", 422, details=e.messages)
    except Exception as e:
        current_app.logger.error(f"Failed to parse text: {str(e)}")
        return error_response("Failed to parse text", 500)


@jobs_bp.route('/ocr-extract', methods=['POST'])
@jwt_required()
def extract_text_from_image():
    """从上传的图片中提取文字"""
    try:
        user_id = int(get_jwt_identity())
        
        # 检查是否有上传的文件
        if 'image' not in request.files:
            return error_response("Please upload an image file", 400)
        
        file = request.files['image']
        if file.filename == '':
            return error_response("Please select an image to upload", 400)
        
        # 验证文件类型
        if not _allowed_image_file(file.filename):
            return error_response("Unsupported image format. Supported formats: jpg, jpeg, png, bmp, tiff, webp", 400)
        
        # 确保上传目录存在
        upload_dir = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        
        # 保存上传的文件
        filename = secure_filename(file.filename)
        timestamp = str(int(time.time()))
        safe_filename = f"ocr_{user_id}_{timestamp}_{filename}"
        file_path = os.path.join(upload_dir, safe_filename)
        
        file.save(file_path)
        
        try:
            # 使用OCR服务提取文字
            ocr_service = OCRService()
            result = ocr_service.extract_text_from_image(file_path)
            
            if not result['success']:
                return error_response(result['error'], 400)
            
            return success_response({
                'text': result['text'],
                'original_text': result.get('original_text', ''),
                'language': result.get('language', 'unknown'),
                'message': 'OCR text recognition successful'
            })
            
        finally:
            # 清理临时文件
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                current_app.logger.warning(f"Failed to clean up temporary file: {e}")
                
    except Exception as e:
        current_app.logger.error(f"OCR text recognition failed: {str(e)}")
        return error_response("Image text recognition failed", 500)


def _allowed_image_file(filename):
    """检查是否为允许的图片文件格式"""
    allowed_extensions = {'png', 'jpg', 'jpeg', 'tiff', 'bmp', 'webp'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


@jobs_bp.route('/templates', methods=['GET'])
@jwt_required()
def get_job_templates():
    """获取职位模板"""
    try:
        templates = [
            {
                'id': 1,
                'title': 'Product Manager',
                'category': 'Product',
                'description': 'Lead product development and strategy',
                'skills': ['Product Strategy', 'User Research', 'Data Analysis', 'Agile'],
                'experience_level': 'mid'
            },
            {
                'id': 2,
                'title': 'Software Engineer',
                'category': 'Engineering',
                'description': 'Develop and maintain software applications',
                'skills': ['Python', 'JavaScript', 'React', 'SQL'],
                'experience_level': 'entry'
            },
            {
                'id': 3,
                'title': 'Data Scientist',
                'category': 'Data',
                'description': 'Analyze data and build machine learning models',
                'skills': ['Python', 'Machine Learning', 'Statistics', 'SQL'],
                'experience_level': 'mid'
            },
            {
                'id': 4,
                'title': 'Marketing Manager',
                'category': 'Marketing',
                'description': 'Plan and execute marketing campaigns',
                'skills': ['Digital Marketing', 'Analytics', 'Content Strategy', 'SEO'],
                'experience_level': 'mid'
            },
            {
                'id': 5,
                'title': 'UX Designer',
                'category': 'Design',
                'description': 'Design user experiences and interfaces',
                'skills': ['Figma', 'User Research', 'Prototyping', 'Design Systems'],
                'experience_level': 'entry'
            }
        ]
        
        return success_response({
            'templates': templates
        })
        
    except Exception as e:
        current_app.logger.error(f"Failed to get job templates: {str(e)}")
        return error_response("Failed to get job templates", 500)

@jobs_bp.route('/<int:job_id>/match-resume', methods=['POST'])
@jwt_required()
def match_job_with_resume(job_id):
    """职位与简历匹配"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json() or {}
        resume_id = data.get('resume_id')
        
        # 获取职位
        job = Job.query.filter_by(id=job_id, user_id=user_id).first()
        if not job:
            return error_response("Job does not exist", 404)
        
        # 获取简历
        if resume_id:
            resume = Resume.query.filter_by(id=resume_id, user_id=user_id).first()
            if not resume:
                return error_response("Resume does not exist", 404)
        else:
            # 使用用户最新的简历
            resume = Resume.query.filter_by(user_id=user_id).order_by(Resume.created_at.desc()).first()
            if not resume:
                return error_response("Resume not found", 404)
        
        # 计算匹配度
        match_result = _calculate_job_resume_match(job, resume)
        
        # 更新职位的匹配信息
        job.match_score = match_result['score']
        job.match_details = match_result['details']
        db.session.commit()
        
        return success_response({
            'job': job.to_dict(),
            'resume': resume.to_dict(),
            'match_result': match_result
        }, "Matching analysis completed")
        
    except Exception as e:
        current_app.logger.error(f"Failed to match job with resume: {str(e)}")
        return error_response("Matching analysis failed", 500)

@jobs_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_job_stats():
    """获取职位统计"""
    try:
        user_id = int(get_jwt_identity())
        
        # 基本统计
        total_jobs = Job.query.filter_by(user_id=user_id).count()
        active_jobs = Job.query.filter_by(user_id=user_id, status=JobStatus.ACTIVE).count()
        
        # 按类型统计
        job_types = db.session.query(
            Job.job_type, db.func.count(Job.id)
        ).filter_by(user_id=user_id).group_by(Job.job_type).all()
        
        # 按经验级别统计
        experience_levels = db.session.query(
            Job.experience_level, db.func.count(Job.id)
        ).filter_by(user_id=user_id).group_by(Job.experience_level).all()
        
        return success_response({
            'total_jobs': total_jobs,
            'active_jobs': active_jobs,
            'job_types': [{'type': jt[0].value if jt[0] else 'unknown', 'count': jt[1]} for jt in job_types],
            'experience_levels': [{'level': el[0] or 'unknown', 'count': el[1]} for el in experience_levels]
        })
        
    except Exception as e:
        current_app.logger.error(f"Failed to get job statistics: {str(e)}")
        return error_response("Failed to get statistics", 500)

def _calculate_job_resume_match(job: Job, resume: Resume) -> dict:
    """计算职位与简历的匹配度"""
    try:
        score = 0.0
        details = {
            'skill_matches': [],
            'skill_gaps': [],
            'experience_match': False,
            'recommendations': []
        }
        
        # 技能匹配 (60%权重)
        job_skills = set([skill.lower() for skill in (job.skills_required or [])])
        resume_skills = set([skill.lower() for skill in (resume.skills or [])])
        
        if job_skills:
            matched_skills = job_skills.intersection(resume_skills)
            skill_match_ratio = len(matched_skills) / len(job_skills)
            score += skill_match_ratio * 0.6
            
            details['skill_matches'] = list(matched_skills)
            details['skill_gaps'] = list(job_skills - resume_skills)
        
        # 经验匹配 (30%权重)
        if job.experience_level and resume.experience:
            # 简化的经验匹配逻辑
            resume_years = len(resume.experience) if isinstance(resume.experience, list) else 0
            
            experience_match = False
            if job.experience_level == 'entry' and resume_years >= 0:
                experience_match = True
            elif job.experience_level == 'mid' and resume_years >= 2:
                experience_match = True
            elif job.experience_level == 'senior' and resume_years >= 5:
                experience_match = True
            
            if experience_match:
                score += 0.3
                details['experience_match'] = True
        
        # 关键词匹配 (10%权重)
        if job.description and resume.raw_text:
            job_words = set(job.description.lower().split())
            resume_words = set(resume.raw_text.lower().split())
            common_words = job_words.intersection(resume_words)
            
            if job_words:
                keyword_ratio = len(common_words) / len(job_words)
                score += keyword_ratio * 0.1
        
        # 生成建议
        if details['skill_gaps']:
            details['recommendations'].append(f"Recommend learning the following skills: {', '.join(list(details['skill_gaps'])[:3])}")
        
        if not details['experience_match']:
            details['recommendations'].append("Consider gaining more relevant work experience")
        
        return {
            'score': round(score * 100, 2),  # 转换为百分比
            'details': details
        }
        
    except Exception as e:
        current_app.logger.error(f"Failed to calculate match: {str(e)}")
        return {
            'score': 0.0,
            'details': {'error': 'Failed to calculate match'}
        } 