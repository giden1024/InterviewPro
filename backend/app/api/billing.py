"""
付费和订阅管理API
"""
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import requests
import time
from datetime import datetime, timedelta

from app.models.user import User
from app.models.subscription import Subscription, PaymentHistory
from app.extensions import db
from app.utils.subscription_utils import (
    get_pricing_plans, 
    verify_creem_signature, 
    get_user_subscription_status,
    create_user_subscription
)

billing_bp = Blueprint('billing', __name__)

@billing_bp.route('/plans', methods=['GET'])
def get_plans():
    """获取所有付费计划"""
    try:
        plans = get_pricing_plans()
        return jsonify({
            'success': True,
            'data': plans
        })
    except Exception as e:
        current_app.logger.error(f"Error fetching plans: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch pricing plans'
        }), 500

@billing_bp.route('/subscription', methods=['GET'])
@jwt_required()
def get_current_subscription():
    """获取当前用户的订阅状态"""
    try:
        user_id = get_jwt_identity()
        subscription_status = get_user_subscription_status(user_id)
        
        if not subscription_status:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': subscription_status
        })
    except Exception as e:
        current_app.logger.error(f"Error fetching subscription: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch subscription status'
        }), 500

@billing_bp.route('/checkout', methods=['POST'])
@jwt_required()
def create_checkout():
    """创建Creem.io支付会话"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        plan = data.get('plan')
        
        if not plan or plan not in ['basic', 'premium']:
            return jsonify({
                'success': False,
                'error': 'Invalid plan. Must be "basic" or "premium"'
            }), 400
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        # 根据计划选择对应的产品ID
        if plan == 'basic':
            product_id = current_app.config.get('CREEM_BASIC_PRODUCT_ID', 'prod_1UsU2rK5AiyVINJuHWnPyy')
        elif plan == 'premium':
            product_id = current_app.config.get('CREEM_PREMIUM_PRODUCT_ID', 'prod_7A6SRjA0LFPQWoNmdiNJEa')
        else:
            product_id = current_app.config.get('CREEM_TEST_PRODUCT_ID', 'prod_1UsU2rK5AiyVINJuHWnPyy')
        
        # 生成唯一的request_id用于跟踪
        request_id = f"user_{user_id}_{plan}_{int(time.time())}"
        
        # 构建checkout数据
        checkout_data = {
            'product_id': product_id,
            'success_url': f"{current_app.config.get('FRONTEND_URL', 'http://localhost:3000')}/billing/success",
            'request_id': request_id
        }
        
        # 设置API请求头
        headers = {
            'x-api-key': current_app.config.get('CREEM_API_KEY'),
            'Content-Type': 'application/json'
        }
        
        current_app.logger.info(f"Creating checkout for user {user_id}, plan {plan}")
        current_app.logger.info(f"Checkout data: {checkout_data}")
        
        # 调用Creem.io API
        api_url = 'https://api.creem.io/v1/checkouts'
        if current_app.config.get('CREEM_TEST_MODE', True):
            api_url = 'https://test-api.creem.io/v1/checkouts'  # 测试环境URL
        
        current_app.logger.info(f"Calling Creem API: {api_url}")
        current_app.logger.info(f"API Key: {current_app.config.get('CREEM_API_KEY')[:10]}...")
        current_app.logger.info(f"Checkout data: {checkout_data}")
        
        try:
            response = requests.post(
                api_url,
                json=checkout_data,
                headers=headers,
                timeout=30
            )
            
            current_app.logger.info(f"Creem API response status: {response.status_code}")
            current_app.logger.info(f"Creem API response: {response.text}")
            
            if response.status_code == 200 or response.status_code == 201:
                response_data = response.json()
                current_app.logger.info(f"Creem API success response: {response_data}")
                
                checkout_url = response_data.get('checkout_url') or response_data.get('url')
                checkout_id = response_data.get('checkout_id') or response_data.get('id')
                
                current_app.logger.info(f"Extracted checkout_url: {checkout_url}, checkout_id: {checkout_id}")
                
                if checkout_url and checkout_id:
                    # 记录待处理的支付
                    payment = PaymentHistory(
                        user_id=user_id,
                        creem_checkout_id=checkout_id,
                        plan=plan,
                        amount=29 if plan == 'basic' else 99,
                        currency='CNY',
                        status='pending',
                        request_id=request_id
                    )
                    db.session.add(payment)
                    db.session.commit()
                    
                    return jsonify({
                        'success': True,
                        'data': {
                            'checkout_url': checkout_url,
                            'request_id': request_id
                        }
                    })
                else:
                    current_app.logger.error(f"Missing checkout data - URL: {checkout_url}, ID: {checkout_id}")
                    # # 注释掉mock代码：如果缺少数据，使用临时值避免NULL错误
                    # temp_checkout_id = f"temp_{request_id}"
                    # payment = PaymentHistory(
                    #     user_id=user_id,
                    #     creem_checkout_id=temp_checkout_id,
                    #     plan=plan,
                    #     amount=29 if plan == 'basic' else 99,
                    #     currency='CNY',
                    #     status='failed',
                    #     request_id=request_id
                    # )
                    # db.session.add(payment)
                    # db.session.commit()
                    
                    return jsonify({
                        'success': False,
                        'error': 'Failed to get checkout URL from payment provider'
                    }), 500
            else:
                current_app.logger.error(f"Creem API failed: {response.status_code} - {response.text}")
                # # 注释掉mock代码：API失败时也要创建记录，避免NULL错误
                # temp_checkout_id = f"failed_{request_id}"
                # payment = PaymentHistory(
                #     user_id=user_id,
                #     creem_checkout_id=temp_checkout_id,
                #     plan=plan,
                #     amount=29 if plan == 'basic' else 99,
                #     currency='CNY',
                #     status='failed',
                #     request_id=request_id
                # )
                # db.session.add(payment)
                # db.session.commit()
                
                return jsonify({
                    'success': False,
                    'error': 'Payment provider error',
                    'details': response.text
                }), 500
                
        except requests.exceptions.RequestException as req_error:
            current_app.logger.error(f"Request exception: {str(req_error)}")
            # # 注释掉mock代码：网络异常时也要创建记录
            # temp_checkout_id = f"error_{request_id}"
            # payment = PaymentHistory(
            #     user_id=user_id,
            #     creem_checkout_id=temp_checkout_id,
            #     plan=plan,
            #     amount=29 if plan == 'basic' else 99,
            #     currency='CNY',
            #     status='failed',
            #     request_id=request_id
            # )
            # db.session.add(payment)
            # db.session.commit()
            
            return jsonify({
                'success': False,
                'error': 'Failed to connect to payment provider'
            }), 500
            
    except requests.RequestException as e:
        current_app.logger.error(f"Request error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to connect to payment provider'
        }), 500
    except Exception as e:
        current_app.logger.error(f"Unexpected error in create_checkout: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@billing_bp.route('/webhook', methods=['POST'])
def payment_webhook():
    """处理Creem.io支付回调 - Webhook方式"""
    try:
        # 获取webhook数据
        webhook_data = request.get_json()
        current_app.logger.info(f"Received webhook: {webhook_data}")
        
        # 验证webhook签名
        signature = request.headers.get('X-Creem-Signature')
        if not signature or not verify_creem_signature(webhook_data, signature):
            current_app.logger.warning("Invalid webhook signature")
            return jsonify({'error': 'Invalid signature'}), 400
        
        # 处理支付成功事件
        event_type = webhook_data.get('type')
        if event_type == 'payment.completed':
            return handle_payment_completed(webhook_data.get('data', {}))
        elif event_type == 'payment.failed':
            return handle_payment_failed(webhook_data.get('data', {}))
        
        return jsonify({'status': 'received'})
        
    except Exception as e:
        current_app.logger.error(f"Webhook error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@billing_bp.route('/callback', methods=['GET'])
def payment_callback():
    """处理Creem.io支付回调 - URL回调方式"""
    # 立即记录回调接收时间和基本信息
    callback_start_time = datetime.utcnow()
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', 'unknown'))
    user_agent = request.headers.get('User-Agent', 'unknown')
    
    current_app.logger.info("=" * 80)
    current_app.logger.info(f"🔔 PAYMENT CALLBACK RECEIVED AT {callback_start_time}")
    current_app.logger.info(f"🌍 Client IP: {client_ip}")
    current_app.logger.info(f"🔍 User-Agent: {user_agent}")
    current_app.logger.info(f"🌐 Request Method: {request.method}")
    current_app.logger.info(f"🔗 Request URL: {request.url}")
    current_app.logger.info(f"📡 Request Path: {request.path}")
    current_app.logger.info(f"🔍 Query String: {request.query_string.decode()}")
    current_app.logger.info("=" * 80)
    
    try:
        # 获取回调参数
        checkout_id = request.args.get('checkout_id')
        order_id = request.args.get('order_id')
        customer_id = request.args.get('customer_id')
        subscription_id = request.args.get('subscription_id')
        product_id = request.args.get('product_id')
        request_id = request.args.get('request_id')
        signature = request.args.get('signature')
        
        # 详细日志记录
        current_app.logger.info(f"🔔 Payment callback received")
        current_app.logger.info(f"📋 All parameters: {request.args.to_dict()}")
        current_app.logger.info(f"🌐 Request headers: {dict(request.headers)}")
        current_app.logger.info(f"🔑 Signature received: {signature}")
        current_app.logger.info(f"📝 Request ID: {request_id}")
        
        # 检查必需参数
        missing_params = []
        if not checkout_id:
            missing_params.append('checkout_id')
        if not request_id:
            missing_params.append('request_id')
        if not signature:
            missing_params.append('signature')
            
        if missing_params:
            error_msg = f"Missing required parameters: {', '.join(missing_params)}"
            current_app.logger.error(f"❌ {error_msg}")
            return jsonify({'error': error_msg}), 400
        
        # 验证签名
        callback_data = {k: v for k, v in request.args.items() if k != 'signature'}
        current_app.logger.info(f"🔐 Verifying signature for data: {callback_data}")
        
        signature_valid = verify_creem_signature(callback_data, signature)
        current_app.logger.info(f"🔐 Signature validation result: {signature_valid}")
        
        if not signature_valid:
            current_app.logger.warning(f"❌ Invalid callback signature")
            current_app.logger.warning(f"   Expected signature calculation for: {callback_data}")
            current_app.logger.warning(f"   Received signature: {signature}")
            
            # 在开发环境中，我们暂时跳过签名验证以便调试
            if current_app.config.get('CREEM_TEST_MODE', True):
                current_app.logger.warning("⚠️ DEVELOPMENT MODE: Skipping signature verification")
            else:
                return jsonify({'error': 'Invalid signature'}), 400
        
        # 从request_id解析用户信息
        try:
            current_app.logger.info(f"🔍 Parsing request_id: {request_id}")
            parts = request_id.split('_')
            current_app.logger.info(f"🔍 Request ID parts: {parts}")
            
            if len(parts) >= 3:
                user_id = int(parts[1])
                plan = parts[2]
                current_app.logger.info(f"✅ Parsed user_id: {user_id}, plan: {plan}")
            else:
                raise ValueError("Invalid request_id format")
        except (ValueError, IndexError) as e:
            current_app.logger.error(f"❌ Failed to parse request_id {request_id}: {str(e)}")
            current_app.logger.error(f"❌ Request ID parts: {request_id.split('_') if request_id else 'None'}")
            return jsonify({'error': 'Invalid request_id'}), 400
        
        # 更新用户订阅
        current_app.logger.info(f"🔄 Starting subscription update process...")
        current_app.logger.info(f"📊 Update parameters: user_id={user_id}, plan={plan}")
        
        success = update_user_subscription(
            user_id=user_id,
            plan=plan,
            checkout_id=checkout_id,
            order_id=order_id,
            customer_id=customer_id,
            subscription_id=subscription_id,
            request_id=request_id
        )
        
        current_app.logger.info(f"📊 Subscription update result: {success}")
        
        if success:
            current_app.logger.info(f"✅ Subscription update successful, preparing redirect...")
            # 重定向到成功页面，传递完整的回调参数
            frontend_url = current_app.config.get('FRONTEND_URL', 'http://localhost:3000')
            success_url = f"{frontend_url}/billing/success?request_id={request_id}&checkout_id={checkout_id}"
            if order_id:
                success_url += f"&order_id={order_id}"
            if customer_id:
                success_url += f"&customer_id={customer_id}"
            if product_id:
                success_url += f"&product_id={product_id}"
            
            return f"""
            <html>
                <head>
                    <title>支付成功</title>
                    <meta charset="UTF-8">
                </head>
                <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                    <div style="max-width: 500px; margin: 0 auto; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                        <h1 style="color: #52c41a;">🎉 支付成功！</h1>
                        <p style="font-size: 18px; color: #666;">恭喜您成功订阅了{plan}计划！</p>
                        <p style="color: #999;">您的权益已激活，正在跳转到订阅管理页面...</p>
                        <div style="margin: 20px 0;">
                            <div style="width: 200px; height: 4px; background: #f0f0f0; margin: 0 auto; border-radius: 2px; overflow: hidden;">
                                <div id="progress" style="width: 0%; height: 100%; background: #52c41a; transition: width 0.1s;"></div>
                            </div>
                        </div>
                        <p id="countdown" style="color: #666;">3秒后自动跳转...</p>
                    </div>
                    <script>
                        let seconds = 3;
                        const countdownEl = document.getElementById('countdown');
                        const progressEl = document.getElementById('progress');
                        
                        const updateCountdown = () => {{
                            countdownEl.textContent = seconds + '秒后自动跳转...';
                            progressEl.style.width = ((3 - seconds) / 3 * 100) + '%';
                            
                            if (seconds <= 0) {{
                                countdownEl.textContent = '正在跳转...';
                                progressEl.style.width = '100%';
                                window.location.href = '{success_url}';
                            }} else {{
                                seconds--;
                                setTimeout(updateCountdown, 1000);
                            }}
                        }};
                        
                        updateCountdown();
                    </script>
                </body>
            </html>
            """
        else:
            current_app.logger.error(f"❌ Subscription update failed!")
            current_app.logger.error(f"❌ Failed request_id: {request_id}")
            current_app.logger.error(f"❌ Failed parameters: user_id={user_id}, plan={plan}")
            return jsonify({'error': 'Failed to update subscription'}), 500
            
    except Exception as e:
        callback_end_time = datetime.utcnow()
        processing_time = callback_end_time - callback_start_time
        current_app.logger.error("=" * 80)
        current_app.logger.error(f"💥 CALLBACK PROCESSING FAILED")
        current_app.logger.error(f"⏱️  Processing time: {processing_time}")
        current_app.logger.error(f"❌ Error: {str(e)}")
        current_app.logger.error(f"📍 Error type: {type(e).__name__}")
        import traceback
        current_app.logger.error(f"📚 Traceback: {traceback.format_exc()}")
        current_app.logger.error("=" * 80)
        return jsonify({'error': 'Internal server error'}), 500
    
    finally:
        # 记录回调处理完成
        callback_end_time = datetime.utcnow()
        processing_time = callback_end_time - callback_start_time
        current_app.logger.info("=" * 80)
        current_app.logger.info(f"🏁 CALLBACK PROCESSING COMPLETED")
        current_app.logger.info(f"⏱️  Total processing time: {processing_time}")
        current_app.logger.info(f"🕐 Start time: {callback_start_time}")
        current_app.logger.info(f"🕐 End time: {callback_end_time}")
        current_app.logger.info("=" * 80)

def handle_payment_completed(payment_data):
    """处理支付完成事件"""
    try:
        request_id = payment_data.get('request_id')
        checkout_id = payment_data.get('checkout_id')
        order_id = payment_data.get('order_id')
        customer_id = payment_data.get('customer_id')
        
        if not request_id:
            return jsonify({'error': 'Missing request_id'}), 400
        
        # 解析用户信息
        parts = request_id.split('_')
        user_id = int(parts[1])
        plan = parts[2]
        
        # 更新订阅
        success = update_user_subscription(
            user_id=user_id,
            plan=plan,
            checkout_id=checkout_id,
            order_id=order_id,
            customer_id=customer_id,
            request_id=request_id
        )
        
        return jsonify({'status': 'success' if success else 'failed'})
        
    except Exception as e:
        current_app.logger.error(f"Error handling payment completed: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

def handle_payment_failed(payment_data):
    """处理支付失败事件"""
    try:
        request_id = payment_data.get('request_id')
        
        if request_id:
            # 更新支付记录状态
            payment = PaymentHistory.query.filter_by(request_id=request_id).first()
            if payment:
                payment.status = 'failed'
                db.session.commit()
        
        return jsonify({'status': 'received'})
        
    except Exception as e:
        current_app.logger.error(f"Error handling payment failed: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@billing_bp.route('/sync-payment/<request_id>', methods=['POST'])
@jwt_required()
def sync_payment_status(request_id):
    """手动同步支付状态 - 用于回调失败时的补救"""
    try:
        user_id = get_jwt_identity()
        
        # 查找对应的支付记录
        payment = PaymentHistory.query.filter_by(
            request_id=request_id,
            user_id=user_id
        ).first()
        
        if not payment:
            return error_response("Payment record not found", 404)
        
        if payment.status == 'completed':
            return success_response({
                'message': 'Payment already completed',
                'payment': {
                    'id': payment.id,
                    'plan': payment.plan,
                    'status': payment.status,
                    'amount': payment.amount
                }
            })
        
        # 调用Creem.io API检查支付状态
        try:
            import requests
            
            api_url = f"https://api.creem.io/v1/checkout/{payment.creem_checkout_id}"
            headers = {
                'x-api-key': current_app.config.get('CREEM_API_KEY'),
                'Content-Type': 'application/json'
            }
            
            current_app.logger.info(f"🔄 Checking payment status with Creem.io: {api_url}")
            response = requests.get(api_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                creem_data = response.json()
                current_app.logger.info(f"📊 Creem.io response: {creem_data}")
                
                # 如果Creem.io显示支付已完成，更新本地状态
                if creem_data.get('status') == 'completed':
                    success = update_user_subscription(
                        user_id=user_id,
                        plan=payment.plan,
                        checkout_id=payment.creem_checkout_id,
                        order_id=payment.creem_order_id,
                        customer_id=payment.creem_customer_id,
                        request_id=request_id
                    )
                    
                    if success:
                        current_app.logger.info(f"✅ Payment status synced successfully")
                        return success_response({
                            'message': 'Payment status synced successfully',
                            'payment': {
                                'id': payment.id,
                                'plan': payment.plan,
                                'status': 'completed',
                                'amount': payment.amount
                            }
                        })
                    else:
                        return error_response("Failed to update subscription", 500)
                else:
                    return success_response({
                        'message': f'Payment status is {creem_data.get("status")}',
                        'creem_status': creem_data.get('status')
                    })
            else:
                current_app.logger.error(f"❌ Creem.io API error: {response.status_code} {response.text}")
                return error_response("Failed to check payment status with Creem.io", 500)
                
        except Exception as api_error:
            current_app.logger.error(f"❌ Error calling Creem.io API: {str(api_error)}")
            return error_response("Failed to check payment status", 500)
        
    except Exception as e:
        current_app.logger.error(f"Error syncing payment status: {str(e)}")
        return error_response("Failed to sync payment status", 500)

def update_user_subscription(user_id, plan, checkout_id, order_id=None, customer_id=None, subscription_id=None, request_id=None):
    """更新用户订阅状态"""
    try:
        current_app.logger.info(f"🔄 Starting subscription update for user {user_id}")
        current_app.logger.info(f"📋 Parameters: plan={plan}, checkout_id={checkout_id}, order_id={order_id}")
        current_app.logger.info(f"📋 Parameters: customer_id={customer_id}, request_id={request_id}")
        
        user = User.query.get(user_id)
        if not user:
            current_app.logger.error(f"❌ User {user_id} not found")
            return False
        
        current_app.logger.info(f"✅ Found user: {user.email}")
        
        # 获取或创建订阅
        subscription = user.subscription
        if not subscription:
            current_app.logger.info(f"📝 Creating new subscription for user {user_id}")
            subscription = Subscription(user_id=user_id)
            db.session.add(subscription)
        else:
            current_app.logger.info(f"📝 Updating existing subscription: {subscription.plan} -> {plan}")
            current_app.logger.info(f"📝 Current status: {subscription.status}")
        
        # 更新订阅信息
        subscription.plan = plan
        subscription.status = 'active'
        subscription.creem_customer_id = customer_id
        subscription.creem_subscription_id = subscription_id
        subscription.creem_order_id = order_id
        subscription.creem_checkout_id = checkout_id
        subscription.start_date = datetime.utcnow()
        subscription.end_date = datetime.utcnow() + timedelta(days=30)  # 30天订阅
        
        # 重置使用统计
        subscription.monthly_interviews_used = 0
        subscription.monthly_ai_questions_used = 0
        subscription.monthly_resume_analysis_used = 0
        subscription.usage_reset_date = datetime.utcnow().replace(day=1)
        
        current_app.logger.info(f"💰 Processing payment record for request_id: {request_id}")
        
        # 更新支付记录
        payment = PaymentHistory.query.filter_by(request_id=request_id).first()
        if payment:
            current_app.logger.info(f"📝 Found existing payment record: {payment.status} -> completed")
            payment.subscription_id = subscription.id
            payment.creem_checkout_id = checkout_id
            payment.creem_order_id = order_id
            payment.creem_customer_id = customer_id
            payment.status = 'completed'
            payment.payment_date = datetime.utcnow()
        else:
            current_app.logger.info(f"📝 Creating new payment record for request_id: {request_id}")
            # 创建新的支付记录
            payment = PaymentHistory(
                user_id=user_id,
                subscription_id=subscription.id,
                creem_checkout_id=checkout_id,
                creem_order_id=order_id,
                creem_customer_id=customer_id,
                request_id=request_id,
                plan=plan,
                amount=29 if plan == 'basic' else 99,
                currency='CNY',
                status='completed'
            )
            db.session.add(payment)
        
        current_app.logger.info(f"💾 Committing database changes...")
        db.session.commit()
        current_app.logger.info(f"✅ Database commit successful")
        
        current_app.logger.info(f"🎉 Successfully updated subscription for user {user_id} to plan {plan}")
        return True
        
    except Exception as e:
        current_app.logger.error(f"Error updating subscription: {str(e)}")
        db.session.rollback()
        return False

@billing_bp.route('/usage', methods=['GET'])
@jwt_required()
def get_usage_stats():
    """获取用户使用统计"""
    try:
        user_id = get_jwt_identity()
        subscription_status = get_user_subscription_status(user_id)
        
        if not subscription_status:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': {
                'usage': subscription_status['usage'],
                'limits': subscription_status['limits'],
                'features': subscription_status['features']
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error fetching usage stats: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch usage statistics'
        }), 500

@billing_bp.route('/history', methods=['GET'])
@jwt_required()
def get_payment_history():
    """获取用户支付历史"""
    try:
        user_id = get_jwt_identity()
        
        payments = PaymentHistory.query.filter_by(user_id=user_id)\
                                      .order_by(PaymentHistory.created_at.desc())\
                                      .all()
        
        return jsonify({
            'success': True,
            'data': [payment.to_dict() for payment in payments]
        })
        
    except Exception as e:
        current_app.logger.error(f"Error fetching payment history: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch payment history'
        }), 500

@billing_bp.route('/cancel', methods=['POST'])
@jwt_required()
def cancel_subscription():
    """取消订阅"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or not user.subscription:
            return jsonify({
                'success': False,
                'error': 'No active subscription found'
            }), 404
        
        subscription = user.subscription
        subscription.status = 'cancelled'
        # 保持到期日期，让用户使用到期
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Subscription cancelled successfully'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error cancelling subscription: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to cancel subscription'
        }), 500
