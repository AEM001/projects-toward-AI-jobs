# Day 4 指导：日志系统 + 异常处理（不写代码版）

## 目标（你今天要交付什么）
把“可观察性”和“可控失败”补齐：
- 任何一次业务操作（add/get/list/update/delete、storage save/load）都有一致的日志。
- 所有常见失败场景都有明确的自定义异常类型，调用方可以区分处理。
- 配置集中化：日志配置、应用配置（例如日志级别、日志路径、数据文件路径）。

交付物：
- `config/logging_config.py`
- `src/utils/logger.py`
- `src/utils/exceptions.py`
- `config/settings.py`
- 你现有的 `src/services/task_service.py` / `src/storage/json_storage.py` 接入日志与异常（只改行为，不改功能）

## 你现有代码的“边界”在哪里（方便你放日志/异常）
当前结构（从你项目里看到的）：
- Model：`src/models/task.py`（`Task`、`Status`、`Priority`）
- Service：`src/services/task_service.py`（对外的业务入口）
- Storage：`src/storage/json_storage.py`（文件读写 + JSON 序列化）

建议的责任边界（今天的改动都围绕这个）：
- **Service 层**：
  - 做输入校验（title、status 等）。
  - 做“找不到任务”的判定。
  - 记录“业务事件日志”（谁调用了什么、结果是什么）。
  - 将底层 storage 的失败包装/转译为更稳定的异常（例如统一成 `StorageException`）。
- **Storage 层**：
  - 只负责 I/O（读写文件、JSON encode/decode）。
  - 发生 I/O、JSON 格式错误、权限问题等，抛出 `StorageException`（或其细分）。
  - 记录“技术日志”（读写哪个文件、读写成功与否、异常堆栈）。
- **调用方（Day5 CLI 或未来 API）**：
  - 捕获自定义异常，给用户输出友好信息。
  - 不在 CLI 层写业务规则。

## 1) 应用配置（config/settings.py）你要定义哪些配置项
目的：不要把路径、级别散落在各处。

建议配置项（常用且够用）：
- `APP_NAME`: str（例如 `taskmaster`）
- `LOG_LEVEL`: str（默认 `INFO`）
- `LOG_DIR`: str（默认 `logs`）
- `LOG_FILE`: str（默认 `logs/taskmaster.log`）
- `DATA_FILE`: str（默认 `data/task.json`，给 `JSONStorage` 用）

可选（加分但不必须）：
- `ENV`: str（dev/prod）
- `LOG_TO_CONSOLE`: bool

要求：
- 这些配置应该被日志配置和 storage 初始化共同使用。

## 2) 日志配置（config/logging_config.py）要做什么
目标：一次配置，全项目统一使用。

你要配置两类 handler：
- **FileHandler**：写到 `logs/taskmaster.log`
- **StreamHandler**：输出到控制台

你要统一：
- **log level**（例如开发 INFO，调试用 DEBUG）
- **format**（建议包含：时间、级别、logger 名称、消息、可选 request_id/trace_id）

建议日志格式字段（够用且常见）：
- `asctime`
- `levelname`
- `name`
- `message`

你要提供的“对外接口”（只需要在文件里暴露这种函数/入口即可）：
- `setup_logging() -> None`

调用时机建议：
- Day5 CLI 的主入口一启动就调用一次 `setup_logging()`
- 测试里可以选择不启用文件日志或改成临时目录（后续再做）

## 3) 日志工具（src/utils/logger.py）你要提供什么
目标：让业务代码不用重复写 `logging.getLogger(__name__)` 的样板。

建议你提供一个简单接口：
- `get_logger(name: str | None = None)`
  - name 默认用调用模块名（或者你统一用 `APP_NAME`）

使用约定：
- Service、Storage 各自拿一个 logger：
  - `task_service` 用一个 logger
  - `json_storage` 用一个 logger

## 4) 自定义异常（src/utils/exceptions.py）你要定义哪些
目标：让上层可以“按类型处理”，而不是靠字符串匹配。

建议的异常层次（越简单越好）：
- `TaskMasterException(Exception)`：项目基类异常
- `TaskNotFoundException(TaskMasterException)`
  - 场景：Service 层按 id 找不到任务
  - 建议携带：`task_id`
- `InvalidTaskStatusException(TaskMasterException)`
  - 场景：调用方给了非法 status（例如字符串不在枚举里、或 None）
  - 建议携带：`status`
- `StorageException(TaskMasterException)`
  - 场景：任何文件 I/O、JSON parse、序列化失败
  - 建议携带：`operation`（save/load）、`path`、`original_exception`

