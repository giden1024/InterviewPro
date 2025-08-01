import json
import hashlib
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from flask import current_app
from app.extensions import get_redis_client
from app.models.resume import Resume

logger = logging.getLogger(__name__)

class QuestionCacheService:
    """改进的问题缓存服务"""
    
    def __init__(self):
        self.cache_ttl = 3600  # 1小时缓存过期时间
        self.cache_prefix = "questions:cache"
    
    def _generate_resume_hash(self, resume: Resume) -> str:
        """生成简历内容哈希"""
        try:
            # 基于简历的关键信息生成哈希
            resume_content = {
                'skills': sorted(resume.skills or []),
                'experience_count': len(resume.experience or []),
                'education_count': len(resume.education or []),
                'summary_hash': hashlib.md5((resume.raw_text or "").encode()).hexdigest()[:16]
            }
            
            content_string = json.dumps(resume_content, sort_keys=True)
            return hashlib.md5(content_string.encode()).hexdigest()
        except Exception as e:
            logger.error(f"生成简历哈希失败: {e}")
            # 如果生成哈希失败，使用简历ID作为备选
            return f"resume_{resume.id}"
    
    def _generate_cache_key(self, user_id: int, resume: Resume, 
                           interview_type: str, total_questions: int,
                           difficulty_distribution: Dict[str, int], 
                           type_distribution: Dict[str, int]) -> str:
        """生成改进的缓存键"""
        
        # 生成简历内容哈希
        resume_hash = self._generate_resume_hash(resume)
        
        cache_data = {
            'user_id': user_id,                    # ✅ 用户ID
            'resume_hash': resume_hash,            # ✅ 简历内容哈希
            'interview_type': interview_type,      # ✅ 面试类型
            'total_questions': total_questions,    # ✅ 问题数量
            'difficulty_distribution': difficulty_distribution,
            'type_distribution': type_distribution
        }
        
        # 使用JSON字符串的哈希作为缓存键
        cache_string = json.dumps(cache_data, sort_keys=True)
        cache_hash = hashlib.md5(cache_string.encode()).hexdigest()
        
        return f"{self.cache_prefix}:{cache_hash}"
    
    def get_cached_questions(self, user_id: int, resume: Resume, 
                           interview_type: str, total_questions: int,
                           difficulty_distribution: Dict[str, int], 
                           type_distribution: Dict[str, int]) -> Optional[List[Dict[str, Any]]]:
        """从缓存获取问题"""
        try:
            redis_client = get_redis_client()
            if redis_client is None:
                logger.warning("Redis client not available, skipping cache")
                return None
            
            cache_key = self._generate_cache_key(
                user_id, resume, interview_type, total_questions,
                difficulty_distribution, type_distribution
            )
            
            cached_data = redis_client.get(cache_key)
            if cached_data:
                cache_info = json.loads(cached_data)
                questions = cache_info.get('questions', [])
                logger.info(f"✅ 用户{user_id}从缓存获取到 {len(questions)} 个问题")
                return questions
            else:
                logger.info(f"❌ 用户{user_id}缓存未命中，需要重新生成")
                return None
                
        except Exception as e:
            logger.error(f"缓存读取失败: {e}")
            return None
    
    def cache_questions(self, user_id: int, resume: Resume, 
                       interview_type: str, total_questions: int,
                       difficulty_distribution: Dict[str, int], 
                       type_distribution: Dict[str, int], 
                       questions: List[Dict[str, Any]]) -> bool:
        """缓存问题"""
        try:
            redis_client = get_redis_client()
            if redis_client is None:
                logger.warning("Redis client not available, skipping cache")
                return False
            
            cache_key = self._generate_cache_key(
                user_id, resume, interview_type, total_questions,
                difficulty_distribution, type_distribution
            )
            
            # 将问题序列化为JSON并存储到Redis，包含用户ID信息
            cache_data = {
                'user_id': user_id,
                'questions': questions,
                'cached_at': datetime.now().isoformat()
            }
            cache_json = json.dumps(cache_data, ensure_ascii=False)
            redis_client.setex(cache_key, self.cache_ttl, cache_json)
            
            logger.info(f"✅ 用户{user_id}成功缓存 {len(questions)} 个问题")
            return True
            
        except Exception as e:
            logger.error(f"缓存存储失败: {e}")
            return False
    
    def clear_user_cache(self, user_id: int) -> bool:
        """清除用户的所有缓存"""
        try:
            redis_client = get_redis_client()
            if redis_client is None:
                return False
            
            pattern = f"{self.cache_prefix}:*"
            keys = redis_client.keys(pattern)
            cleared_count = 0
            
            for key in keys:
                cached_data = redis_client.get(key)
                if cached_data:
                    try:
                        cache_info = json.loads(cached_data)
                        if cache_info.get('user_id') == user_id:
                            redis_client.delete(key)
                            cleared_count += 1
                    except:
                        continue
            
            logger.info(f"✅ 清除了用户{user_id}的 {cleared_count} 个缓存项")
            return True
            
        except Exception as e:
            logger.error(f"清除用户缓存失败: {e}")
            return False
    
    def clear_cache(self, resume_id: Optional[int] = None) -> bool:
        """清除缓存"""
        try:
            redis_client = get_redis_client()
            if redis_client is None:
                return False
            
            if resume_id:
                # 清除特定简历的缓存
                pattern = f"{self.cache_prefix}:*"
                keys = redis_client.keys(pattern)
                cleared_count = 0
                
                for key in keys:
                    # 检查键是否包含指定的resume_id
                    # Note: This check is inefficient as it retrieves and parses each value.
                    # A better approach would be to include resume_id directly in the key for pattern matching.
                    # For now, assuming the current key generation logic.
                    if f"resume_id\":{resume_id}" in redis_client.get(key) or "resume_id\":{resume_id}" in redis_client.get(key):
                        redis_client.delete(key)
                        cleared_count += 1
                
                logger.info(f"✅ 清除了 {cleared_count} 个缓存项")
            else:
                # 清除所有问题缓存
                pattern = f"{self.cache_prefix}:*"
                keys = redis_client.keys(pattern)
                if keys:
                    redis_client.delete(*keys)
                    logger.info(f"✅ 清除了 {len(keys)} 个缓存项")
            
            return True
            
        except Exception as e:
            logger.error(f"清除缓存失败: {e}")
            return False
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        try:
            redis_client = get_redis_client()
            if redis_client is None:
                return {"error": "Redis client not available"}
            
            pattern = f"{self.cache_prefix}:*"
            keys = redis_client.keys(pattern)
            
            total_keys = len(keys)
            total_memory = 0
            
            for key in keys:
                memory_usage = redis_client.memory_usage(key)
                if memory_usage:
                    total_memory += memory_usage
            
            return {
                "total_cached_questions": total_keys,
                "total_memory_usage_bytes": total_memory,
                "total_memory_usage_mb": round(total_memory / 1024 / 1024, 2),
                "cache_ttl_seconds": self.cache_ttl
            }
            
        except Exception as e:
            logger.error(f"获取缓存统计失败: {e}")
            return {"error": str(e)} 