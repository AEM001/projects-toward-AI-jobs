from src.models.task import Task, Priority, Status
from src.storage.json_storage import JSONStorage

def main():
    storage=JSONStorage("data/tasks.json")
    tasks=[
        Task(id=1,title="学习python文件操作",priority=Priority.HIGH),
        Task(id=2,title="实现json存储",priority=Priority.MEDIUM,
        status=Status.IN_PROGRESS),
        Task(id=3,title="编写单元测试",priority=Priority.LOW)
    ]

    print("="*50)
    print("1. 保存任务到文件")
    print("="*50)
    storage.save(tasks)
    print(f"✅ 已保存 {len(tasks)} 个任务到: {storage.get_file_path()}")
    
    print("\n"+"="*50)
    print("2. 从文件加载任务")
    print("="*50)
    loaded_tasks=storage.load()
    print(f"✅ 已加载 {len(loaded_tasks)} 个任务")

    print("\n任务列表")
    for task in loaded_tasks:
        print(f"  - {task}")

    print("\n"+"="*50)
    print("3. 修改任务状态并保存")
    print("="*50)

    loaded_tasks[0].update_status(Status.DONE)
    storage.save(loaded_tasks)
    print("✅ 任务状态已更新并保存")

    print("\n"+"="*50)
    print("4. 验证修改已保存")
    print("="*50)
    reloaded_tasks=storage.load()
    print(f"✅ 已重新加载 {len(reloaded_tasks)} 个任务")
    print(f"第一个任务状态:{reloaded_tasks[0].status.value}")

    print("\n所有测试通过")

if __name__=="__main__":
    main()