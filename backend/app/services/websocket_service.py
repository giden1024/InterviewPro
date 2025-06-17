import asyncio
import json
import base64
import logging
import time
import io
import wave
import threading
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from queue import Queue, Empty
import numpy as np

try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class VoiceConfig:
    """语音配置类"""
    sample_rate: int = 16000
    channels: int = 1
    chunk_size: int = 1024
    language: str = 'zh-CN'
    provider: str = 'google'  # google, azure, whisper, baidu
    api_key: Optional[str] = None
    confidence_threshold: float = 0.7

@dataclass
class AudioChunk:
    """音频块数据结构"""
    data: bytes
    chunk_id: int
    user_id: str
    interview_id: str
    timestamp: float
    is_final: bool = False
    sample_rate: int = 16000

@dataclass
class TranscriptionResult:
    """转录结果数据结构"""
    text: str
    confidence: float
    user_id: str
    interview_id: str
    chunk_id: int
    is_final: bool
    language: str
    timestamp: float
    processing_time: float

class VoiceBuffer:
    """语音数据缓冲器"""
    
    def __init__(self, max_buffer_size: int = 10):
        self.buffer: List[AudioChunk] = []
        self.max_buffer_size = max_buffer_size
        self.lock = threading.Lock()
    
    def add_chunk(self, chunk: AudioChunk):
        """添加音频块"""
        with self.lock:
            self.buffer.append(chunk)
            if len(self.buffer) > self.max_buffer_size:
                self.buffer.pop(0)
    
    def get_continuous_audio(self, user_id: str, interview_id: str) -> bytes:
        """获取连续的音频数据"""
        with self.lock:
            relevant_chunks = [
                chunk for chunk in self.buffer 
                if chunk.user_id == user_id and chunk.interview_id == interview_id
            ]
            if not relevant_chunks:
                return b''
            
            # 合并音频数据
            combined_data = b''.join([chunk.data for chunk in relevant_chunks])
            return combined_data
    
    def clear_buffer(self, user_id: str, interview_id: str):
        """清空特定用户的缓冲区"""
        with self.lock:
            self.buffer = [
                chunk for chunk in self.buffer 
                if not (chunk.user_id == user_id and chunk.interview_id == interview_id)
            ]

class STTProvider:
    """语音转文本提供商基类"""
    
    def __init__(self, config: VoiceConfig):
        self.config = config
    
    def transcribe(self, audio_data: bytes) -> TranscriptionResult:
        """转录音频数据"""
        raise NotImplementedError
    
    def transcribe_stream(self, audio_chunks: List[AudioChunk]) -> List[TranscriptionResult]:
        """流式转录音频数据"""
        raise NotImplementedError

class GoogleSTTProvider(STTProvider):
    """Google Speech-to-Text 提供商"""
    
    def __init__(self, config: VoiceConfig):
        super().__init__(config)
        if not SPEECH_RECOGNITION_AVAILABLE:
            raise ImportError("需要安装 speech_recognition 库")
        self.recognizer = sr.Recognizer()
    
    def transcribe(self, audio_data: bytes) -> TranscriptionResult:
        """使用Google API转录音频"""
        start_time = time.time()
        
        try:
            # 将音频数据转换为AudioData对象
            audio_io = io.BytesIO(audio_data)
            with sr.AudioFile(audio_io) as source:
                audio = self.recognizer.record(source)
            
            # 使用Google Web Speech API
            text = self.recognizer.recognize_google(
                audio, 
                language=self.config.language
            )
            
            confidence = 0.9  # Google API不返回置信度，使用默认值
            
            return TranscriptionResult(
                text=text,
                confidence=confidence,
                user_id="",
                interview_id="",
                chunk_id=0,
                is_final=True,
                language=self.config.language,
                timestamp=time.time(),
                processing_time=time.time() - start_time
            )
            
        except sr.UnknownValueError:
            logger.warning("Google STT: 无法识别音频")
            return self._create_empty_result(start_time)
        except sr.RequestError as e:
            logger.error(f"Google STT API错误: {e}")
            return self._create_empty_result(start_time)
        except Exception as e:
            logger.error(f"Google STT处理错误: {e}")
            return self._create_empty_result(start_time)
    
    def _create_empty_result(self, start_time: float) -> TranscriptionResult:
        """创建空结果"""
        return TranscriptionResult(
            text="",
            confidence=0.0,
            user_id="",
            interview_id="",
            chunk_id=0,
            is_final=True,
            language=self.config.language,
            timestamp=time.time(),
            processing_time=time.time() - start_time
        )

