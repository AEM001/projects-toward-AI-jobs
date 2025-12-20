# Day5 CLI 命令行界面指导

## 1. 今日目标 & 全局思路
- **目标**：把已有的 Service / Storage / Logging / Exception 体系，通过一个 CLI 暴露给用户使用。
- **关键能力**：解析命令行（argparse）、格式化输出（tabulate + colorama 可选）、向用户友好地展示日志/异常信息。
- **整体流程**：
  1. 程序入口（`task.py`）中调用 `setup_logging()`、初始化 `JSONStorage` + `TaskService`。
  2. `src/cli.py` 负责解析参数 -> 根据子命令调用 `TaskService`。
  3. 捕获 `TaskMasterException` 并输出友好提示；未知异常输出 error + 堆栈。

```
┌──────────┐      ┌──────────────┐      ┌───────────────┐
│  CLI 命令 │──┬─▶│ ArgumentParser│──┬─▶│ TaskService API│
└──────────┘  │  └──────────────┘  │  └───────────────┘
              │                     │
              │                     └─▶ JSONStorage (load/save)
              │
              └─▶ 终端输出（tabulate/colorama） & 日志文件
```

## 2. 需要编写/更新的文件
| 文件 | 职责 | 关键点 |
| --- | --- | --- |
| `src/cli.py` | 定义 `ArgumentParser`、子命令、输出格式化 | 每个子命令封装为函数，便于单测；统一在此层捕获 `TaskMasterException` 并打印友好信息 |
| `task.py`（项目根目录或 `src/task.py`） | 程序入口 | 调 `setup_logging()`；创建 storage/service；调用 `cli.main(service)` |
| （可选）`src/cli_renderers.py` | 表格输出/颜色封装 | 如果输出逻辑较多，可抽离；也可以直接写在 `src/cli.py` |
| `requirements.txt` | 如果尚未添加 `tabulate`、`colorama` 依赖则补充（目前已存在，可直接使用） |
| 测试（可选）`tests/test_cli.py` | 覆盖参数解析/调度 | 可通过 `argparse` 的 `parse_args`/`Namespace` 单元测试 |

> **已有文件复用**：`TaskService`、`JSONStorage`、`config/logging_config.py`、`src/utils/exceptions.py`、`src/utils/logger.py`。

## 3. 命令设计 & 功能拆解
| 子命令 | 必选参数 | 可选参数 | 说明 |
| --- | --- | --- | --- |
| `add` | `title` | `--priority {low,medium,high}` | 创建任务，默认 `medium` |
| `list` | 无 | `--status {pending,in_progress,done}`、`--all` | `--status` 过滤状态；`--all` 表示包含已完成任务（若默认只看未完成） |
| `done` | `task_id` | 无 | 快捷命令：等价 `update --status done` |
| `update` | `task_id` | `--status {pending,in_progress,done}` | 更新任意状态 |
| `delete` | `task_id` | 无 | 删除任务 |

### 输出要求
- 使用 `tabulate` 把任务列表输出成表格：列包含 `ID`, `Title`, `Priority`, `Status`, `Updated`。
- 使用 `colorama` 可选美化：例如根据状态上色（PENDING 黄色、DONE 绿色）。
- 错误输出使用清晰提示（例如 `print(f"[ERROR] {e}")`）。

### 异常策略
- 捕获 `TaskMasterException`：输出 `str(e)` 并返回非 0 退出码（可选）。
- 捕获 `StorageException` 时，提示“存储失败，请查看 logs/taskmaster.log”。
- 未捕获异常时，logging 会记录堆栈，CLI 输出“发生未知错误”。

