#!/usr/bin/env python3
"""
数据库版本更新脚本
==================
使用方法：
    python migrate_db.py

功能：
    1. 自动检测模型变化
    2. 生成迁移文件
    3. 执行迁移更新数据库
"""
import sys
import os
from subprocess import run, CalledProcessError
from datetime import datetime


def main():
    print("=" * 60)
    print("数据库版本更新")
    print("=" * 60 + "\n")

    # 生成迁移描述（使用当前时间）
    message = f"auto migrate {datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # 步骤 1: 生成迁移文件
    print("=== 步骤 1: 生成迁移文件 ===")
    try:
        run(
            ["alembic", "revision", "--autogenerate", "-m", message],
            check=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        print("✓ 迁移文件生成完成\n")
    except CalledProcessError as e:
        print(f"✗ 生成迁移文件失败: {e}")
        return 1

    # 步骤 2: 执行迁移
    print("=== 步骤 2: 执行迁移 ===")
    try:
        run(
            ["alembic", "upgrade", "head"],
            check=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        print("✓ 数据库迁移完成\n")
    except CalledProcessError as e:
        print(f"✗ 执行迁移失败: {e}")
        return 1

    print("=" * 60)
    print("✓ 数据库版本更新成功！")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