class WhisperSTTProvider(STTProvider):
    """Whisper STT 提供商"""
    
    def __init__(self, config: VoiceConfig):
        super().__init__(config)
        if not WHISPER_AVAILABLE:
            raise ImportError("需要安装 openai-whisper 库")
        self.model = whisper.load_model("base")
    
    def transcribe(self, audio_data: bytes) -> TranscriptionResult:
        """使用Whisper转录音频"""
        start_time = time.time()
        
        try:
            # 将音频数据保存为临时文件
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            # 使用Whisper转录
            result = self.model.transcribe(
                temp_file_path,
                language=self.config.language[:2] if self.config.language else None
            )
            
            # 清理临时文件
            import os
            os.unlink(temp_file_path)
            
            return TranscriptionResult(
                text=result["text"].strip(),
                confidence=0.95,  # Whisper不提供置信度，使用高默认值
                user_id="",
                interview_id="",
                chunk_id=0,
                is_final=True,
                language=self.config.language,
                timestamp=time.time(),
                processing_time=time.time() - start_time
            )
            
        except Exception as e:
            logger.error(f"Whisper STT处理错误: {e}")
            return TranscriptionResult(
                text="",
                confidence=0.0,
                user_id="",
                interview_id="",
                chunk_id=0,
                is_final=True,
                language=self.config.language,
                timestamp=time.time(),
                processing_time=time.time() - start_time
            )

class BaiduSTTProvider(STTProvider):
    """百度语音识别提供商"""
    
    def __init__(self, config: VoiceConfig):
        super().__init__(config)
        if not REQUESTS_AVAILABLE:
            raise ImportError("需要安装 requests 库")
        self.api_key = config.api_key
        self.secret_key = getattr(config, 'secret_key', None)
    
    def transcribe(self, audio_data: bytes) -> TranscriptionResult:
        """使用百度API转录音频"""
        start_time = time.time()
        
        try:
            if not self.api_key or not self.secret_key:
                raise ValueError("百度STT需要API Key和Secret Key")
            
            # 获取access token
            token = self._get_access_token()
            
            # 准备API请求
            url = "https://vop.baidu.com/server_api"
            headers = {'Content-Type': 'application/json'}
            
            # 编码音频数据
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            data = {
                "format": "wav",
                "rate": self.config.sample_rate,
                "channel": self.config.channels,
                "cuid": "python_client",
                "token": token,
                "speech": audio_base64,
                "len": len(audio_data)
            }
            
            response = requests.post(url, json=data, headers=headers)
            result = response.json()
            
            if result.get("err_no") == 0:
                text = result.get("result", [""])[0]
                return TranscriptionResult(
                    text=text,
                    confidence=0.9,
                    user_id="",
                    interview_id="",
                    chunk_id=0,
                    is_final=True,
                    language=self.config.language,
                    timestamp=time.time(),
                    processing_time=time.time() - start_time
                )
            else:
                logger.error(f"百度STT API错误: {result}")
                return self._create_empty_result(start_time)
                
        except Exception as e:
            logger.error(f"百度STT处理错误: {e}")
            return self._create_empty_result(start_time)
    
    def _get_access_token(self) -> str:
        """获取百度API access token"""
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": self.api_key,
            "client_secret": self.secret_key
        }
        
        response = requests.post(url, params=params)
        result = response.json()
        return result.get("access_token", "")
    
    def _create_empty_result(self, start_time: float) -> TranscriptionResult:
        """创建空结果"""
        return TranscriptionResult(
            text="",
            confidence=0.0,
            user_id="",
            interview_id="",
            chunk_id=0,
            is_final=True,
            language=self.config.language,
            timestamp=time.time(),
            processing_time=time.time() - start_time
        )

