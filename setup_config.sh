#!/bin/bash
# GrillRadar 快速配置脚本 (Bash 版本)
# 适用于 Linux/macOS 用户

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 打印函数
print_header() {
    echo -e "\n${BLUE}============================================================${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}============================================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${CYAN}ℹ $1${NC}"
}

# 检查依赖
check_requirements() {
    if ! command -v python3 &> /dev/null; then
        print_error "未找到 Python 3"
        echo "请先安装 Python 3.8+"
        exit 1
    fi

    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    print_success "Python $PYTHON_VERSION 已安装"
}

# 主菜单
show_menu() {
    clear
    print_header "GrillRadar 快速配置"

    echo "请选择配置方式:"
    echo ""
    echo "  1) 交互式配置向导 (推荐新手)"
    echo "  2) 使用配置模板 (快速)"
    echo "  3) 测试当前配置"
    echo "  4) 查看配置文档"
    echo "  0) 退出"
    echo ""
    read -p "请选择 [1-4, 0退出]: " choice

    case $choice in
        1) interactive_wizard ;;
        2) use_template ;;
        3) test_config ;;
        4) view_docs ;;
        0) exit 0 ;;
        *)
            print_warning "无效选择，请重试"
            sleep 1
            show_menu
            ;;
    esac
}

# 交互式向导
interactive_wizard() {
    print_header "交互式配置向导"

    # 检查 Python 向导是否可用
    if [ -f "setup_config.py" ]; then
        print_info "启动 Python 配置向导..."
        python3 setup_config.py
    else
        print_error "未找到 setup_config.py"
        print_info "使用简化版 Bash 配置..."
        bash_wizard
    fi

    echo ""
    read -p "按 Enter 返回主菜单..."
    show_menu
}

