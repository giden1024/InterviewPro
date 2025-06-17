"""
语音转录配置文件
"""
import os
from typing import Dict, Any

class VoiceTranscriptionConfig:
    """语音转录配置类"""
    
    # 基础音频配置
    SAMPLE_RATE = int(os.getenv('VOICE_SAMPLE_RATE', '16000'))
    CHANNELS = int(os.getenv('VOICE_CHANNELS', '1'))
    CHUNK_SIZE = int(os.getenv('VOICE_CHUNK_SIZE', '1024'))
    
    # 语言配置
    DEFAULT_LANGUAGE = os.getenv('VOICE_DEFAULT_LANGUAGE', 'zh-CN')
    SUPPORTED_LANGUAGES = {
        'zh-CN': '中文(简体)',
        'zh-TW': '中文(繁体)',
        'en-US': 'English (US)',
        'en-GB': 'English (UK)',
        'ja-JP': '日本語',
        'ko-KR': '한국어',
        'fr-FR': 'Français',
        'de-DE': 'Deutsch',
        'es-ES': 'Español',
        'it-IT': 'Italiano',
        'pt-BR': 'Português (Brasil)',
        'ru-RU': 'Русский'
    }
    
    # STT提供商配置
    DEFAULT_PROVIDER = os.getenv('VOICE_STT_PROVIDER', 'google')
    AVAILABLE_PROVIDERS = ['google', 'whisper', 'baidu', 'azure']
    
    # 置信度阈值
    CONFIDENCE_THRESHOLD = float(os.getenv('VOICE_CONFIDENCE_THRESHOLD', '0.7'))
    
    # Google STT配置
    GOOGLE_API_KEY = os.getenv('GOOGLE_SPEECH_API_KEY')
    
    # Azure STT配置
    AZURE_SPEECH_KEY = os.getenv('AZURE_SPEECH_KEY')
    AZURE_SPEECH_REGION = os.getenv('AZURE_SPEECH_REGION')
    
    # 百度STT配置
    BAIDU_API_KEY = os.getenv('BAIDU_SPEECH_API_KEY')
    BAIDU_SECRET_KEY = os.getenv('BAIDU_SPEECH_SECRET_KEY')
    
    # Whisper配置
    WHISPER_MODEL = os.getenv('WHISPER_MODEL', 'base')  # tiny, base, small, medium, large
    WHISPER_DEVICE = os.getenv('WHISPER_DEVICE', 'cpu')  # cpu, cuda
    
    # 音频处理配置
    MAX_AUDIO_SIZE = int(os.getenv('MAX_AUDIO_SIZE', str(10 * 1024 * 1024)))  # 10MB
    MIN_AUDIO_SIZE = int(os.getenv('MIN_AUDIO_SIZE', '100'))  # 100 bytes
    
    # 缓冲区配置
    MAX_BUFFER_SIZE = int(os.getenv('VOICE_MAX_BUFFER_SIZE', '10'))
    PROCESSING_INTERVAL = float(os.getenv('VOICE_PROCESSING_INTERVAL', '2.0'))  # 秒
    CHUNK_THRESHOLD = int(os.getenv('VOICE_CHUNK_THRESHOLD', '3'))
    
    # 性能配置
    MAX_CONCURRENT_TRANSCRIPTIONS = int(os.getenv('MAX_CONCURRENT_TRANSCRIPTIONS', '5'))
    TRANSCRIPTION_TIMEOUT = int(os.getenv('TRANSCRIPTION_TIMEOUT', '30'))  # 秒
    
    # 音频格式支持
    SUPPORTED_AUDIO_FORMATS = ['wav', 'mp3', 'ogg', 'flac', 'm4a']
    
    @classmethod
    def get_provider_config(cls, provider: str) -> Dict[str, Any]:
        """获取特定提供商的配置"""
        configs = {
            'google': {
                'api_key': cls.GOOGLE_API_KEY,
                'language': cls.DEFAULT_LANGUAGE,
                'confidence_threshold': cls.CONFIDENCE_THRESHOLD
            },
            'azure': {
                'speech_key': cls.AZURE_SPEECH_KEY,
                'speech_region': cls.AZURE_SPEECH_REGION,
                'language': cls.DEFAULT_LANGUAGE,
                'confidence_threshold': cls.CONFIDENCE_THRESHOLD
            },
            'baidu': {
                'api_key': cls.BAIDU_API_KEY,
                'secret_key': cls.BAIDU_SECRET_KEY,
                'language': cls.DEFAULT_LANGUAGE,
                'confidence_threshold': cls.CONFIDENCE_THRESHOLD
            },
            'whisper': {
                'model': cls.WHISPER_MODEL,
                'device': cls.WHISPER_DEVICE,
                'language': cls.DEFAULT_LANGUAGE[:2] if cls.DEFAULT_LANGUAGE else 'zh',
                'confidence_threshold': cls.CONFIDENCE_THRESHOLD
            }
        }
        
        return configs.get(provider, {})
    
    @classmethod
    def validate_provider_config(cls, provider: str) -> bool:
        """验证提供商配置是否完整"""
        if provider == 'google':
            return bool(cls.GOOGLE_API_KEY)
        elif provider == 'azure':
            return bool(cls.AZURE_SPEECH_KEY and cls.AZURE_SPEECH_REGION)
        elif provider == 'baidu':
            return bool(cls.BAIDU_API_KEY and cls.BAIDU_SECRET_KEY)
        elif provider == 'whisper':
            return True  # Whisper不需要API密钥
        else:
            return False
    
    @classmethod
    def get_fallback_provider(cls) -> str:
        """获取可用的备用提供商"""
        for provider in cls.AVAILABLE_PROVIDERS:
            if cls.validate_provider_config(provider):
                return provider
        return 'whisper'  # 最后备用选择
    
    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'sample_rate': cls.SAMPLE_RATE,
            'channels': cls.CHANNELS,
            'chunk_size': cls.CHUNK_SIZE,
            'default_language': cls.DEFAULT_LANGUAGE,
            'supported_languages': cls.SUPPORTED_LANGUAGES,
            'default_provider': cls.DEFAULT_PROVIDER,
            'available_providers': cls.AVAILABLE_PROVIDERS,
            'confidence_threshold': cls.CONFIDENCE_THRESHOLD,
            'max_audio_size': cls.MAX_AUDIO_SIZE,
            'min_audio_size': cls.MIN_AUDIO_SIZE,
            'max_buffer_size': cls.MAX_BUFFER_SIZE,
            'processing_interval': cls.PROCESSING_INTERVAL,
            'chunk_threshold': cls.CHUNK_THRESHOLD,
            'supported_audio_formats': cls.SUPPORTED_AUDIO_FORMATS
        } 