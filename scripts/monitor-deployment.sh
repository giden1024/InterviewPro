#!/bin/bash

# AWS InterviewPro 部署状态监控脚本
SERVER_IP="3.138.194.143"
DOMAIN="offerott.com"

echo "🔍 监控AWS部署状态..."
echo "================================"
echo "服务器: $SERVER_IP"
echo "域名: $DOMAIN" 
echo "GitHub Actions: https://github.com/giden1024/InterviewPro/actions"
echo "================================"

# 检查GitHub Actions状态
check_github_actions() {
    echo -e "\n📊 GitHub Actions 部署状态"
    echo "访问: https://github.com/giden1024/InterviewPro/actions"
    echo "查看最新的部署工作流状态..."
}

# 检查服务器连通性
check_server_connectivity() {
    echo -e "\n🌐 检查服务器连通性..."
    
    if ping -c 3 $SERVER_IP >/dev/null 2>&1; then
        echo "✅ 服务器 $SERVER_IP 连通正常"
    else
        echo "❌ 服务器 $SERVER_IP 无法连通"
        return 1
    fi
}

# 检查网站访问
check_website() {
    echo -e "\n🌍 检查网站访问..."
    
    # 检查HTTP
    if curl -s -o /dev/null -w "%{http_code}" http://$DOMAIN | grep -q "200\|301\|302"; then
        echo "✅ HTTP访问正常: http://$DOMAIN"
    else
        echo "❌ HTTP访问失败: http://$DOMAIN"
    fi
    
    # 检查HTTPS
    if curl -s -o /dev/null -w "%{http_code}" https://$DOMAIN | grep -q "200\|301\|302"; then
        echo "✅ HTTPS访问正常: https://$DOMAIN"
    else
        echo "❌ HTTPS访问失败: https://$DOMAIN"
    fi
}

# 检查API健康状态
check_api() {
    echo -e "\n🔧 检查API状态..."
    
    API_HEALTH=$(curl -s https://$DOMAIN/api/v1/health 2>/dev/null)
    if echo "$API_HEALTH" | grep -q "healthy\|success"; then
        echo "✅ API健康检查通过"
        echo "响应: $API_HEALTH"
    else
        echo "❌ API健康检查失败"
        echo "尝试HTTP..."
        API_HEALTH_HTTP=$(curl -s http://$DOMAIN/api/v1/health 2>/dev/null)
        if echo "$API_HEALTH_HTTP" | grep -q "healthy\|success"; then
            echo "✅ API HTTP访问正常"
            echo "响应: $API_HEALTH_HTTP"
        else
            echo "❌ API完全无法访问"
        fi
    fi
}

# 检查关键页面
check_key_pages() {
    echo -e "\n📄 检查关键页面..."
    
    # 主页
    if curl -s https://$DOMAIN/ | grep -q "InterviewPro\|登录\|面试"; then
        echo "✅ 主页加载正常"
    else
        echo "❌ 主页加载失败"
    fi
    
    # 登录页面  
    if curl -s https://$DOMAIN/login | grep -q "login\|登录\|邮箱"; then
        echo "✅ 登录页面正常"
    else
        echo "❌ 登录页面失败"
    fi
}

# 测试新功能
test_new_features() {
    echo -e "\n🧪 测试新修复的功能..."
    
    echo "📋 简历解析JSON显示页面:"
    echo "   https://$DOMAIN/test-resume-parser-json-display.html"
    
    echo "🔐 登录错误测试页面:"  
    echo "   https://$DOMAIN/test-login-error-fix.html"
    
    echo "🧹 缓存清理工具:"
    echo "   https://$DOMAIN/clear-cache-and-reload.html"
    
    echo "🔍 调试工具页面:"
    echo "   https://$DOMAIN/debug-login-issue.html"
}

# 显示部署验证结果
show_deployment_summary() {
    echo -e "\n🎯 部署验证总结"
    echo "================================"
    
    echo "📈 本次部署包含的主要修复："
    echo "  ✨ 完整简历解析功能（项目、经历、教育背景）"
    echo "  🔐 登录错误信息显示修复"
    echo "  📊 数据库模型增强" 
    echo "  🧪 新增测试和调试工具"
    echo "  📚 完整文档更新"
    
    echo -e "\n🔗 关键访问地址："
    echo "  🌐 生产网站: https://$DOMAIN"
    echo "  📡 API接口: https://$DOMAIN/api/v1/"
    echo "  💚 健康检查: https://$DOMAIN/api/v1/health"
    echo "  📊 GitHub Actions: https://github.com/giden1024/InterviewPro/actions"
    
    echo -e "\n⏰ 部署时间估计："
    echo "  GitHub Actions通常需要5-10分钟完成完整部署流程"
    echo "  包括: 测试 → 安全扫描 → 构建 → 部署 → 验证"
}

# 主函数
main() {
    check_github_actions
    check_server_connectivity
    check_website  
    check_api
    check_key_pages
    test_new_features
    show_deployment_summary
    
    echo -e "\n🎉 部署监控完成！"
    echo "如需查看详细部署日志，请访问GitHub Actions页面。"
}

# 运行监控
main 