你今天要做的关键点：
- **Service 层不要再抛 `ValueError("Task not found")`**，而是抛 `TaskNotFoundException`。
- **Storage 层不要裸抛 `Exception/IOError/ValueError` 给上层**，统一转成 `StorageException`（底层错误保留在 cause 里）。

## 5) Service 层要集成哪些日志与异常（以 TaskService 为准）
你现有 `TaskService` 方法：
- `add_task(title, priority=...) -> Task`
- `get_task(task_id) -> Task`
- `list_tasks(status=None) -> List[Task]`
- `update_task_status(task_id, status) -> Task`
- `delete_task(task_id) -> None`

### 5.1 需要记录哪些日志（建议“事件日志”）
每个 public 方法建议至少打两条：
- **开始**（INFO/DEBUG）：
  - 方法名
  - 关键输入（例如 `task_id`，但避免敏感信息；title 可以打长度或截断）
- **成功结束**（INFO）：
  - 结果（新增 task_id、更新后的 status、删除成功等）

失败场景：
- **业务失败（可预期）**：
  - `TaskNotFoundException`、`InvalidTaskStatusException`：建议 `warning` 级别（不是 error）
- **系统失败（不可预期）**：
  - `StorageException`、未知异常：建议 `error` 级别，并记录异常堆栈（`exc_info=True` 的语义）

### 5.2 Service 层异常策略（你要做到的行为）
- 找不到任务：抛 `TaskNotFoundException(task_id)`
- status 非法：抛 `InvalidTaskStatusException(status)`
- storage.save/load 失败：捕获底层异常并抛 `StorageException`（或让 storage 已经抛出，你在 service 只做“补充上下文日志”）

建议的统一原则：
- **Service 层只抛“你定义的异常”给上层**（基于 `TaskMasterException`），避免上层到处处理 `ValueError/IOError`。

## 6) Storage 层要集成哪些日志与异常（以 JSONStorage 为准）
你现有 `JSONStorage` 方法：
- `save(tasks) -> None`
- `load() -> List[Task]`
- `exists() -> bool`
- `clear() -> None`
- `get_file_path() -> str`

### 6.1 需要记录哪些日志（建议“技术日志”）
- `save`：
  - 写入路径
  - 写入任务数量
  - 成功/失败
- `load`：
  - 读取路径
  - 读取到的任务数量
  - 文件不存在时是否返回空
  - JSON decode 失败等要带堆栈

### 6.2 Storage 层异常策略
- 任何异常都不要直接 `raise Exception("保存任务失败")` 这种通用异常给上层。
- 统一转成 `StorageException`，并保留原始异常作为 cause（便于排查）。

## 7) 调用方（Day5 CLI）该怎么用（提前给你接口对齐）
虽然 CLI 是 Day5，但你 Day4 做的异常/日志要让 CLI 易用。

建议 CLI 主入口流程：
- 启动：
  - 调 `setup_logging()`
  - 初始化 `JSONStorage(file_path=settings.DATA_FILE)`
  - 初始化 `TaskService(storage)`
- 执行命令：
  - 捕获 `TaskMasterException`：
    - 给用户友好提示（例如“找不到任务 id=xxx”）
    - 退出码可选（后续再做）
  - 捕获未知异常：
    - 记录 error 日志（带堆栈）
    - 给用户一个通用提示

## 8) 你完成后怎么自查（不依赖写新测试）
建议你手动跑一遍这些场景（Day5 CLI 没做也没关系，你可以用简单脚本或 REPL 调 service）：
- add 正常
- get 正常
- get 不存在的 id：
  - 应该抛 `TaskNotFoundException`
  - 日志里应该是 warning（或你定义的级别）
- update 不存在的 id：同上
- storage 文件写入路径不可写 / JSON 被破坏：
  - 应该抛 `StorageException`
  - 日志里应该有 error + 堆栈

## 9) 你今天最终“对外承诺”的接口清单（总结）
你新增/变更后，对外（给 CLI/未来 API）可依赖的接口应当是：
- `config.settings`：提供日志与数据路径等配置常量
- `config.logging_config.setup_logging() -> None`
- `src.utils.logger.get_logger(name=None)`
- `src.utils.exceptions`：
  - `TaskMasterException`
  - `TaskNotFoundException`
  - `InvalidTaskStatusException`
  - `StorageException`
- `TaskService`：方法签名不一定要变，但**异常类型会从 ValueError 迁移到你的自定义异常**

