#!/usr/bin/env python3
"""
语音转录功能演示和测试脚本
"""
import os
import sys
import time
import base64
import threading
import json
import wave
import asyncio
from typing import Dict, Any

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app.services.websocket_service import (
        VoiceTranscriptionService, 
        VoiceConfig, 
        TranscriptionResult,
        get_voice_service,
        shutdown_voice_service
    )
    from app.config.voice_config import VoiceTranscriptionConfig
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保在正确的环境中运行此脚本")
    sys.exit(1)

class VoiceTranscriptionDemo:
    """语音转录演示类"""
    
    def __init__(self):
        self.results = []
        self.demo_running = False
        
        # 初始化配置
        self.config = VoiceConfig(
            sample_rate=VoiceTranscriptionConfig.SAMPLE_RATE,
            channels=VoiceTranscriptionConfig.CHANNELS,
            language=VoiceTranscriptionConfig.DEFAULT_LANGUAGE,
            provider=VoiceTranscriptionConfig.DEFAULT_PROVIDER,
            confidence_threshold=VoiceTranscriptionConfig.CONFIDENCE_THRESHOLD
        )
        
        self.service = None
    
    def print_header(self):
        """打印演示标题"""
        print("=" * 80)
        print("🎤 语音转录功能演示 - InterviewGenius AI")
        print("=" * 80)
        print()
        
    def print_config_info(self):
        """打印配置信息"""
        print("📋 当前配置:")
        print(f"   • 采样率: {self.config.sample_rate} Hz")
        print(f"   • 声道数: {self.config.channels}")
        print(f"   • 语言: {self.config.language}")
        print(f"   • STT提供商: {self.config.provider}")
        print(f"   • 置信度阈值: {self.config.confidence_threshold}")
        print()
        
        # 检查提供商可用性
        print("🔧 STT提供商状态:")
        for provider in VoiceTranscriptionConfig.AVAILABLE_PROVIDERS:
            is_available = VoiceTranscriptionConfig.validate_provider_config(provider)
            status = "✅ 可用" if is_available else "❌ 配置不完整"
            print(f"   • {provider.capitalize()}: {status}")
        print()
    
    def create_test_audio_data(self, text: str = "测试音频数据") -> bytes:
        """创建模拟音频数据"""
        # 创建简单的WAV格式音频数据
        sample_rate = self.config.sample_rate
        duration = 2.0  # 2秒
        frequency = 440  # A4音符
        
        import numpy as np
        
        # 生成正弦波
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        wave_data = np.sin(frequency * 2 * np.pi * t)
        
        # 转换为16位整数
        wave_data = (wave_data * 32767).astype(np.int16)
        
        # 创建WAV文件内容
        import io
        import wave
        
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(self.config.channels)
            wav_file.setsampwidth(2)  # 16位
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(wave_data.tobytes())
        
        return wav_buffer.getvalue()
    
    def result_callback(self, result: TranscriptionResult):
        """转录结果回调函数"""
        self.results.append(result)
        
        print(f"🎯 转录结果:")
        print(f"   • 用户ID: {result.user_id}")
        print(f"   • 面试ID: {result.interview_id}")
        print(f"   • 转录文本: '{result.text}'")
        print(f"   • 置信度: {result.confidence:.2f}")
        print(f"   • 语言: {result.language}")
        print(f"   • 处理时间: {result.processing_time:.3f}秒")
        print(f"   • 是否最终结果: {result.is_final}")
        print()
    
    def test_basic_transcription(self):
        """测试基础转录功能"""
        print("🧪 测试 1: 基础语音转录功能")
        print("-" * 50)
        
        try:
            # 初始化服务
            self.service = get_voice_service(self.config)
            
            # 注册回调
            user_id = "demo_user_001"
            interview_id = "demo_interview_001"
            self.service.register_result_callback(user_id, interview_id, self.result_callback)
            
            # 创建测试音频数据
            print("📝 创建测试音频数据...")
            audio_data = self.create_test_audio_data("这是一个语音转录测试")
            
            print(f"📊 音频数据大小: {len(audio_data)} bytes")
            
            # 处理音频数据
            print("🔄 开始处理音频数据...")
            self.service.process_voice_data(
                audio_data=audio_data,
                user_id=user_id,
                interview_id=interview_id,
                chunk_id=1,
                is_final=True
            )
            
            # 等待处理完成
            print("⏳ 等待转录完成...")
            time.sleep(5)
            
            # 显示结果
            if self.results:
                print("✅ 转录测试完成!")
            else:
                print("⚠️  未收到转录结果（可能是提供商配置问题）")
            
            # 清理
            self.service.unregister_result_callback(user_id, interview_id)
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
        
        print()
    
    def test_multiple_chunks(self):
        """测试多块音频处理"""
        print("🧪 测试 2: 多块音频处理")
        print("-" * 50)
        
        try:
            if not self.service:
                self.service = get_voice_service(self.config)
            
            user_id = "demo_user_002"
            interview_id = "demo_interview_002"
            
            # 注册回调
            self.service.register_result_callback(user_id, interview_id, self.result_callback)
            
            # 发送多个音频块
            num_chunks = 3
            for i in range(num_chunks):
                print(f"📤 发送音频块 {i+1}/{num_chunks}")
                
                audio_data = self.create_test_audio_data(f"音频块{i+1}")
                is_final = (i == num_chunks - 1)
                
                self.service.process_voice_data(
                    audio_data=audio_data,
                    user_id=user_id,
                    interview_id=interview_id,
                    chunk_id=i+1,
                    is_final=is_final
                )
                
                time.sleep(1)
            
            # 等待处理完成
            print("⏳ 等待所有块处理完成...")
            time.sleep(8)
            
            print("✅ 多块音频测试完成!")
            
            # 清理
            self.service.unregister_result_callback(user_id, interview_id)
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
        
        print()
    
    def test_concurrent_users(self):
        """测试并发用户处理"""
        print("🧪 测试 3: 并发用户语音处理")
        print("-" * 50)
        
        try:
            if not self.service:
                self.service = get_voice_service(self.config)
            
            def simulate_user(user_num: int):
                """模拟单个用户"""
                user_id = f"demo_user_{user_num:03d}"
                interview_id = f"demo_interview_{user_num:03d}"
                
                # 注册回调
                self.service.register_result_callback(user_id, interview_id, self.result_callback)
                
                # 发送音频数据
                audio_data = self.create_test_audio_data(f"用户{user_num}的语音")
                
                self.service.process_voice_data(
                    audio_data=audio_data,
                    user_id=user_id,
                    interview_id=interview_id,
                    chunk_id=1,
                    is_final=True
                )
                
                time.sleep(2)  # 等待处理
                
                # 清理
                self.service.unregister_result_callback(user_id, interview_id)
            
            # 创建多个用户线程
            num_users = 3
            threads = []
            
            print(f"🚀 启动 {num_users} 个并发用户...")
            
            for i in range(num_users):
                thread = threading.Thread(target=simulate_user, args=(i+1,))
                threads.append(thread)
                thread.start()
            
            # 等待所有线程完成
            for thread in threads:
                thread.join()
            
            print("✅ 并发用户测试完成!")
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
        
        print()
    
    def test_service_stats(self):
        """测试服务统计信息"""
        print("🧪 测试 4: 服务统计信息")
        print("-" * 50)
        
        try:
            if not self.service:
                self.service = get_voice_service(self.config)
            
            stats = self.service.get_service_stats()
            
            print("📊 语音转录服务统计:")
            for key, value in stats.items():
                print(f"   • {key}: {value}")
            
            print("✅ 服务统计测试完成!")
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
        
        print()
    
    def run_comprehensive_demo(self):
        """运行完整演示"""
        try:
            self.print_header()
            self.print_config_info()
            
            self.demo_running = True
            
            # 运行各项测试
            self.test_basic_transcription()
            self.test_multiple_chunks()
            self.test_concurrent_users()
            self.test_service_stats()
            
            # 显示总结
            self.print_summary()
            
        except KeyboardInterrupt:
            print("\n🛑 演示被用户中断")
        except Exception as e:
            print(f"\n❌ 演示运行错误: {e}")
        finally:
            self.cleanup()
    
    def print_summary(self):
        """打印测试总结"""
        print("=" * 80)
        print("📋 测试总结")
        print("=" * 80)
        print(f"• 总转录结果数量: {len(self.results)}")
        
        if self.results:
            avg_confidence = sum(r.confidence for r in self.results) / len(self.results)
            avg_processing_time = sum(r.processing_time for r in self.results) / len(self.results)
            
            print(f"• 平均置信度: {avg_confidence:.2f}")
            print(f"• 平均处理时间: {avg_processing_time:.3f}秒")
            
            # 按提供商分组统计
            providers = set(r.language for r in self.results)
            print(f"• 使用的语言: {', '.join(providers)}")
        
        print()
        print("🎉 语音转录功能演示完成!")
        print("=" * 80)
    
    def cleanup(self):
        """清理资源"""
        print("🧹 清理资源...")
        
        if self.service:
            try:
                shutdown_voice_service()
                print("✅ 语音服务已关闭")
            except Exception as e:
                print(f"⚠️  清理语音服务时出错: {e}")
        
        self.demo_running = False

def main():
    """主函数"""
    demo = VoiceTranscriptionDemo()
    
    try:
        demo.run_comprehensive_demo()
    except Exception as e:
        print(f"程序运行错误: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 