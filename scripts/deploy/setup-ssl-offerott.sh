#!/bin/bash

echo "=== 为 offerott.com 配置 Let's Encrypt SSL证书 ==="

# 1. 获取SSL证书
echo "1. 获取SSL证书..."
sudo certbot certonly --standalone \
  --email admin@offerott.com \
  --agree-tos \
  --no-eff-email \
  -d offerott.com \
  -d www.offerott.com \
  --non-interactive

# 检查证书是否成功获取
if [ -f "/etc/letsencrypt/live/offerott.com/fullchain.pem" ]; then
    echo "✅ SSL证书获取成功"
else
    echo "❌ SSL证书获取失败"
    exit 1
fi

# 2. 备份现有nginx配置
echo "2. 备份现有nginx配置..."
sudo cp /etc/nginx/sites-available/interviewpro /etc/nginx/sites-available/interviewpro.backup.$(date +%Y%m%d_%H%M%S)

# 3. 更新nginx配置
echo "3. 更新nginx配置..."
sudo tee /etc/nginx/sites-available/interviewpro << 'NGINXCONF'
server {
    listen 80;
    server_name offerott.com www.offerott.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name offerott.com www.offerott.com;

    # Let's Encrypt SSL证书
    ssl_certificate /etc/letsencrypt/live/offerott.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/offerott.com/privkey.pem;

    # SSL安全配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-CHACHA20-POLY1305:ECDHE-RSA-AES128-SHA256:ECDHE-RSA-AES256-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # 安全头
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # 前端代理
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;
        
        # WebSocket支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # API代理
    location /api/ {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;
        
        # CORS支持
        add_header Access-Control-Allow-Origin "https://offerott.com" always;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
        add_header Access-Control-Allow-Headers "Content-Type, Authorization, X-Requested-With" always;
        add_header Access-Control-Allow-Credentials "true" always;
        
        if ($request_method = 'OPTIONS') {
            add_header Access-Control-Allow-Origin "https://offerott.com";
            add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";
            add_header Access-Control-Allow-Headers "Content-Type, Authorization, X-Requested-With";
            add_header Access-Control-Allow-Credentials "true";
            add_header Content-Length 0;
            add_header Content-Type text/plain;
            return 204;
        }
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # WebSocket代理
    location /ws/ {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 静态文件缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        expires 1y;
        add_header Cache-Control "public, immutable";
        add_header Vary Accept-Encoding;
    }

    # 文件上传限制
    client_max_body_size 10M;
    client_body_timeout 60s;
    client_header_timeout 60s;
    
    # Gzip压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;
    
    # 日志
    access_log /var/log/nginx/offerott.com.access.log;
    error_log /var/log/nginx/offerott.com.error.log;
}
NGINXCONF

# 4. 测试nginx配置
echo "4. 测试nginx配置..."
sudo nginx -t

if [ $? -eq 0 ]; then
    echo "✅ nginx配置测试通过"
else
    echo "❌ nginx配置测试失败"
    exit 1
fi

# 5. 重启nginx
echo "5. 重启nginx..."
sudo systemctl restart nginx

# 6. 检查nginx状态
echo "6. 检查nginx状态..."
sudo systemctl status nginx --no-pager

# 7. 设置自动续期
echo "7. 设置SSL证书自动续期..."
(crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet && systemctl reload nginx") | crontab -

echo ""
echo "=== SSL证书配置完成 ==="
echo "✅ 域名: https://offerott.com"
echo "✅ 域名: https://www.offerott.com" 
echo "✅ SSL证书: Let's Encrypt (受信任)"
echo "✅ 自动续期: 已设置"
echo ""
echo "现在可以通过 https://offerott.com 安全访问网站，不会再显示安全警告！" 