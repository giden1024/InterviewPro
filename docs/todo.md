# myy记录文档

第一优先级（1-2周内）：
修复认证API的小问题
实现简历上传和解析功能
集成DeepSeek AI问题生成
第二优先级（2-4周内）：
完善面试会话管理
实现语音转文本功能
开始前端界面开发



后端功能完成之后，开始在 cursor 中添加mcp。
并且使用 browsertools 以及 gomaster

确认如何安装browser tools
https://zhuanlan.zhihu.com/p/1901976336110708019



20250826
订阅功能

1. 升级时间问题
✅ 是的，会员开始时间从升级当天开始
从代码中可以看到：
Apply
30天后到期
具体流程：
用户升级成功 → 立即设置 start_date 为当前时间
订阅期限：30天（固定）
精确到秒级别的开始时间
2. 自动扣费问题
⚠️ 当前实现是一次性支付，不会自动扣费
当前机制：
每次支付都是独立的一次性交易
30天后到期，需要用户手动续费
没有自动续费功能
Creem.io的能力：
✅ 支持一次性支付（当前使用）
✅ 支持订阅模式（可配置自动续费）
🔧 当前实现的特点
✅ 已实现功能
即时生效：支付成功后立即激活
精确计时：从升级当天开始计算
固定周期：30天订阅期
状态管理：active/expired状态切换
使用统计重置：升级时清零计数器
⚠️ 当前限制
手动续费：到期后需要用户主动续费
无过期检查：没有自动检查过期订阅的定时任务
无提醒机制：不会提前通知用户续费






# 查询权益消耗数量
SELECT user_id, plan, monthly_interviews_used, monthly_ai_questions_used, monthly_resume_analysis_used, updated_at 
FROM subscriptions 
WHERE user_id = (SELECT id FROM users WHERE email = '393893095@qq.com');



# 权益验证




# 对外暴露
https://dashboard.ngrok.com/signup

6VMX9344QJ
YW3B8Q5FV4
5Q5MMJ4U89
ZP2ABYZB2A
G6UC7FRWZQ
VD5TNJHPDW
F8EDKC3NMV
PBNKATTXP4
HVFDSGGJMW
T4NXJCTKEK

ngrok config add-authtoken 31oqYYjF26jp67jkyxopKYKkGLS_74iwb2ecxYTNui2gcuqUb