from datetime import datetime, timedelta
from decimal import Decimal
from app.extensions import db

class Subscription(db.Model):
    """用户订阅模型"""
    __tablename__ = 'subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    plan = db.Column(db.String(20), nullable=False, default='free')  # free, basic, premium, enterprise
    status = db.Column(db.String(20), nullable=False, default='active')  # active, cancelled, expired
    
    # Creem.io 相关字段
    creem_customer_id = db.Column(db.String(100))
    creem_subscription_id = db.Column(db.String(100))
    creem_order_id = db.Column(db.String(100))
    creem_checkout_id = db.Column(db.String(100))
    
    # 订阅时间
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_date = db.Column(db.DateTime)
    trial_end_date = db.Column(db.DateTime)
    
    # 使用统计
    monthly_interviews_used = db.Column(db.Integer, default=0)
    monthly_ai_questions_used = db.Column(db.Integer, default=0)
    monthly_resume_analysis_used = db.Column(db.Integer, default=0)
    usage_reset_date = db.Column(db.DateTime, default=lambda: datetime.utcnow().replace(day=1))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = db.relationship('User', backref=db.backref('subscription', uselist=False))
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'plan': self.plan,
            'status': self.status,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'monthly_interviews_used': self.monthly_interviews_used,
            'monthly_ai_questions_used': self.monthly_ai_questions_used,
            'monthly_resume_analysis_used': self.monthly_resume_analysis_used,
            'usage_reset_date': self.usage_reset_date.isoformat() if self.usage_reset_date else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def reset_monthly_usage(self):
        """重置月度使用统计"""
        self.monthly_interviews_used = 0
        self.monthly_ai_questions_used = 0
        self.monthly_resume_analysis_used = 0
        self.usage_reset_date = datetime.utcnow().replace(day=1)
        db.session.commit()
    
    def is_expired(self):
        """检查订阅是否过期"""
        if not self.end_date:
            return False
        return self.end_date < datetime.utcnow()
    
    def get_plan_limits(self):
        """获取当前计划的限制"""
        limits = {
            'free': {
                'interviews': 3,
                'ai_questions': 10,
                'resume_analysis': 1,
                'report_history': 7,
                'voice_interview': False,
                'custom_questions': False,
                'advanced_analysis': False
            },
            'basic': {
                'interviews': 20,
                'ai_questions': 100,
                'resume_analysis': 5,
                'report_history': 30,
                'voice_interview': True,
                'custom_questions': False,
                'advanced_analysis': False
            },
            'premium': {
                'interviews': -1,  # 无限
                'ai_questions': -1,
                'resume_analysis': -1,
                'report_history': 365,
                'voice_interview': True,
                'custom_questions': True,
                'advanced_analysis': True
            }
        }
        return limits.get(self.plan, limits['free'])
    
    def can_use_feature(self, feature_type):
        """检查是否可以使用某个功能"""
        if self.is_expired():
            return False
            
        limits = self.get_plan_limits()
        
        # 检查功能是否在计划中
        if feature_type in ['voice_interview', 'custom_questions', 'advanced_analysis']:
            return limits.get(feature_type, False)
        
        # 检查使用次数限制
        if feature_type == 'interviews':
            limit = limits['interviews']
            if limit == -1:
                return True
            return self.monthly_interviews_used < limit
            
        elif feature_type == 'ai_questions':
            limit = limits['ai_questions']
            if limit == -1:
                return True
            return self.monthly_ai_questions_used < limit
            
        elif feature_type == 'resume_analysis':
            limit = limits['resume_analysis']
            if limit == -1:
                return True
            return self.monthly_resume_analysis_used < limit
        
        return False
    
    def increment_usage(self, usage_type):
        """增加使用次数"""
        if usage_type == 'interviews':
            self.monthly_interviews_used += 1
        elif usage_type == 'ai_questions':
            self.monthly_ai_questions_used += 1
        elif usage_type == 'resume_analysis':
            self.monthly_resume_analysis_used += 1
        
        db.session.commit()

class PaymentHistory(db.Model):
    """支付历史记录"""
    __tablename__ = 'payment_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subscription_id = db.Column(db.Integer, db.ForeignKey('subscriptions.id'))
    
    # Creem.io 支付信息
    creem_checkout_id = db.Column(db.String(100), nullable=True)
    creem_order_id = db.Column(db.String(100))
    creem_customer_id = db.Column(db.String(100))
    request_id = db.Column(db.String(200))
    
    # 支付详情
    plan = db.Column(db.String(20), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), default='CNY')
    status = db.Column(db.String(20), nullable=False)  # pending, completed, failed, refunded
    
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    user = db.relationship('User', backref='payment_history')
    subscription = db.relationship('Subscription', backref='payment_history')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'plan': self.plan,
            'amount': float(self.amount),
            'currency': self.currency,
            'status': self.status,
            'payment_date': self.payment_date.isoformat(),
            'created_at': self.created_at.isoformat()
        }