## 4. CLI 逻辑骨架（伪代码）
```python
# src/cli.py
import argparse
from tabulate import tabulate
from colorama import Fore, Style, init as colorama_init
from src.models.task import Priority, Status
from src.utils.exceptions import TaskMasterException

class TaskCLI:
    def __init__(self, service):
        self.service = service
        colorama_init(autoreset=True)

    def build_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(description="TaskMaster CLI")
        subparsers = parser.add_subparsers(dest="command", required=True)

        # add
        add_parser = subparsers.add_parser("add", help="添加任务")
        add_parser.add_argument("title")
        add_parser.add_argument("--priority", choices=[p.value for p in Priority], default=Priority.MEDIUM.value)

        # list
        list_parser = subparsers.add_parser("list", help="列出任务")
        list_parser.add_argument("--status", choices=[s.value for s in Status])
        list_parser.add_argument("--all", action="store_true")

        # done
        done_parser = subparsers.add_parser("done", help="标记完成")
        done_parser.add_argument("task_id")

        # update
        update_parser = subparsers.add_parser("update", help="更新状态")
        update_parser.add_argument("task_id")
        update_parser.add_argument("--status", required=True, choices=[s.value for s in Status])

        # delete
        delete_parser = subparsers.add_parser("delete", help="删除任务")
        delete_parser.add_argument("task_id")

        return parser

    def run(self, argv=None):
        parser = self.build_parser()
        args = parser.parse_args(argv)
        try:
            if args.command == "add":
                self.handle_add(args)
            elif args.command == "list":
                self.handle_list(args)
            elif args.command == "done":
                self.handle_update(args.task_id, Status.DONE.value)
            elif args.command == "update":
                self.handle_update(args.task_id, args.status)
            elif args.command == "delete":
                self.handle_delete(args.task_id)
        except TaskMasterException as e:
            print(f"[ERROR] {e}")
        except Exception as e:
            print("[ERROR] 未知错误，详见日志")
            raise

    def handle_add(self, args):
        priority = Priority(args.priority)
        task = self.service.add_task(args.title, priority)
        print(f"创建成功: {task.id}")

    def handle_list(self, args):
        status = Status(args.status) if args.status else None
        tasks = self.service.list_tasks(status=status)
        table = [[t.id, t.title, t.priority.value, t.status.value, t.updated_at.strftime("%Y-%m-%d %H:%M")]
                 for t in tasks]
        print(tabulate(table, headers=["ID", "Title", "Priority", "Status", "Updated"], tablefmt="pretty"))

    def handle_update(self, task_id, status_value):
        status = Status(status_value)
        task = self.service.update_task_status(task_id, status)
        print(f"已更新: {task.id} -> {task.status.value}")

    def handle_delete(self, task_id):
        self.service.delete_task(task_id)
        print(f"已删除: {task_id}")
```

> 上面代码仅示意结构：实际实现时可根据需要调整提示语、颜色、错误处理。

## 5. 入口文件 `task.py` 框架
```python
# task.py
from config.logging_config import setup_logging
from config import settings
from src.storage.json_storage import JSONStorage
from src.services.task_service import TaskService
from src.cli import TaskCLI


def main():
    setup_logging()
    storage = JSONStorage(settings.DATA_FILE)
    service = TaskService(storage)
    cli = TaskCLI(service)
    cli.run()


if __name__ == "__main__":
    main()
```

- 支持 `python task.py add "buy milk" --priority high` 等命令。
- 若后续要把 CLI 安装成包，只需将 `main()` 暴露给 `entry_points`。

## 6. 开发小贴士
1. **先实现无装饰的 CLI**，确认命令流程正常，再加 tabulate/colorama 美化。
2. **善用日志**：CLI 层只需输出关键信息，详细堆栈交给日志文件。
3. **测试建议**：
   - 对 `TaskCLI.build_parser()` 做单元测试：模拟不同参数，断言解析结果。
   - 对 handler 函数做单测：用假服务（Mock）断言调用了正确的 service 方法。
4. **错误码**（可选）：根据异常类型返回不同的 `sys.exit(code)`，方便脚本级调用。

---

以上就是 Day5 CLI 的结构与实现指导：先搭建解析骨架，再一步步填充业务逻辑与输出格式，就能得到一个功能完整、可维护的命令行工具。祝你编码顺利！
