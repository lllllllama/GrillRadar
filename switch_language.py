#!/usr/bin/env python3
"""
GrillRadar 语言切换工具 / Language Switcher Utility

一键切换文档语言 / Switch documentation language with one click

用法 / Usage:
    python switch_language.py en    # 切换到英文 / Switch to English
    python switch_language.py zh    # 切换到中文 / Switch to Chinese
    python switch_language.py       # 显示当前语言 / Show current language
"""
import os
import shutil
import sys
from pathlib import Path


# 双语文档映射 / Bilingual document mapping
DOCS = {
    'README.md': {
        'zh': 'README.md',
        'en': 'README.en.md'
    },
    'CONFIGURATION.md': {
        'zh': 'CONFIGURATION.md',
        'en': 'CONFIGURATION.en.md'
    },
    'DOMAINS.md': {
        'zh': 'DOMAINS.md',
        'en': 'DOMAINS.en.md'
    },
    'EXTERNAL_INFO.md': {
        'zh': 'EXTERNAL_INFO.md',
        'en': 'EXTERNAL_INFO.en.md'
    },
    'WEB_INTERFACE.md': {
        'zh': 'WEB_INTERFACE.md',
        'en': 'WEB_INTERFACE.en.md'
    }
}

# 语言显示名称 / Language display names
LANG_NAMES = {
    'zh': '中文 (Chinese)',
    'en': 'English'
}


def get_current_language():
    """
    检测当前文档语言 / Detect current documentation language

    Returns:
        'zh' or 'en'
    """
    # 检查README.md的第一行来判断语言
    # Check first line of README.md to determine language
    readme_path = Path('README.md')
    if not readme_path.exists():
        return 'unknown'

    with open(readme_path, 'r', encoding='utf-8') as f:
        first_line = f.readline()

    # 如果第一行包含中文字符，则为中文
    if any('\u4e00' <= char <= '\u9fff' for char in first_line):
        return 'zh'
    else:
        return 'en'


def switch_language(target_lang):
    """
    切换文档语言 / Switch documentation language

    Args:
        target_lang: 'zh' or 'en'
    """
    if target_lang not in ['zh', 'en']:
        print(f"❌ 无效的语言选项 / Invalid language: {target_lang}")
        print("   支持的语言 / Supported languages: zh, en")
        return False

    current_lang = get_current_language()

    if current_lang == target_lang:
        print(f"✓ 当前已是{LANG_NAMES[target_lang]} / Already in {LANG_NAMES[target_lang]}")
        return True

    print(f"🔄 切换语言中 / Switching language: {LANG_NAMES[current_lang]} → {LANG_NAMES[target_lang]}")
    print()

    success_count = 0
    fail_count = 0

    for doc_name, lang_files in DOCS.items():
        source_file = lang_files[target_lang]

        if not Path(source_file).exists():
            print(f"⚠️  跳过 / Skip: {doc_name} (未找到{LANG_NAMES[target_lang]}版本 / {LANG_NAMES[target_lang]} version not found)")
            fail_count += 1
            continue

        # 创建符号链接或复制文件
        # 由于符号链接在某些系统上可能有问题，这里使用复制
        # Create symbolic link or copy file
        # Use copy instead of symlink for better compatibility
        try:
            # 备份当前文件（如果需要）
            # Backup current file (if needed)
            if Path(doc_name).exists() and doc_name != source_file:
                backup_path = Path(doc_name).with_suffix('.md.bak')
                shutil.copy(doc_name, backup_path)

            # 复制目标语言文件到主文件名
            # Copy target language file to main filename
            if doc_name != source_file:
                shutil.copy(source_file, doc_name)
                print(f"✓ {doc_name} → {source_file}")
                success_count += 1
            else:
                print(f"○ {doc_name} (无需更改 / No change needed)")
        except Exception as e:
            print(f"❌ 失败 / Failed: {doc_name} - {e}")
            fail_count += 1

    print()
    print("=" * 60)
    if fail_count == 0:
        print(f"✅ 语言切换完成 / Language switched successfully!")
        print(f"   成功 / Success: {success_count} 个文件 / files")
        print(f"   当前语言 / Current language: {LANG_NAMES[target_lang]}")
    else:
        print(f"⚠️  语言切换部分完成 / Language switch partially completed")
        print(f"   成功 / Success: {success_count} 个文件 / files")
        print(f"   失败 / Failed: {fail_count} 个文件 / files")
    print("=" * 60)

    return fail_count == 0


def show_status():
    """显示当前语言状态 / Show current language status"""
    current_lang = get_current_language()

    print("=" * 60)
    print("GrillRadar 文档语言状态 / Documentation Language Status")
    print("=" * 60)
    print()
    print(f"当前语言 / Current Language: {LANG_NAMES.get(current_lang, 'Unknown')}")
    print()
    print("可用文档 / Available Documents:")
    print()

    for doc_name, lang_files in DOCS.items():
        zh_exists = "✓" if Path(lang_files['zh']).exists() else "✗"
        en_exists = "✓" if Path(lang_files['en']).exists() else "✗"
        print(f"  {doc_name:20s}  中文:{zh_exists}  English:{en_exists}")

    print()
    print("使用方法 / Usage:")
    print("  python switch_language.py zh    # 切换到中文 / Switch to Chinese")
    print("  python switch_language.py en    # 切换到英文 / Switch to English")
    print("=" * 60)


def main():
    """主函数 / Main function"""
    if len(sys.argv) < 2:
        show_status()
        return

    target_lang = sys.argv[1].lower()

    if target_lang in ['--help', '-h', 'help']:
        print(__doc__)
        return

    success = switch_language(target_lang)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
