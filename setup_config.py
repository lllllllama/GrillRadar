#!/usr/bin/env python3
"""
GrillRadar 配置向导
交互式配置工具，帮助用户快速完成环境配置
"""
import os
import sys
from pathlib import Path
from typing import Optional

# 颜色输出
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text: str):
    """打印标题"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text:^60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}\n")

def print_success(text: str):
    """打印成功消息"""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")

def print_warning(text: str):
    """打印警告消息"""
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")

def print_error(text: str):
    """打印错误消息"""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

def print_info(text: str):
    """打印信息"""
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")

def get_input(prompt: str, default: Optional[str] = None, required: bool = False) -> str:
    """获取用户输入"""
    if default:
        prompt_text = f"{prompt} [{default}]: "
    else:
        prompt_text = f"{prompt}: "

    while True:
        value = input(f"{Colors.OKBLUE}{prompt_text}{Colors.ENDC}").strip()

        if not value and default:
            return default

        if not value and required:
            print_warning("此项为必填项，请输入有效值")
            continue

        return value

def get_choice(prompt: str, choices: list, default: Optional[str] = None) -> str:
    """获取用户选择"""
    print(f"\n{Colors.OKBLUE}{prompt}{Colors.ENDC}")
    for i, choice in enumerate(choices, 1):
        marker = f" (默认)" if choice == default else ""
        print(f"  {i}. {choice}{marker}")

    while True:
        choice_input = input(f"{Colors.OKBLUE}请选择 [1-{len(choices)}]: {Colors.ENDC}").strip()

        if not choice_input and default:
            return default

        try:
            choice_idx = int(choice_input) - 1
            if 0 <= choice_idx < len(choices):
                return choices[choice_idx]
        except ValueError:
            pass

        print_warning(f"请输入 1-{len(choices)} 之间的数字")

def detect_existing_config() -> Optional[Path]:
    """检测现有配置"""
    env_file = Path(".env")
    if env_file.exists():
        return env_file
    return None

def create_env_file(config: dict):
    """创建 .env 文件"""
    env_file = Path(".env")

    with open(env_file, 'w', encoding='utf-8') as f:
        f.write("# GrillRadar 环境配置\n")
        f.write("# 由配置向导自动生成\n\n")

        # LLM 配置
        f.write("# ======================\n")
        f.write("# LLM API 配置\n")
        f.write("# ======================\n\n")

        if config['llm_provider'] == 'anthropic':
            if config.get('use_third_party'):
                f.write("# 使用第三方 Anthropic 兼容服务\n")
                f.write(f"ANTHROPIC_AUTH_TOKEN={config['anthropic_token']}\n")
                f.write(f"ANTHROPIC_BASE_URL={config['anthropic_base_url']}\n\n")
            else:
                f.write("# 使用官方 Anthropic API\n")
                f.write(f"ANTHROPIC_API_KEY={config['anthropic_api_key']}\n\n")
        elif config['llm_provider'] == 'openai':
            f.write("# 使用 OpenAI API\n")
            f.write(f"OPENAI_API_KEY={config['openai_api_key']}\n\n")

        # LLM 参数
        f.write("# LLM 参数配置\n")
        f.write(f"DEFAULT_LLM_PROVIDER={config['llm_provider']}\n")
        f.write(f"DEFAULT_MODEL={config['llm_model']}\n")
        f.write(f"LLM_TEMPERATURE={config.get('temperature', '0.7')}\n")
        f.write(f"LLM_MAX_TOKENS={config.get('max_tokens', '16000')}\n")
        f.write(f"LLM_TIMEOUT={config.get('timeout', '120')}\n\n")

        # 应用配置
        f.write("# ======================\n")
        f.write("# 应用配置\n")
        f.write("# ======================\n\n")
        f.write(f"APP_NAME={config.get('app_name', 'GrillRadar')}\n")
        f.write(f"APP_VERSION={config.get('app_version', '1.0.0')}\n")
        f.write(f"DEBUG={config.get('debug', 'False')}\n")

    print_success(f"配置文件已创建: {env_file.absolute()}")

def setup_wizard():
    """配置向导主流程"""
    print_header("GrillRadar 配置向导")

    # 检测现有配置
    existing_config = detect_existing_config()
    if existing_config:
        print_warning(f"检测到现有配置文件: {existing_config}")
        overwrite = get_choice(
            "是否覆盖现有配置？",
            ["是，重新配置", "否，退出"],
            default="否，退出"
        )
        if "否" in overwrite:
            print_info("配置向导已退出")
            return

    config = {}

    # 1. 选择 LLM 提供商
    print_header("步骤 1/4: 选择 LLM 提供商")
    print_info("GrillRadar 支持以下 LLM 提供商：")
    print_info("  • Anthropic Claude (推荐) - 强大的推理能力")
    print_info("  • OpenAI GPT - 广泛使用的模型")

    llm_provider = get_choice(
        "请选择 LLM 提供商",
        ["anthropic", "openai"],
        default="anthropic"
    )
    config['llm_provider'] = llm_provider

    # 2. 配置 API 密钥
    print_header("步骤 2/4: 配置 API 密钥")

    if llm_provider == "anthropic":
        print_info("Anthropic API 配置方式：")
        print_info("  1. 官方 API: https://console.anthropic.com/")
        print_info("  2. 第三方兼容服务: 如 BigModel (智谱AI)")

        use_official = get_choice(
            "使用哪种方式？",
            ["官方 Anthropic API", "第三方兼容服务 (如 BigModel)"],
            default="官方 Anthropic API"
        )

        if "官方" in use_official:
            config['use_third_party'] = False
            api_key = get_input(
                "请输入 Anthropic API Key",
                required=True
            )
            config['anthropic_api_key'] = api_key
        else:
            config['use_third_party'] = True
            print_info("\n第三方服务配置（以 BigModel 为例）：")
            print_info("  注册: https://open.bigmodel.cn/")
            print_info("  获取 Auth Token 后填入下方")

            auth_token = get_input(
                "请输入 Auth Token",
                required=True
            )
            config['anthropic_token'] = auth_token

            base_url = get_input(
                "请输入 Base URL",
                default="https://open.bigmodel.cn/api/anthropic"
            )
            config['anthropic_base_url'] = base_url

    else:  # OpenAI
        print_info("OpenAI API 配置:")
        print_info("  获取 API Key: https://platform.openai.com/api-keys")

        api_key = get_input(
            "请输入 OpenAI API Key",
            required=True
        )
        config['openai_api_key'] = api_key

    # 3. 选择模型
    print_header("步骤 3/4: 选择模型")

    if llm_provider == "anthropic":
        models = [
            "claude-sonnet-4 (推荐，平衡性能)",
            "claude-opus-4 (最强性能)",
            "claude-3-5-sonnet-20241022 (legacy)"
        ]
        model_choice = get_choice("请选择模型", models, default=models[0])
        config['llm_model'] = model_choice.split()[0]
    else:
        models = [
            "gpt-4o (推荐)",
            "gpt-4-turbo",
            "gpt-3.5-turbo (经济)"
        ]
        model_choice = get_choice("请选择模型", models, default=models[0])
        config['llm_model'] = model_choice.split()[0]

    # 4. 高级配置
    print_header("步骤 4/4: 高级配置 (可选)")

    advanced = get_choice(
        "是否配置高级选项？",
        ["否，使用默认值", "是，自定义配置"],
        default="否，使用默认值"
    )

    if "是" in advanced:
        temperature = get_input(
            "Temperature (0.0-1.0，控制创造性)",
            default="0.7"
        )
        config['temperature'] = temperature

        max_tokens = get_input(
            "Max Tokens (最大生成长度)",
            default="16000"
        )
        config['max_tokens'] = max_tokens

        debug = get_choice(
            "是否开启调试模式？",
            ["False", "True"],
            default="False"
        )
        config['debug'] = debug

    # 创建配置文件
    print_header("生成配置文件")
    create_env_file(config)

    # 验证配置
    print_header("验证配置")
    print_info("正在验证配置文件...")

    try:
        # 尝试导入并验证
        sys.path.insert(0, str(Path.cwd()))
        from app.config.validator import ConfigValidator

        ConfigValidator.validate_all()
        print_success("配置验证通过！")
    except Exception as e:
        print_warning(f"配置验证时出现警告: {e}")
        print_info("您仍然可以继续使用，但建议检查配置")

    # 完成
    print_header("配置完成")
    print_success("GrillRadar 配置已完成！")
    print_info("\n下一步：")
    print_info("  1. 启动应用: python -m uvicorn app.main:app --reload")
    print_info("  2. 访问文档: http://localhost:8000/docs")
    print_info("  3. 查看示例: examples/")
    print_info("\n如需修改配置，可以：")
    print_info("  • 重新运行此向导: python setup_config.py")
    print_info("  • 手动编辑: .env 文件")

def quick_test():
    """快速测试配置"""
    print_header("快速测试配置")

    try:
        from dotenv import load_dotenv
        load_dotenv()

        from app.config.settings import settings

        print_info("当前配置：")
        print(f"  • LLM Provider: {settings.DEFAULT_LLM_PROVIDER}")
        print(f"  • Model: {settings.DEFAULT_MODEL}")
        print(f"  • Temperature: {settings.LLM_TEMPERATURE}")
        print(f"  • Max Tokens: {settings.LLM_MAX_TOKENS}")

        # 检查 API Key
        if settings.DEFAULT_LLM_PROVIDER == "anthropic":
            if settings.ANTHROPIC_API_KEY or settings.ANTHROPIC_AUTH_TOKEN:
                print_success("API 密钥已配置")
            else:
                print_error("未检测到 API 密钥")
        elif settings.DEFAULT_LLM_PROVIDER == "openai":
            if settings.OPENAI_API_KEY:
                print_success("API 密钥已配置")
            else:
                print_error("未检测到 API 密钥")

    except Exception as e:
        print_error(f"配置测试失败: {e}")

def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description="GrillRadar 配置向导",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python setup_config.py              # 运行交互式配置向导
  python setup_config.py --test       # 测试当前配置
  python setup_config.py --help       # 显示此帮助信息
        """
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='测试当前配置'
    )

    args = parser.parse_args()

    if args.test:
        quick_test()
    else:
        try:
            setup_wizard()
        except KeyboardInterrupt:
            print_info("\n\n配置向导已取消")
            sys.exit(0)
        except Exception as e:
            print_error(f"\n配置过程中出现错误: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