# Bash 版简化配置向导
bash_wizard() {
    print_header "简化配置向导"

    # 检查现有配置
    if [ -f ".env" ]; then
        print_warning "检测到现有 .env 文件"
        read -p "是否覆盖? [y/N]: " overwrite
        if [[ ! $overwrite =~ ^[Yy]$ ]]; then
            print_info "保留现有配置"
            return
        fi
    fi

    # 选择 LLM 提供商
    echo ""
    print_info "选择 LLM 提供商:"
    echo "  1) Anthropic Claude (推荐)"
    echo "  2) OpenAI GPT"
    read -p "请选择 [1-2]: " provider_choice

    # 获取 API Key
    echo ""
    if [ "$provider_choice" = "1" ]; then
        print_info "Anthropic Claude 配置"
        echo "  获取 API Key: https://console.anthropic.com/"
        read -p "是否使用第三方服务 (如 BigModel)? [y/N]: " use_third_party

        if [[ $use_third_party =~ ^[Yy]$ ]]; then
            read -p "请输入 Auth Token: " auth_token
            read -p "请输入 Base URL [https://open.bigmodel.cn/api/anthropic]: " base_url
            base_url=${base_url:-https://open.bigmodel.cn/api/anthropic}

            cat > .env << EOF
# GrillRadar 环境配置 (第三方 Anthropic 服务)
ANTHROPIC_AUTH_TOKEN=$auth_token
ANTHROPIC_BASE_URL=$base_url
DEFAULT_LLM_PROVIDER=anthropic
DEFAULT_MODEL=claude-sonnet-4
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=16000
LLM_TIMEOUT=120

APP_NAME=GrillRadar
APP_VERSION=1.0.0
DEBUG=False
EOF
        else
            read -p "请输入 Anthropic API Key: " api_key

            cat > .env << EOF
# GrillRadar 环境配置 (Anthropic 官方)
ANTHROPIC_API_KEY=$api_key
DEFAULT_LLM_PROVIDER=anthropic
DEFAULT_MODEL=claude-sonnet-4
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=16000
LLM_TIMEOUT=120

APP_NAME=GrillRadar
APP_VERSION=1.0.0
DEBUG=False
EOF
        fi
    else
        print_info "OpenAI GPT 配置"
        echo "  获取 API Key: https://platform.openai.com/api-keys"
        read -p "请输入 OpenAI API Key: " api_key

        cat > .env << EOF
# GrillRadar 环境配置 (OpenAI)
OPENAI_API_KEY=$api_key
DEFAULT_LLM_PROVIDER=openai
DEFAULT_MODEL=gpt-4o
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=16000
LLM_TIMEOUT=120

APP_NAME=GrillRadar
APP_VERSION=1.0.0
DEBUG=False
EOF
    fi

    print_success "配置文件已创建: .env"
    print_info ""
    print_info "下一步:"
    print_info "  1. 启动应用: python -m uvicorn app.main:app --reload"
    print_info "  2. 访问文档: http://localhost:8000/docs"
}

# 使用模板
use_template() {
    print_header "使用配置模板"

    if [ ! -f ".env.example" ]; then
        print_error "未找到 .env.example 模板"
        return
    fi

    # 选择模板
    echo "可用模板:"
    echo "  1) .env.example (基础配置)"
    if [ -f ".env.example.detailed" ]; then
        echo "  2) .env.example.detailed (详细配置)"
    fi
    echo ""
    read -p "请选择模板 [1-2]: " template_choice

    if [ "$template_choice" = "2" ] && [ -f ".env.example.detailed" ]; then
        template_file=".env.example.detailed"
    else
        template_file=".env.example"
    fi

    # 复制模板
    if [ -f ".env" ]; then
        print_warning "目标文件 .env 已存在"
        read -p "是否覆盖? [y/N]: " overwrite
        if [[ ! $overwrite =~ ^[Yy]$ ]]; then
            print_info "操作已取消"
            echo ""
            read -p "按 Enter 返回主菜单..."
            show_menu
            return
        fi
    fi

    cp "$template_file" .env
    print_success "已复制 $template_file 到 .env"

    # 提示编辑
    echo ""
    print_info "请编辑 .env 文件，填入你的配置:"
    print_info "  必需修改: ANTHROPIC_API_KEY 或 OPENAI_API_KEY"
    echo ""

    # 提供编辑选项
    read -p "是否现在编辑? [Y/n]: " edit_now
    if [[ ! $edit_now =~ ^[Nn]$ ]]; then
        # 使用系统默认编辑器
        ${EDITOR:-nano} .env
    fi

    print_success "配置已准备完成"
    print_info "运行 'python -m uvicorn app.main:app --reload' 启动应用"

    echo ""
    read -p "按 Enter 返回主菜单..."
    show_menu
}

# 测试配置
test_config() {
    print_header "测试当前配置"

    if [ ! -f ".env" ]; then
        print_error "未找到 .env 文件"
        print_info "请先运行配置向导"
        echo ""
        read -p "按 Enter 返回主菜单..."
        show_menu
        return
    fi

    # 使用 Python 测试工具
    if [ -f "setup_config.py" ]; then
        python3 setup_config.py --test
    else
        # 简单测试
        print_info "检查配置文件..."

        # 检查关键字段
        if grep -q "ANTHROPIC_API_KEY=" .env || grep -q "ANTHROPIC_AUTH_TOKEN=" .env; then
            print_success "检测到 Anthropic API 配置"
        elif grep -q "OPENAI_API_KEY=" .env; then
            print_success "检测到 OpenAI API 配置"
        else
            print_warning "未检测到 API 密钥配置"
        fi

        # 显示当前配置
        echo ""
        print_info "当前配置摘要:"
        grep -E "^(DEFAULT_LLM_PROVIDER|DEFAULT_MODEL|LLM_TEMPERATURE)=" .env || true
    fi

    echo ""
    read -p "按 Enter 返回主菜单..."
    show_menu
}

# 查看文档
view_docs() {
    print_header "配置文档"

    if [ -f "CONFIGURATION.md" ]; then
        # 使用 less 或 more 查看
        if command -v less &> /dev/null; then
            less CONFIGURATION.md
        else
            more CONFIGURATION.md
        fi
    else
        print_warning "未找到 CONFIGURATION.md"
        print_info "请访问项目 README 查看文档"
    fi

    show_menu
}

# 主程序
main() {
    # 检查依赖
    check_requirements

    # 显示主菜单
    show_menu
}

# 运行主程序
main
