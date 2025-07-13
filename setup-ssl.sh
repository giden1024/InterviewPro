#!/bin/bash

# SSL配置脚本 - InterviewPro
echo "🔒 开始配置SSL证书..."

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    echo "❌ 请使用sudo运行此脚本"
    exit 1
fi

# 更新系统包
echo "📦 更新系统包..."
apt update

# 安装nginx和certbot
echo "🔧 安装nginx和certbot..."
apt install -y nginx certbot python3-certbot-nginx openssl

# 停止nginx服务
systemctl stop nginx

# 创建自签名证书目录
mkdir -p /etc/ssl/private
mkdir -p /etc/ssl/certs

# 生成自签名证书（用于测试）
echo "🔐 生成自签名SSL证书..."
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/ssl/private/selfsigned.key \
    -out /etc/ssl/certs/selfsigned.crt \
    -subj "/C=US/ST=State/L=City/O=Organization/OU=OrgUnit/CN=3.14.247.189"

# 设置证书权限
chmod 600 /etc/ssl/private/selfsigned.key
chmod 644 /etc/ssl/certs/selfsigned.crt

# 备份默认nginx配置
cp /etc/nginx/sites-available/default /etc/nginx/sites-available/default.backup

# 复制新的nginx配置
cp /home/ubuntu/InterviewPro/nginx-ssl.conf /etc/nginx/sites-available/interviewpro

# 创建软链接
ln -sf /etc/nginx/sites-available/interviewpro /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# 测试nginx配置
echo "🧪 测试nginx配置..."
nginx -t

if [ $? -eq 0 ]; then
    echo "✅ nginx配置测试通过"
    
    # 启动nginx
    systemctl start nginx
    systemctl enable nginx
    
    # 修改docker-compose配置以使用nginx代理
    echo "🔄 更新Docker配置..."
    cd /home/ubuntu/InterviewPro
    
    # 停止当前容器
    docker-compose -f docker-compose.prod.yml down
    
    # 修改端口映射（nginx将处理80和443端口）
    sed -i 's/80:80/3000:80/g' docker-compose.prod.yml
    
    # 重新启动容器
    docker-compose -f docker-compose.prod.yml up -d
    
    echo "✅ SSL配置完成！"
    echo ""
    echo "📋 配置信息："
    echo "   HTTP:  http://3.14.247.189 (自动重定向到HTTPS)"
    echo "   HTTPS: https://3.14.247.189"
    echo "   证书类型: 自签名证书（浏览器会显示不安全警告）"
    echo ""
    echo "🔔 注意事项："
    echo "   1. 当前使用的是自签名证书，浏览器会显示安全警告"
    echo "   2. 如果您有域名，可以使用Let's Encrypt获取免费的受信任证书"
    echo "   3. 要获取受信任证书，请运行: sudo certbot --nginx -d yourdomain.com"
    echo ""
    echo "🔍 检查服务状态："
    systemctl status nginx
    
else
    echo "❌ nginx配置测试失败，请检查配置文件"
    exit 1
fi 