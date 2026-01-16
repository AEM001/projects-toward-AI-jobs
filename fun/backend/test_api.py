"""
API 测试脚本
使用方法: python test_api.py
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_api():
    # 测试用户数据
    test_email = "test@example.com"
    test_password = "test123"

    print_section("1. 测试根路径")
    response = requests.get(f"{BASE_URL}/")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")

    print_section("2. 用户注册")
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json={"email": test_email, "password": test_password}
    )
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")

    print_section("3. 用户登录")
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": test_email, "password": test_password}
    )
    print(f"状态码: {response.status_code}")
    login_data = response.json()
    print(f"响应: {login_data}")

    token = login_data.get("access_token")
    if not token:
        print("登录失败，退出测试")
        return

    headers = {"Authorization": f"Bearer {token}"}

    print_section("4. 创建任务 1")
    response = requests.post(
        f"{BASE_URL}/tasks",
        json={"title": "学习 FastAPI", "description": "掌握基础概念"},
        headers=headers
    )
    print(f"状态码: {response.status_code}")
    task1 = response.json()
    print(f"响应: {json.dumps(task1, indent=2, ensure_ascii=False)}")

    print_section("5. 创建任务 2")
    response = requests.post(
        f"{BASE_URL}/tasks",
        json={"title": "学习 Vue 3", "description": "Composition API"},
        headers=headers
    )
    print(f"状态码: {response.status_code}")
    task2 = response.json()
    print(f"响应: {json.dumps(task2, indent=2, ensure_ascii=False)}")

    print_section("6. 获取任务列表")
    response = requests.get(f"{BASE_URL}/tasks", headers=headers)
    print(f"状态码: {response.status_code}")
    tasks = response.json()
    print(f"任务数量: {len(tasks)}")
    print(f"响应: {json.dumps(tasks, indent=2, ensure_ascii=False)}")

    if tasks:
        task_id = tasks[0]["id"]

        print_section("7. 更新任务状态")
        response = requests.put(
            f"{BASE_URL}/tasks/{task_id}",
            json={"status": "in_progress"},
            headers=headers
        )
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

        print_section("8. 删除任务")
        response = requests.delete(f"{BASE_URL}/tasks/{task_id}", headers=headers)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")

        print_section("9. 获取任务列表（再次）")
        response = requests.get(f"{BASE_URL}/tasks", headers=headers)
        print(f"状态码: {response.status_code}")
        print(f"任务数量: {len(response.json())}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

    print_section("测试完成！")
    print(f"\nAPI 文档: {BASE_URL}/docs")
    print(f"前端地址: http://localhost:5173")


if __name__ == "__main__":
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("\n❌ 错误: 无法连接到后端服务")
        print("请确保后端已启动: uvicorn main:app --reload --port 8000")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
