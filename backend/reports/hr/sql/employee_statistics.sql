-- 员工统计报表
-- 参数：department (可选部门筛选), start_date (可选开始日期), end_date (可选结束日期)
SELECT
    department_name as department,
    COUNT(*) as employee_count,
    SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active_count,
    SUM(CASE WHEN status = 'inactive' THEN 1 ELSE 0 END) as inactive_count,
    AVG(salary) as avg_salary,
    MIN(hire_date) as earliest_hire,
    MAX(hire_date) as latest_hire
FROM hr_employees
WHERE 1=1
    {% if department %}
    AND department_name = :department
    {% endif %}
    {% if start_date %}
    AND hire_date >= :start_date
    {% endif %}
    {% if end_date %}
    AND hire_date <= :end_date
    {% endif %}
GROUP BY department_name
ORDER BY employee_count DESC