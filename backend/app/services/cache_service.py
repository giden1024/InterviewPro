import json
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from flask import current_app
from app.extensions import get_redis_client

class CacheService:
    """缓存服务类"""
    
    QUESTION_CACHE_PREFIX = "questions_cache"
    CACHE_EXPIRY_DAYS = 7
    
    @staticmethod
    def _get_cache_key(user_id: int, resume_id: int) -> str:
        """生成缓存键"""
        return f"{CacheService.QUESTION_CACHE_PREFIX}:{user_id}:{resume_id}"
    
    @staticmethod
    def _get_resume_version_key(resume_id: int) -> str:
        """生成简历版本键"""
        return f"resume_version:{resume_id}"
    
    @staticmethod
    def get_cached_questions(user_id: int, resume_id: int) -> Optional[List[Dict[Any, Any]]]:
        """获取缓存的问题"""
        redis_client = get_redis_client()
        if not redis_client:
            current_app.logger.info("Redis client not available, skipping cache")
            return None
        
        try:
            cache_key = CacheService._get_cache_key(user_id, resume_id)
            cached_data = redis_client.get(cache_key)
            
            if cached_data:
                data = json.loads(cached_data)
                current_app.logger.info(f"Cache hit for user {user_id}, resume {resume_id}")
                return data.get('questions')
            else:
                current_app.logger.info(f"Cache miss for user {user_id}, resume {resume_id}")
                return None
                
        except Exception as e:
            current_app.logger.error(f"Error getting cached questions: {e}")
            return None
    
    @staticmethod
    def set_cached_questions(user_id: int, resume_id: int, questions: List[Dict[Any, Any]], resume_updated_at: datetime = None):
        """设置缓存的问题"""
        redis_client = get_redis_client()
        if not redis_client:
            current_app.logger.info("Redis client not available, skipping cache")
            return
        
        try:
            cache_key = CacheService._get_cache_key(user_id, resume_id)
            version_key = CacheService._get_resume_version_key(resume_id)
            
            # 准备缓存数据
            cache_data = {
                'questions': questions,
                'cached_at': datetime.utcnow().isoformat(),
                'resume_updated_at': resume_updated_at.isoformat() if resume_updated_at else None
            }
            
            # 设置缓存，过期时间为7天
            expiry_seconds = CacheService.CACHE_EXPIRY_DAYS * 24 * 60 * 60
            redis_client.setex(cache_key, expiry_seconds, json.dumps(cache_data, default=str))
            
            # 记录简历版本，用于后续缓存失效
            if resume_updated_at:
                redis_client.setex(version_key, expiry_seconds, resume_updated_at.isoformat())
            
            current_app.logger.info(f"Cached questions for user {user_id}, resume {resume_id}")
            
        except Exception as e:
            current_app.logger.error(f"Error setting cached questions: {e}")
    
    @staticmethod
    def invalidate_resume_cache(resume_id: int):
        """清除特定简历的所有缓存"""
        redis_client = get_redis_client()
        if not redis_client:
            current_app.logger.info("Redis client not available, skipping cache invalidation")
            return
        
        try:
            # 查找所有相关的缓存键
            pattern = f"{CacheService.QUESTION_CACHE_PREFIX}:*:{resume_id}"
            keys = redis_client.keys(pattern)
            
            if keys:
                redis_client.delete(*keys)
                current_app.logger.info(f"Invalidated {len(keys)} cache entries for resume {resume_id}")
            
            # 删除简历版本键
            version_key = CacheService._get_resume_version_key(resume_id)
            redis_client.delete(version_key)
            
        except Exception as e:
            current_app.logger.error(f"Error invalidating resume cache: {e}")
    
    @staticmethod
    def is_resume_cache_valid(resume_id: int, current_updated_at: datetime) -> bool:
        """检查简历缓存是否仍然有效"""
        redis_client = get_redis_client()
        if not redis_client:
            return False
        
        try:
            version_key = CacheService._get_resume_version_key(resume_id)
            cached_version = redis_client.get(version_key)
            
            if not cached_version:
                return False
            
            cached_updated_at = datetime.fromisoformat(cached_version)
            return cached_updated_at >= current_updated_at
            
        except Exception as e:
            current_app.logger.error(f"Error checking resume cache validity: {e}")
            return False
    
    @staticmethod
    def get_cache_stats() -> Dict[str, Any]:
        """获取缓存统计信息"""
        redis_client = get_redis_client()
        if not redis_client:
            return {"error": "Redis client not available"}
        
        try:
            pattern = f"{CacheService.QUESTION_CACHE_PREFIX}:*"
            keys = redis_client.keys(pattern)
            
            return {
                "total_cached_entries": len(keys),
                "cache_prefix": CacheService.QUESTION_CACHE_PREFIX,
                "expiry_days": CacheService.CACHE_EXPIRY_DAYS
            }
            
        except Exception as e:
            current_app.logger.error(f"Error getting cache stats: {e}")
            return {"error": str(e)} 