class VoiceTranscriptionService:
    """语音转录服务"""
    
    def __init__(self, config: VoiceConfig = None):
        self.config = config or VoiceConfig()
        self.buffer = VoiceBuffer()
        self.processing_queue = Queue()
        self.result_callbacks: Dict[str, Callable] = {}
        self.is_running = False
        self.worker_thread = None
        
        # 初始化STT提供商
        self.stt_provider = self._create_stt_provider()
        
        # 活跃会话追踪
        self.active_sessions: Dict[str, Dict] = {}
        
        logger.info(f"语音转录服务初始化完成，使用提供商: {self.config.provider}")
    
    def _create_stt_provider(self) -> STTProvider:
        """创建STT提供商"""
        if self.config.provider == 'google':
            return GoogleSTTProvider(self.config)
        elif self.config.provider == 'whisper':
            return WhisperSTTProvider(self.config)
        elif self.config.provider == 'baidu':
            return BaiduSTTProvider(self.config)
        else:
            logger.warning(f"未知的STT提供商: {self.config.provider}，使用Google作为默认")
            return GoogleSTTProvider(self.config)
    
    def start_service(self):
        """启动转录服务"""
        if self.is_running:
            logger.warning("语音转录服务已在运行")
            return
        
        self.is_running = True
        self.worker_thread = threading.Thread(target=self._process_audio_worker)
        self.worker_thread.daemon = True
        self.worker_thread.start()
        
        logger.info("语音转录服务已启动")
    
    def stop_service(self):
        """停止转录服务"""
        self.is_running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5)
        
        logger.info("语音转录服务已停止")
    
    def process_voice_data(self, audio_data: bytes, user_id: str, interview_id: str, 
                          chunk_id: int, is_final: bool = False) -> Optional[TranscriptionResult]:
        """处理语音数据"""
        try:
            # 创建音频块
            chunk = AudioChunk(
                data=audio_data,
                chunk_id=chunk_id,
                user_id=user_id,
                interview_id=interview_id,
                timestamp=time.time(),
                is_final=is_final,
                sample_rate=self.config.sample_rate
            )
            
            # 添加到缓冲区
            self.buffer.add_chunk(chunk)
            
            # 如果是最终块或缓冲区达到阈值，处理音频
            if is_final or self._should_process_buffer(user_id, interview_id):
                # 获取连续音频数据
                continuous_audio = self.buffer.get_continuous_audio(user_id, interview_id)
                
                if continuous_audio:
                    # 加入处理队列
                    task = {
                        'audio_data': continuous_audio,
                        'user_id': user_id,
                        'interview_id': interview_id,
                        'chunk_id': chunk_id,
                        'is_final': is_final,
                        'timestamp': time.time()
                    }
                    
                    self.processing_queue.put(task)
                    
                    # 如果是最终块，清空缓冲区
                    if is_final:
                        self.buffer.clear_buffer(user_id, interview_id)
            
            return None  # 异步处理，结果通过回调返回
            
        except Exception as e:
            logger.error(f"处理语音数据错误: {e}")
            return None
    
    def _should_process_buffer(self, user_id: str, interview_id: str) -> bool:
        """判断是否应该处理缓冲区"""
        # 简单策略：缓冲区有3个或更多块时处理
        session_key = f"{user_id}_{interview_id}"
        current_time = time.time()
        
        # 更新会话信息
        if session_key not in self.active_sessions:
            self.active_sessions[session_key] = {
                'last_process_time': current_time,
                'chunk_count': 0
            }
        
        session = self.active_sessions[session_key]
        session['chunk_count'] += 1
        
        # 每隔2秒或每3个块处理一次
        time_threshold = current_time - session['last_process_time'] > 2.0
        chunk_threshold = session['chunk_count'] >= 3
        
        if time_threshold or chunk_threshold:
            session['last_process_time'] = current_time
            session['chunk_count'] = 0
            return True
        
        return False
    
    def _process_audio_worker(self):
        """音频处理工作线程"""
        logger.info("音频处理工作线程已启动")
        
        while self.is_running:
            try:
                # 获取处理任务
                task = self.processing_queue.get(timeout=1.0)
                
                # 处理音频
                result = self._transcribe_audio(task)
                
                # 调用回调函数
                if result and result.text.strip():
                    callback_key = f"{task['user_id']}_{task['interview_id']}"
                    if callback_key in self.result_callbacks:
                        self.result_callbacks[callback_key](result)
                
                self.processing_queue.task_done()
                
            except Empty:
                continue
            except Exception as e:
                logger.error(f"音频处理工作线程错误: {e}")
    
    def _transcribe_audio(self, task: Dict) -> Optional[TranscriptionResult]:
        """转录音频任务"""
        try:
            # 使用STT提供商转录
            result = self.stt_provider.transcribe(task['audio_data'])
            
            # 更新结果信息
            result.user_id = task['user_id']
            result.interview_id = task['interview_id']
            result.chunk_id = task['chunk_id']
            result.is_final = task['is_final']
            
            # 过滤低置信度结果
            if result.confidence < self.config.confidence_threshold:
                logger.debug(f"过滤低置信度结果: {result.confidence}")
                return None
            
            logger.info(f"转录完成 - 用户: {task['user_id']}, 文本: '{result.text[:50]}...', 置信度: {result.confidence}")
            
            return result
            
        except Exception as e:
            logger.error(f"音频转录错误: {e}")
            return None
    
    def register_result_callback(self, user_id: str, interview_id: str, callback: Callable):
        """注册结果回调函数"""
        callback_key = f"{user_id}_{interview_id}"
        self.result_callbacks[callback_key] = callback
        logger.info(f"已注册语音转录回调: {callback_key}")
    
    def unregister_result_callback(self, user_id: str, interview_id: str):
        """取消注册结果回调函数"""
        callback_key = f"{user_id}_{interview_id}"
        if callback_key in self.result_callbacks:
            del self.result_callbacks[callback_key]
            logger.info(f"已取消语音转录回调: {callback_key}")
    
    def get_service_stats(self) -> Dict[str, Any]:
        """获取服务统计信息"""
        return {
            'is_running': self.is_running,
            'provider': self.config.provider,
            'queue_size': self.processing_queue.qsize(),
            'active_callbacks': len(self.result_callbacks),
            'active_sessions': len(self.active_sessions),
            'buffer_size': len(self.buffer.buffer) if self.buffer else 0
        }

# 全局语音转录服务实例
_voice_service_instance = None

def get_voice_service(config: VoiceConfig = None) -> VoiceTranscriptionService:
    """获取语音转录服务单例"""
    global _voice_service_instance
    
    if _voice_service_instance is None:
        _voice_service_instance = VoiceTranscriptionService(config)
        _voice_service_instance.start_service()
    
    return _voice_service_instance

def shutdown_voice_service():
    """关闭语音转录服务"""
    global _voice_service_instance
    
    if _voice_service_instance:
        _voice_service_instance.stop_service()
        _voice_service_instance = None
        logger.info("全局语音转录服务已关闭") 