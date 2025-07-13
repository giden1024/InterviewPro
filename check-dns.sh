#!/bin/bash

# DNS解析检查脚本

echo "🌐 检查域名DNS解析状态..."

SERVER_IP="47.110.144.20"
DOMAIN="offerott.com"
WWW_DOMAIN="www.offerott.com"

# 检查主域名
echo "📋 检查 $DOMAIN 解析："
DOMAIN_IP=$(nslookup $DOMAIN | grep -A1 "Non-authoritative answer:" | grep "Address:" | head -1 | awk '{print $2}')
if [ "$DOMAIN_IP" = "$SERVER_IP" ]; then
    echo "✅ $DOMAIN → $DOMAIN_IP (正确)"
    DOMAIN_OK=true
else
    echo "❌ $DOMAIN → $DOMAIN_IP (错误，应为 $SERVER_IP)"
    DOMAIN_OK=false
fi

# 检查www子域名
echo "📋 检查 $WWW_DOMAIN 解析："
WWW_IP=$(nslookup $WWW_DOMAIN | grep -A1 "Non-authoritative answer:" | grep "Address:" | head -1 | awk '{print $2}')
if [ "$WWW_IP" = "$SERVER_IP" ]; then
    echo "✅ $WWW_DOMAIN → $WWW_IP (正确)"
    WWW_OK=true
else
    echo "❌ $WWW_DOMAIN → $WWW_IP (错误，应为 $SERVER_IP)"
    WWW_OK=false
fi

# 测试连通性
echo "🔍 测试连通性："
if ping -c 3 $DOMAIN > /dev/null 2>&1; then
    echo "✅ $DOMAIN 连通正常"
else
    echo "❌ $DOMAIN 连通失败"
fi

# 总结
echo ""
echo "📊 DNS状态总结："
if [ "$DOMAIN_OK" = true ] && [ "$WWW_OK" = true ]; then
    echo "🎉 DNS解析完全正确！可以申请Let's Encrypt证书了"
    echo "📝 运行以下命令申请SSL证书："
    echo "   bash /root/setup-letsencrypt.sh"
else
    echo "⏳ DNS尚未完全生效，请等待..."
    echo "💡 DNS传播通常需要几分钟到48小时"
fi

echo ""
echo "🔗 当前访问方式："
echo "  HTTP:  http://47.110.144.20"
echo "  HTTPS: https://47.110.144.20 (自签名证书)" 