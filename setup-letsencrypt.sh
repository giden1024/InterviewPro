#!/bin/bash

# Let's Encrypt SSL证书自动化配置脚本
# 在DNS生效后运行此脚本

echo "🔐 开始配置Let's Encrypt SSL证书..."

# 检查域名解析
echo "🌐 检查域名解析..."
DOMAIN_IP=$(nslookup offerott.com | grep -A1 "Non-authoritative answer:" | grep "Address:" | head -1 | awk '{print $2}')
SERVER_IP="47.110.144.20"

if [ "$DOMAIN_IP" != "$SERVER_IP" ]; then
    echo "❌ 域名尚未解析到服务器IP"
    echo "   当前解析: $DOMAIN_IP"
    echo "   服务器IP: $SERVER_IP"
    echo "   请等待DNS生效后再运行此脚本"
    exit 1
fi

echo "✅ 域名解析正确: $DOMAIN_IP"

# 安装Certbot
echo "📦 安装Certbot..."
apt update
apt install -y certbot python3-certbot-nginx

# 停止Nginx（Let's Encrypt需要使用80端口验证）
echo "⏸️ 临时停止Nginx..."
systemctl stop nginx

# 申请SSL证书
echo "🔒 申请Let's Encrypt SSL证书..."
certbot certonly --standalone \
    -d offerott.com \
    -d www.offerott.com \
    --non-interactive \
    --agree-tos \
    --email admin@offerott.com

# 检查证书申请结果
if [ $? -eq 0 ]; then
    echo "✅ SSL证书申请成功！"
    
    # 创建Let's Encrypt Nginx配置
    cat > /etc/nginx/sites-available/interviewpro-letsencrypt << 'EOF'
# HTTP服务器 - 重定向到HTTPS
server {
    listen 80;
    server_name offerott.com www.offerott.com 47.110.144.20;
    
    # Let's Encrypt验证
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    # 重定向所有其他HTTP请求到HTTPS
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS服务器
server {
    listen 443 ssl http2;
    server_name offerott.com www.offerott.com 47.110.144.20;

    # Let's Encrypt SSL证书
    ssl_certificate /etc/letsencrypt/live/offerott.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/offerott.com/privkey.pem;

    # SSL安全配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-SHA256:ECDHE-RSA-AES256-SHA384;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_stapling on;
    ssl_stapling_verify on;
    ssl_trusted_certificate /etc/letsencrypt/live/offerott.com/chain.pem;

    # 安全头
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # 前端静态文件
    location / {
        root /opt/interviewpro/frontend;
        index index.html;
        try_files $uri $uri/ /index.html;
        
        # 静态资源缓存
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # 后端API代理
    location /api/ {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $server_name;
        
        # CORS配置
        add_header Access-Control-Allow-Origin "https://$server_name" always;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
        add_header Access-Control-Allow-Headers "Origin, Content-Type, Accept, Authorization, X-Requested-With" always;
        add_header Access-Control-Allow-Credentials "true" always;
        
        if ($request_method = 'OPTIONS') {
            return 204;
        }
    }

    # WebSocket支持
    location /socket.io/ {
        proxy_pass http://127.0.0.1:5001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 文件上传大小限制
    client_max_body_size 10M;
    
    # Gzip压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/javascript
        application/xml+rss
        application/json
        image/svg+xml;
}
EOF

    # 启用Let's Encrypt配置
    ln -sf /etc/nginx/sites-available/interviewpro-letsencrypt /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/interviewpro-ssl
    
    # 测试配置
    nginx -t
    
    # 启动Nginx
    systemctl start nginx
    
    # 配置自动续期
    echo "🔄 配置证书自动续期..."
    (crontab -l 2>/dev/null || true; echo "0 12 * * * /usr/bin/certbot renew --quiet --nginx") | crontab -
    
    echo "🎉 Let's Encrypt SSL证书配置完成！"
    echo "🌐 现在可以通过以下地址访问："
    echo "  https://offerott.com"
    echo "  https://www.offerott.com"
    echo "  https://47.110.144.20"
    
else
    echo "❌ SSL证书申请失败"
    echo "请检查域名解析和网络连接"
    systemctl start nginx
    exit 1
fi

# 显示证书信息
echo "📋 证书信息："
certbot certificates

echo "✅ 配置完成！" 