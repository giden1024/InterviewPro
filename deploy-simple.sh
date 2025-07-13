#!/bin/bash

echo "🚀 开始简化部署InterviewPro..."

# 服务器信息
SERVER_IP="47.110.144.20"
SERVER_USER="root"
SERVER_PASS="Xmov1993!!"

echo "📦 准备项目文件..."

# 构建前端
echo "🔨 构建前端..."
cd frontend
npm install
npm run build
cd ..

echo "📤 上传项目到服务器..."

# 上传前端构建文件
sshpass -p "$SERVER_PASS" scp -r frontend/dist/ ${SERVER_USER}@${SERVER_IP}:/tmp/frontend-dist/

# 上传后端文件
sshpass -p "$SERVER_PASS" scp -r backend/ ${SERVER_USER}@${SERVER_IP}:/tmp/backend/

# 上传nginx配置
sshpass -p "$SERVER_PASS" scp nginx.simple.conf ${SERVER_USER}@${SERVER_IP}:/tmp/

echo "🔧 在服务器上配置环境..."

sshpass -p "$SERVER_PASS" ssh ${SERVER_USER}@${SERVER_IP} << 'EOF'
echo "🛠️ 安装必要软件..."

# 更新系统
apt update

# 安装Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt install -y nodejs

# 安装Python和pip
apt install -y python3 python3-pip python3-venv

# 安装Nginx
apt install -y nginx

# 安装PM2
npm install -g pm2

echo "📁 设置项目目录..."

# 创建项目目录
mkdir -p /opt/interviewpro/frontend
mkdir -p /opt/interviewpro/backend

# 移动文件
cp -r /tmp/frontend-dist/* /opt/interviewpro/frontend/
cp -r /tmp/backend/* /opt/interviewpro/backend/

# 设置后端
cd /opt/interviewpro/backend

# 创建Python虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装Python依赖
pip install -r requirements.txt

# 初始化数据库
python init_db.py

echo "⚙️ 配置Nginx..."

# 配置Nginx
cp /tmp/nginx.simple.conf /etc/nginx/sites-available/interviewpro
ln -sf /etc/nginx/sites-available/interviewpro /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# 测试Nginx配置
nginx -t

# 重启Nginx
systemctl restart nginx
systemctl enable nginx

echo "🚀 启动应用..."

# 启动后端服务
cd /opt/interviewpro/backend
source venv/bin/activate
pm2 start run_complete.py --name "interviewpro-backend" --interpreter python

# 设置PM2开机自启
pm2 startup
pm2 save

echo "✅ 部署完成！"
echo "🌐 访问地址: http://47.110.144.20"
echo "🔗 域名访问: http://offerott.com"

# 显示服务状态
pm2 status
systemctl status nginx
EOF

echo "🎉 部署完成！" 