#!/usr/bin/env python3
"""
创建 hr_employees 表并插入随机数据
用于测试人力资源报表功能

使用方式:
    cd /Users/lrq/Python项目/final_fastapi_streamlit
    python seed_hr_data.py
"""

import sys
import os
import pymysql
import random
from datetime import datetime, timedelta
import logging

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入后端配置
try:
    from backend.core.config import settings
except ImportError as e:
    print(f"导入配置失败: {e}")
    print("请确保在项目根目录运行此脚本")
    sys.exit(1)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 数据库连接配置
DB_CONFIG = {
    'host': settings.MYSQL_HOST,
    'port': settings.MYSQL_PORT,
    'user': settings.MYSQL_USER,
    'password': settings.MYSQL_PASSWORD,
    'database': settings.MYSQL_DB,
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

# 部门列表
DEPARTMENTS = [
    '技术部', '销售部', '市场部', '人力资源部', '财务部',
    '产品部', '运营部', '设计部', '行政部', '法务部'
]

# 名字列表（用于生成随机员工姓名）
FIRST_NAMES = ['张', '王', '李', '赵', '刘', '陈', '杨', '黄', '周', '吴',
               '徐', '孙', '胡', '朱', '高', '林', '何', '郭', '马', '罗']

LAST_NAMES = ['伟', '芳', '娜', '秀英', '敏', '静', '丽', '强', '磊', '军',
              '洋', '勇', '艳', '杰', '娟', '涛', '明', '超', '秀兰', '霞']

# 薪资范围（元）
SALARY_RANGE = {
    '初级': (5000, 10000),
    '中级': (10000, 20000),
    '高级': (20000, 50000),
    '管理': (50000, 100000)
}

def get_connection():
    """获取数据库连接"""
    try:
        connection = pymysql.connect(**DB_CONFIG)
        logger.info(f"成功连接到数据库: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
        return connection
    except pymysql.Error as e:
        logger.error(f"数据库连接失败: {e}")
        sys.exit(1)

def create_table(connection):
    """创建 hr_employees 表"""

    create_table_sql = """
    CREATE TABLE IF NOT EXISTS hr_employees (
        id INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键',
        employee_name VARCHAR(100) NOT NULL COMMENT '员工姓名',
        department_name VARCHAR(100) NOT NULL COMMENT '部门名称',
        status ENUM('active', 'inactive') NOT NULL DEFAULT 'active' COMMENT '状态',
        salary DECIMAL(10, 2) NOT NULL COMMENT '薪资',
        hire_date DATE NOT NULL COMMENT '入职日期',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
        INDEX idx_department (department_name),
        INDEX idx_status (status),
        INDEX idx_hire_date (hire_date)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='人力资源员工表';
    """

    try:
        with connection.cursor() as cursor:
            cursor.execute(create_table_sql)
        connection.commit()
        logger.info("hr_employees 表创建成功")

        # 检查表是否存在
        with connection.cursor() as cursor:
            cursor.execute("SHOW TABLES LIKE 'hr_employees'")
            result = cursor.fetchone()
            if result:
                logger.info("确认表已存在")
                return True
            else:
                logger.error("表创建失败")
                return False

    except pymysql.Error as e:
        logger.error(f"创建表失败: {e}")
        connection.rollback()
        return False

def generate_random_employee(employee_id):
    """生成随机员工数据"""

    # 随机选择部门
    department = random.choice(DEPARTMENTS)

    # 生成随机姓名
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)
    employee_name = f"{first_name}{last_name}"

    # 根据部门和随机因素确定薪资等级
    if '管理' in department or '总监' in department:
        grade = '管理'
    elif '高级' in department or random.random() > 0.7:
        grade = '高级'
    elif random.random() > 0.4:
        grade = '中级'
    else:
        grade = '初级'

    salary_min, salary_max = SALARY_RANGE[grade]
    salary = random.randint(salary_min, salary_max)

    # 随机决定状态 (80% 活跃，20% 非活跃)
    status = 'active' if random.random() > 0.2 else 'inactive'

    # 生成随机入职日期 (过去5年内)
    today = datetime.now()
    days_ago = random.randint(1, 5 * 365)  # 过去5年
    hire_date = today - timedelta(days=days_ago)

    # 格式化日期为字符串 (YYYY-MM-DD)
    hire_date_str = hire_date.strftime('%Y-%m-%d')

    return {
        'employee_name': employee_name,
        'department_name': department,
        'status': status,
        'salary': salary,
        'hire_date': hire_date_str
    }

def insert_sample_data(connection, count=50):
    """插入示例数据"""

    # 先清空表 (可选)
    try:
        with connection.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE hr_employees")
        logger.info("已清空 hr_employees 表")
    except pymysql.Error as e:
        logger.warning(f"清空表时出错 (可能表不存在或无权操作): {e}")

    insert_sql = """
    INSERT INTO hr_employees
    (employee_name, department_name, status, salary, hire_date)
    VALUES (%s, %s, %s, %s, %s)
    """

    employees_data = []
    for i in range(count):
        employee = generate_random_employee(i + 1)
        employees_data.append((
            employee['employee_name'],
            employee['department_name'],
            employee['status'],
            employee['salary'],
            employee['hire_date']
        ))

    try:
        with connection.cursor() as cursor:
            cursor.executemany(insert_sql, employees_data)
        connection.commit()

        logger.info(f"成功插入 {len(employees_data)} 条员工记录")

        # 显示插入的数据摘要
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    department_name,
                    COUNT(*) as count,
                    AVG(salary) as avg_salary,
                    SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active_count
                FROM hr_employees
                GROUP BY department_name
                ORDER BY count DESC
            """)
            summary = cursor.fetchall()

            logger.info("数据插入摘要:")
            for dept in summary:
                logger.info(f"  部门: {dept['department_name']}, 人数: {dept['count']}, "
                          f"平均薪资: {dept['avg_salary']:.2f}, 活跃: {dept['active_count']}")

        return True

    except pymysql.Error as e:
        logger.error(f"插入数据失败: {e}")
        connection.rollback()
        return False

def verify_data(connection):
    """验证数据是否正确插入"""

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as total FROM hr_employees")
            result = cursor.fetchone()
            total = result['total']

            if total > 0:
                logger.info(f"验证成功: hr_employees 表中有 {total} 条记录")

                # 显示各部门人数
                cursor.execute("""
                    SELECT department_name, COUNT(*) as count
                    FROM hr_employees
                    GROUP BY department_name
                    ORDER BY count DESC
                """)
                departments = cursor.fetchall()

                logger.info("部门分布:")
                for dept in departments:
                    logger.info(f"  {dept['department_name']}: {dept['count']} 人")

                return True
            else:
                logger.error("验证失败: 表中没有数据")
                return False

    except pymysql.Error as e:
        logger.error(f"验证数据时出错: {e}")
        return False

def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("开始创建 hr_employees 表并插入随机数据")
    logger.info("=" * 60)

    # 获取数据库连接
    connection = get_connection()

    try:
        # 1. 创建表
        if not create_table(connection):
            logger.error("表创建失败，退出")
            sys.exit(1)

        # 2. 插入数据
        record_count = 50  # 插入50条记录
        if not insert_sample_data(connection, record_count):
            logger.error("数据插入失败，退出")
            sys.exit(1)

        # 3. 验证数据
        if not verify_data(connection):
            logger.error("数据验证失败")
            sys.exit(1)

        logger.info("=" * 60)
        logger.info("✅ 数据准备完成！")
        logger.info(f"   表名: hr_employees")
        logger.info(f"   记录数: {record_count}")
        logger.info(f"   数据库: {DB_CONFIG['database']}")
        logger.info("=" * 60)
        logger.info("现在可以测试报表功能:")
        logger.info("   1. 启动后端: ./scripts/start_backend.sh")
        logger.info("   2. 启动前端: ./scripts/start_frontend.sh")
        logger.info("   3. 访问 http://localhost:8501")
        logger.info("   4. 在员工管理页面选择 '报表数据'")

    finally:
        connection.close()
        logger.info("数据库连接已关闭")

if __name__ == "__main__":
    main()