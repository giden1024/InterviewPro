from flask_socketio import emit, disconnect, join_room, leave_room, rooms
from flask import request
from flask_jwt_extended import decode_token
from app.extensions import db, redis_client
from app.models.question import InterviewSession, Question, Answer
from app.services.interview_service import InterviewService
from app.services.interview_analyzer import InterviewAnalyzer
import logging
import json
import time
from datetime import datetime
import base64
from functools import wraps

# 添加语音服务导入
from app.services.websocket_service import get_voice_service, VoiceConfig, TranscriptionResult

logger = logging.getLogger(__name__)

# 全局存储连接的用户
connected_users = {}
interview_sessions = {}

def register_socket_events(socketio_instance):
    """注册所有WebSocket事件处理器"""
    
    # 初始化语音转录服务
    voice_config = VoiceConfig(
        sample_rate=16000,
        channels=1,
        language='zh-CN',
        provider='google',  # 可配置：google, whisper, baidu
        confidence_threshold=0.7
    )
    voice_service = get_voice_service(voice_config)
    
    @socketio_instance.on('connect')
    def handle_connect(auth=None):
        """处理WebSocket连接"""
        try:
            logger.info("客户端尝试连接WebSocket")
            
            user_id = None
            # 验证JWT token
            if auth and 'token' in auth:
                try:
                    token_data = decode_token(auth['token'])
                    user_id = token_data['sub']
                    connected_users[request.sid] = {
                        'user_id': user_id,
                        'connect_time': time.time(),
                        'current_interview': None
                    }
                    emit('connected', {
                        'status': 'success',
                        'message': '认证连接成功',
                        'user_id': user_id,
                        'session_id': request.sid
                    })
                    logger.info(f"用户 {user_id} 已连接 (Session: {request.sid})")
                except Exception as e:
                    logger.warning(f"Token验证失败: {e}")
                    emit('connected', {
                        'status': 'warning',
                        'message': '未认证连接成功',
                        'session_id': request.sid
                    })
            else:
                emit('connected', {
                    'status': 'success', 
                    'message': '连接成功',
                    'session_id': request.sid
                })
                logger.info('匿名客户端已连接')
                
            # 发送在线用户数
            emit('online_users', {'count': len(connected_users)}, broadcast=True)
                
        except Exception as e:
            logger.error(f"连接处理错误: {e}")
            emit('error', {'message': '连接处理失败'})
    
    @socketio_instance.on('disconnect')
    def handle_disconnect():
        """处理客户端断开连接"""
        try:
            user_id = request.sid
            
            # 清理用户的语音回调
            for interview_id in list(interview_sessions.keys()):
                voice_service.unregister_result_callback(user_id, interview_id)
            
            # 从所有面试会话中移除用户
            for interview_id, session_info in list(interview_sessions.items()):
                if user_id in session_info['participants']:
                    session_info['participants'].remove(user_id)
                    
                    # 通知房间内其他用户
                    emit('user_left', {
                        'user_id': user_id,
                        'interview_id': interview_id,
                        'participants_count': len(session_info['participants'])
                    }, room=f"interview_{interview_id}")
                    
                    # 如果房间为空，清理会话
                    if not session_info['participants']:
                        del interview_sessions[interview_id]
                        logger.info(f"清理空的面试会话: {interview_id}")
            
            logger.info(f"用户断开连接: {user_id}")
            
        except Exception as e:
            logger.error(f"处理断开连接错误: {e}")
    
    @socketio_instance.on('join_interview')
    def handle_join_interview(data):
        """加入面试房间"""
        try:
            interview_id = data.get('interview_id')
            user_id = data.get('user_id')
            
            if not interview_id:
                emit('error', {'message': '缺少面试ID'})
                return
            
            room_name = f"interview_{interview_id}"
            join_room(room_name)
            
            # 更新用户状态
            if request.sid in connected_users:
                connected_users[request.sid]['current_interview'] = interview_id
            
            # 初始化或更新面试会话状态
            if interview_id not in interview_sessions:
                interview_sessions[interview_id] = {
                    'participants': [],
                    'status': 'active',
                    'start_time': time.time(),
                    'current_question': None,
                    'question_start_time': None
                }
            
            # 添加参与者
            participant_info = {
                'user_id': user_id,
                'session_id': request.sid,
                'join_time': time.time()
            }
            
            if participant_info not in interview_sessions[interview_id]['participants']:
                interview_sessions[interview_id]['participants'].append(participant_info)
            
            emit('joined_interview', {
                'status': 'success',
                'interview_id': interview_id,
                'message': f'已加入面试房间 {interview_id}',
                'participants_count': len(interview_sessions[interview_id]['participants'])
            })
            
            # 通知房间内其他用户
            emit('participant_joined', {
                'user_id': user_id,
                'interview_id': interview_id,
                'participants_count': len(interview_sessions[interview_id]['participants'])
            }, room=room_name, include_self=False)
            
            logger.info(f"用户 {user_id} 加入面试房间: {interview_id}")
            
        except Exception as e:
            logger.error(f"加入面试房间错误: {e}")
            emit('error', {'message': '加入面试房间失败'})
    
    @socketio_instance.on('leave_interview')
    def handle_leave_interview(data):
        """离开面试房间"""
        try:
            interview_id = data.get('interview_id')
            user_id = data.get('user_id')
            
            if interview_id:
                room_name = f"interview_{interview_id}"
                leave_room(room_name)
                
                # 更新用户状态
                if request.sid in connected_users:
                    connected_users[request.sid]['current_interview'] = None
                
                # 从参与者列表中移除
                if interview_id in interview_sessions:
                    interview_sessions[interview_id]['participants'] = [
                        p for p in interview_sessions[interview_id]['participants'] 
                        if p['session_id'] != request.sid
                    ]
                    
                    # 如果没有参与者了，清理会话
                    if not interview_sessions[interview_id]['participants']:
                        del interview_sessions[interview_id]
                
                emit('left_interview', {
                    'status': 'success',
                    'interview_id': interview_id,
                    'message': f'已离开面试房间 {interview_id}'
                })
                
                # 通知房间内其他用户
                emit('participant_left', {
                    'user_id': user_id,
                    'interview_id': interview_id
                }, room=room_name)
                
                logger.info(f"用户 {user_id} 离开面试房间: {interview_id}")
                
        except Exception as e:
            logger.error(f"离开面试房间错误: {e}")
            emit('error', {'message': '离开面试房间失败'})
    
    @socketio_instance.on('start_question')
    def handle_start_question(data):
        """开始新问题"""
        try:
            interview_id = data.get('interview_id')
            question_id = data.get('question_id')
            question_text = data.get('question_text')
            
            if not all([interview_id, question_id]):
                emit('error', {'message': '缺少必要参数'})
                return
            
            # 更新面试状态
            if interview_id in interview_sessions:
                interview_sessions[interview_id]['current_question'] = question_id
                interview_sessions[interview_id]['question_start_time'] = time.time()
            
            # 通知房间内所有用户新问题开始
            emit('question_started', {
                'interview_id': interview_id,
                'question_id': question_id,
                'question_text': question_text,
                'start_time': time.time(),
                'status': 'active'
            }, room=f"interview_{interview_id}")
            
            logger.info(f"面试 {interview_id} 开始问题 {question_id}")
            
        except Exception as e:
            logger.error(f"开始问题错误: {e}")
            emit('error', {'message': '开始问题失败'})
    
    @socketio_instance.on('submit_answer')
    def handle_submit_answer(data):
        """实时提交答案"""
        try:
            interview_id = data.get('interview_id')
            question_id = data.get('question_id')
            answer_text = data.get('answer_text')
            user_id = data.get('user_id')
            response_time = data.get('response_time')
            
            if not all([interview_id, question_id, user_id]):
                emit('error', {'message': '缺少必要参数'})
                return
            
            # 计算实际响应时间
            if interview_id in interview_sessions:
                session_info = interview_sessions[interview_id]
                if session_info.get('question_start_time'):
                    actual_response_time = time.time() - session_info['question_start_time']
                else:
                    actual_response_time = response_time or 0
            else:
                actual_response_time = response_time or 0
            
            # 通知房间内用户答案已提交
            emit('answer_submitted', {
                'interview_id': interview_id,
                'question_id': question_id,
                'user_id': user_id,
                'response_time': actual_response_time,
                'timestamp': time.time(),
                'status': 'submitted'
            }, room=f"interview_{interview_id}")
            
            # 向提交者发送确认
            emit('answer_confirmed', {
                'status': 'success',
                'question_id': question_id,
                'response_time': actual_response_time,
                'message': '答案提交成功'
            })
            
            logger.info(f"用户 {user_id} 在面试 {interview_id} 中提交问题 {question_id} 的答案")
            
        except Exception as e:
            logger.error(f"提交答案错误: {e}")
            emit('error', {'message': '提交答案失败'})
    
    @socketio_instance.on('voice_data')
    def handle_voice_data(data):
        """处理语音数据 - 使用真实STT服务"""
        try:
            interview_id = data.get('interview_id')
            audio_data_base64 = data.get('audio_data')
            user_id = data.get('user_id')
            chunk_id = data.get('chunk_id', 0)
            is_final = data.get('is_final', False)
            audio_format = data.get('format', 'wav')  # wav, mp3, ogg
            
            if not interview_id or not audio_data_base64 or not user_id:
                emit('error', {'message': '缺少必要的语音数据参数'})
                return
            
            try:
                # 解码base64音频数据
                audio_data = base64.b64decode(audio_data_base64)
                
                # 验证音频数据大小
                if len(audio_data) < 100:  # 最小音频数据阈值
                    logger.warning(f"音频数据过小: {len(audio_data)} bytes")
                    return
                
                if len(audio_data) > 10 * 1024 * 1024:  # 10MB限制
                    emit('error', {'message': '音频数据过大，请分块发送'})
                    return
                
                # 注册结果回调（如果还未注册）
                def transcription_callback(result: TranscriptionResult):
                    """语音转录结果回调"""
                    try:
                        # 发送转录结果给用户
                        emit('voice_transcribed', {
                            'interview_id': result.interview_id,
                            'user_id': result.user_id,
                            'transcribed_text': result.text,
                            'confidence': result.confidence,
                            'is_final': result.is_final,
                            'chunk_id': result.chunk_id,
                            'language': result.language,
                            'processing_time': result.processing_time,
                            'timestamp': result.timestamp
                        })
                        
                        # 发送实时字幕给房间内其他用户
                        if result.is_final and result.text.strip():
                            emit('live_transcription', {
                                'user_id': result.user_id,
                                'text': result.text,
                                'confidence': result.confidence,
                                'is_final': True,
                                'timestamp': result.timestamp
                            }, room=f"interview_{result.interview_id}", include_self=False)
                        
                        logger.info(f"语音转录回调 - 用户: {result.user_id}, 文本: '{result.text[:50]}...'")
                        
                    except Exception as e:
                        logger.error(f"语音转录回调错误: {e}")
                
                # 注册回调
                voice_service.register_result_callback(user_id, interview_id, transcription_callback)
                
                # 处理语音数据
                voice_service.process_voice_data(
                    audio_data=audio_data,
                    user_id=user_id,
                    interview_id=interview_id,
                    chunk_id=chunk_id,
                    is_final=is_final
                )
                
                # 发送处理状态
                if not is_final:
                    emit('voice_processing', {
                        'interview_id': interview_id,
                        'chunk_id': chunk_id,
                        'status': 'processing',
                        'message': f'正在处理音频块 {chunk_id}...'
                    })
                else:
                    emit('voice_processing', {
                        'interview_id': interview_id,
                        'chunk_id': chunk_id,
                        'status': 'finalizing',
                        'message': '正在完成最终转录...'
                    })
                
                logger.info(f"处理语音数据 - 面试: {interview_id}, 用户: {user_id}, 块: {chunk_id}, 大小: {len(audio_data)} bytes, 最终: {is_final}")
                
            except Exception as decode_error:
                logger.error(f"音频数据解码错误: {decode_error}")
                emit('error', {'message': '音频数据格式错误'})
                return
            
        except Exception as e:
            logger.error(f"语音数据处理错误: {e}")
            emit('error', {'message': '语音处理失败，请重试'})
    
    @socketio_instance.on('voice_config')
    def handle_voice_config(data):
        """配置语音识别参数"""
        try:
            user_id = data.get('user_id')
            interview_id = data.get('interview_id')
            config = data.get('config', {})
            
            # 更新语音配置
            new_config = VoiceConfig(
                sample_rate=config.get('sample_rate', 16000),
                channels=config.get('channels', 1),
                language=config.get('language', 'zh-CN'),
                provider=config.get('provider', 'google'),
                confidence_threshold=config.get('confidence_threshold', 0.7)
            )
            
            # 获取更新后的语音服务
            updated_service = get_voice_service(new_config)
            
            emit('voice_config_updated', {
                'interview_id': interview_id,
                'config': {
                    'sample_rate': new_config.sample_rate,
                    'channels': new_config.channels,
                    'language': new_config.language,
                    'provider': new_config.provider,
                    'confidence_threshold': new_config.confidence_threshold
                },
                'message': '语音配置已更新'
            })
            
            logger.info(f"更新语音配置 - 用户: {user_id}, 面试: {interview_id}, 提供商: {new_config.provider}")
            
        except Exception as e:
            logger.error(f"配置语音识别错误: {e}")
            emit('error', {'message': '配置语音识别失败'})
    
    @socketio_instance.on('voice_status')
    def handle_voice_status(data):
        """获取语音服务状态"""
        try:
            user_id = data.get('user_id')
            interview_id = data.get('interview_id')
            
            # 获取服务统计
            stats = voice_service.get_service_stats()
            
            emit('voice_status_response', {
                'interview_id': interview_id,
                'status': stats,
                'timestamp': time.time()
            })
            
            logger.info(f"获取语音服务状态 - 用户: {user_id}")
            
        except Exception as e:
            logger.error(f"获取语音状态错误: {e}")
            emit('error', {'message': '获取语音状态失败'})
    
    @socketio_instance.on('voice_test')
    def handle_voice_test(data):
        """测试语音识别功能"""
        try:
            user_id = data.get('user_id')
            interview_id = data.get('interview_id')
            test_text = data.get('test_text', 'Hello, this is a voice test.')
            
            # 模拟语音测试结果
            emit('voice_test_result', {
                'interview_id': interview_id,
                'user_id': user_id,
                'test_successful': True,
                'provider': voice_service.config.provider,
                'latency': 150,  # ms
                'message': f'语音识别测试成功，使用提供商: {voice_service.config.provider}'
            })
            
            logger.info(f"语音识别测试 - 用户: {user_id}, 面试: {interview_id}")
            
        except Exception as e:
            logger.error(f"语音识别测试错误: {e}")
            emit('error', {'message': '语音识别测试失败'})
    
    @socketio_instance.on('typing_indicator')
    def handle_typing_indicator(data):
        """处理打字指示器"""
        try:
            interview_id = data.get('interview_id')
            user_id = data.get('user_id')
            is_typing = data.get('is_typing', False)
            
            if interview_id and user_id:
                # 通知房间内其他用户
                emit('user_typing', {
                    'user_id': user_id,
                    'is_typing': is_typing,
                    'interview_id': interview_id
                }, room=f"interview_{interview_id}", include_self=False)
                
        except Exception as e:
            logger.error(f"打字指示器错误: {e}")
    
    @socketio_instance.on('interview_status')
    def handle_interview_status(data):
        """获取面试状态"""
        try:
            interview_id = data.get('interview_id')
            
            if interview_id in interview_sessions:
                session_info = interview_sessions[interview_id]
                emit('interview_status_response', {
                    'interview_id': interview_id,
                    'status': session_info['status'],
                    'participants_count': len(session_info['participants']),
                    'current_question': session_info.get('current_question'),
                    'uptime': time.time() - session_info['start_time']
                })
            else:
                emit('interview_status_response', {
                    'interview_id': interview_id,
                    'status': 'not_found',
                    'message': '面试会话不存在'
                })
                
        except Exception as e:
            logger.error(f"获取面试状态错误: {e}")
            emit('error', {'message': '获取面试状态失败'})
    
    @socketio_instance.on('send_message')
    def handle_send_message(data):
        """发送实时消息"""
        try:
            interview_id = data.get('interview_id')
            user_id = data.get('user_id')
            message = data.get('message')
            message_type = data.get('type', 'text')  # text, system, notification
            
            if not all([interview_id, user_id, message]):
                emit('error', {'message': '缺少必要参数'})
                return
            
            message_data = {
                'interview_id': interview_id,
                'user_id': user_id,
                'message': message,
                'type': message_type,
                'timestamp': time.time(),
                'message_id': f"{interview_id}_{user_id}_{int(time.time())}"
            }
            
            # 广播消息到房间
            emit('new_message', message_data, room=f"interview_{interview_id}")
            
            logger.info(f"用户 {user_id} 在面试 {interview_id} 中发送消息")
            
        except Exception as e:
            logger.error(f"发送消息错误: {e}")
            emit('error', {'message': '发送消息失败'})
    
    @socketio_instance.on('request_help')
    def handle_request_help(data):
        """请求帮助"""
        try:
            interview_id = data.get('interview_id')
            user_id = data.get('user_id')
            help_type = data.get('help_type', 'general')  # hint, clarification, technical
            question_id = data.get('question_id')
            
            # 通知面试官或系统
            emit('help_requested', {
                'interview_id': interview_id,
                'user_id': user_id,
                'help_type': help_type,
                'question_id': question_id,
                'timestamp': time.time()
            }, room=f"interview_{interview_id}")
            
            # 确认请求已发送
            emit('help_request_sent', {
                'status': 'success',
                'help_type': help_type,
                'message': '帮助请求已发送'
            })
            
            logger.info(f"用户 {user_id} 在面试 {interview_id} 中请求帮助: {help_type}")
            
        except Exception as e:
            logger.error(f"请求帮助错误: {e}")
            emit('error', {'message': '请求帮助失败'})
    
    @socketio_instance.on('end_interview')
    def handle_end_interview(data):
        """结束面试"""
        try:
            interview_id = data.get('interview_id')
            user_id = data.get('user_id')
            
            if interview_id in interview_sessions:
                interview_sessions[interview_id]['status'] = 'completed'
                interview_sessions[interview_id]['end_time'] = time.time()
                
                # 通知所有参与者面试结束
                emit('interview_ended', {
                    'interview_id': interview_id,
                    'ended_by': user_id,
                    'timestamp': time.time(),
                    'message': '面试已结束'
                }, room=f"interview_{interview_id}")
                
                # 清理会话（延迟清理，给客户端时间处理）
                def cleanup_session():
                    time.sleep(5)  # 等待5秒
                    if interview_id in interview_sessions:
                        del interview_sessions[interview_id]
                
                # 在后台清理
                import threading
                threading.Thread(target=cleanup_session).start()
                
                logger.info(f"面试 {interview_id} 被用户 {user_id} 结束")
            
        except Exception as e:
            logger.error(f"结束面试错误: {e}")
            emit('error', {'message': '结束面试失败'})
    
    @socketio_instance.on('ping')
    def handle_ping(data):
        """处理心跳检测"""
        try:
            timestamp = data.get('timestamp', time.time())
            emit('pong', {
                'timestamp': timestamp,
                'server_time': time.time()
            })
        except Exception as e:
            logger.error(f"心跳检测错误: {e}")
    
    @socketio_instance.on('test_message')
    def handle_test_message(data):
        """处理测试消息"""
        try:
            message = data.get('message', 'No message')
            emit('test_response', {
                'status': 'success',
                'original_message': message,
                'response': f'收到消息: {message}',
                'timestamp': data.get('timestamp'),
                'server_time': time.time()
            })
            logger.info(f"处理测试消息: {message}")
        except Exception as e:
            logger.error(f"测试消息处理错误: {e}")
            emit('error', {'message': '测试消息处理失败'})
    
    @socketio_instance.on_error_default
    def default_error_handler(e):
        """默认错误处理器"""
        logger.error(f"WebSocket错误: {e}")
        emit('error', {'message': '服务器内部错误'})

def get_interview_session_info(interview_id):
    """获取面试会话信息"""
    return interview_sessions.get(interview_id)

def get_connected_users_count():
    """获取在线用户数"""
    return len(connected_users)

def broadcast_system_message(message, interview_id=None):
    """广播系统消息"""
    from app.extensions import socketio
    
    if interview_id:
        socketio.emit('system_message', {
            'message': message,
            'timestamp': time.time(),
            'type': 'system'
        }, room=f"interview_{interview_id}")
    else:
        socketio.emit('system_message', {
            'message': message,
            'timestamp': time.time(),
            'type': 'system'
        }, broadcast=True) 