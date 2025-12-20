import argparse
from typing import Iterable, List, Optional

from colorama import Fore, Style, init as colorama_init
from tabulate import tabulate

from src.models.task import Priority, Status, Task
from src.services.task_service import TaskService
from src.utils.exceptions import StorageException, TaskMasterException

SHORT_ID_LEN = 8


class TaskCLI:
    """Command line interface wrapper around TaskService."""

    def __init__(self, service: TaskService):
        self.service = service
        self._last_displayed_tasks: List[Task] = []
        colorama_init(autoreset=True)

    # ------------------------------------------------------------------
    # public API
    # ------------------------------------------------------------------
    def run(self, argv: Optional[Iterable[str]] = None) -> int:
        parser = self._build_parser()
        args = parser.parse_args(argv)

        try:
            command = args.command
            if command == "add":
                return self._handle_add(args)
            if command == "list":
                return self._handle_list(args)
            if command == "done":
                return self._handle_update(args.task_id, status_value=Status.DONE.value, priority_value=None)
            if command == "update":
                return self._handle_update(args.task_id, status_value=args.status, priority_value=args.priority)
            if command == "delete":
                return self._handle_delete(args.task_id)
        except StorageException as e:
            print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} 存储失败：{e}. 请查看 logs/taskmaster.log")
            return 2
        except TaskMasterException as e:
            print(f"{Fore.YELLOW}[WARN]{Style.RESET_ALL} {e}")
            return 1
        except Exception as e:  # pragma: no cover - 兜底
            print(f"{Fore.RED}[FATAL]{Style.RESET_ALL} 未知错误：{e}")
            raise

        return 0

    # ------------------------------------------------------------------
    # parser
    # ------------------------------------------------------------------
    def _build_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            description="TaskMaster CLI：使用命令管理任务",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=(
                "示例:\n"
                "  python task.py add \"写周报\" --priority high\n"
                "  python task.py list --status pending\n"
                "  python task.py done 2           # 使用列表序号\n"
                "  python task.py update a21f98bf --status done  # 使用 Short ID\n"
                "  python task.py delete 3\n"
            ),
        )
        subparsers = parser.add_subparsers(dest="command", required=True)

        # add -----------------------------------------------------------
        add_parser = subparsers.add_parser("add", help="添加任务")
        add_parser.add_argument("title", help="任务标题")
        add_parser.add_argument(
            "--priority",
            choices=[p.value for p in Priority],
            default=Priority.MEDIUM.value,
            help="任务优先级（默认 medium）",
        )

        # list ----------------------------------------------------------
        list_parser = subparsers.add_parser("list", help="列出任务")
        list_parser.add_argument(
            "--status",
            choices=[s.value for s in Status],
            help="按状态过滤",
        )
        list_parser.add_argument(
            "--all",
            action="store_true",
            help="包含所有任务（即使完成）",
        )

        # done ----------------------------------------------------------
        done_parser = subparsers.add_parser("done", help="标记任务完成")
        done_parser.add_argument("task_id", help="任务序号 / Short ID / 完整 ID")

        # update --------------------------------------------------------
        update_parser = subparsers.add_parser("update", help="更新任务状态/优先级")
        update_parser.add_argument("task_id", help="任务序号 / Short ID / 完整 ID")
        update_parser.add_argument(
            "--status",
            choices=[s.value for s in Status],
            help="新的任务状态",
        )
        update_parser.add_argument(
            "--priority",
            choices=[p.value for p in Priority],
            help="新的任务优先级",
        )

        # delete --------------------------------------------------------
        delete_parser = subparsers.add_parser("delete", help="删除任务")
        delete_parser.add_argument("task_id", help="任务序号 / Short ID / 完整 ID")

        return parser

    # ------------------------------------------------------------------
    # handlers
    # ------------------------------------------------------------------
    def _handle_add(self, args: argparse.Namespace) -> int:
        priority = Priority(args.priority)
        task = self.service.add_task(args.title, priority)
        print(f"{Fore.GREEN}创建成功{Style.RESET_ALL}: {task.id} [{task.priority.value}]")
        return 0

    def _handle_list(self, args: argparse.Namespace) -> int:
        status = Status(args.status) if args.status else None
        tasks = self.service.list_tasks(status=status)
        if not args.all:
            tasks = [t for t in tasks if t.status != Status.DONE]
        self._render_task_table(tasks)
        return 0

    def _handle_update(
        self,
        task_id: str,
        status_value: Optional[str],
        priority_value: Optional[str],
    ) -> int:
        resolved_id = self._resolve_task_id(task_id)
        status = Status(status_value) if status_value else None
        priority = Priority(priority_value) if priority_value else None
        return self._perform_update(resolved_id, status=status, priority=priority)

    def _perform_update(self, task_id: str, status: Optional[Status], priority: Optional[Priority]) -> int:
        if status is None and priority is None:
            print(f"{Fore.YELLOW}[WARN]{Style.RESET_ALL} 请使用 --status 和/或 --priority 指定更新内容")
            return 1

        if status is not None:
            task = self.service.update_task_status(task_id, status)
            print(f"已更新状态 {task.id}: {task.status.value}")

        if priority is not None:
            task = self.service.update_task_priority(task_id, priority)
            print(f"已更新优先级 {task.id}: {task.priority.value}")
        return 0

    def _handle_delete(self, task_id: str) -> int:
        resolved_id = self._resolve_task_id(task_id)
        self.service.delete_task(resolved_id)
        print(f"已删除 {resolved_id}")
        return 0

    # ------------------------------------------------------------------
    # rendering helpers
    # ------------------------------------------------------------------
    def _render_task_table(self, tasks: List[Task]) -> None:
        if not tasks:
            print("暂无任务")
            return

        self._last_displayed_tasks = list(tasks)

        def fmt_status(status: Status) -> str:
            if status == Status.DONE:
                return f"{Fore.GREEN}{status.value}{Style.RESET_ALL}"
            if status == Status.IN_PROGRESS:
                return f"{Fore.YELLOW}{status.value}{Style.RESET_ALL}"
            return status.value

        table = [
            [
                idx,
                t.id[:SHORT_ID_LEN],
                t.title,
                t.priority.value,
                fmt_status(t.status),
                t.updated_at.strftime("%Y-%m-%d %H:%M"),
            ]
            for idx, t in enumerate(tasks, start=1)
        ]
        headers = ["No.", "Short ID", "Title", "Priority", "Status", "Updated"]
        print(tabulate(table, headers=headers, tablefmt="pretty"))

    def _resolve_task_id(self, identifier: str) -> str:
        ident = identifier.strip()
        if not ident:
            raise TaskMasterException("任务 ID 不能为空")
        if ident.isdigit():
            index = int(ident)
            source = self._last_displayed_tasks or self.service.list_tasks()
            if not source:
                raise TaskMasterException("当前没有任何任务")
            if index < 1 or index > len(source):
                raise TaskMasterException(f"任务序号超出范围（1-{len(source)}）")
            return str(source[index - 1].id)

        ident_lower = ident.lower()
        matching = [
            str(t.id)
            for t in self.service.list_tasks()
            if str(t.id).lower().startswith(ident_lower)
        ]
        if len(matching) == 1:
            return matching[0]
        if not matching:
            raise TaskMasterException(f"找不到以 {identifier} 开头的任务 ID")
        raise TaskMasterException(
            f"存在多个以 {identifier} 开头的任务，请输入更完整的 ID"
        )
