
# Day4：Config / Logging / Exception 学习笔记（结合本项目）

## 1) Config（配置）是什么？为什么要单独放？

### 核心概念
- **配置**：项目中“可能会变”的参数（路径、级别、开关），不要散落在业务代码里。
- **集中管理**：把配置放在一个地方，后续改动只改一处。

### 在本项目中对应哪些文件
- `config/settings.py`
  - `APP_NAME`：应用名称（用于日志默认 logger 名称、日志文件命名）
  - `BASE_DIR`：项目根目录路径（用于拼接 log/data 路径）
  - `LOG_LEVEL`：日志级别（INFO/DEBUG/WARNING/ERROR）
  - `LOG_DIR` / `LOG_FILE`：日志目录与日志文件路径
  - `DATA_FILE`：默认数据文件路径（`data/task.json`）

### 你能用配置做什么
- 改 `LOG_LEVEL = "DEBUG"`：日志更详细（适合排查问题）
- 改 `DATA_FILE`：切换数据文件位置，不用动 storage/service 代码

---

## 2) Logging（日志）是什么？和 print 有什么区别？

### 核心概念
- **日志的目的**：让你能知道程序“发生了什么”，尤其是线上/运行结束之后的排查。
- **logging vs print**：
  - logging 有**级别**（debug/info/warning/error）
  - logging 可以同时输出到**控制台 + 文件**
  - logging 可以统一**格式**（时间、模块名、级别）

### 日志级别（记住大概含义就够）
- `DEBUG`：非常详细的调试信息（平时可关）
- `INFO`：正常业务流程信息（最常用）
- `WARNING`：可预期但不理想的情况（例如没找到任务）
- `ERROR`：系统错误/异常（例如 I/O 失败、JSON 损坏）

### 在本项目中对应哪些文件
- `config/logging_config.py`
  - `setup_logging()`：程序启动时调用一次，完成 logging 的统一配置
  - 配置了：
    - **StreamHandler**：输出到控制台
    - **FileHandler**：输出到 `logs/taskmaster.log`
    - **formatter**：统一日志格式：时间 + 级别 + logger 名 + message

- `src/utils/logger.py`
  - `get_logger(name=None)`：拿 logger 的小工具
  - `name` 不传时，默认用 `settings.APP_NAME`（例如 `taskmaster`）

### logging 常见“语法”你需要理解的部分（实际使用过程中的方法）
- `logger.info("msg")`：记录一条 INFO 日志
- `logger.info("x=%s", x)`：用 `%s` 占位符传参（推荐写法）
  - 好处：如果日志级别不够导致这条日志不输出，logging 不会提前做字符串拼接（更省性能）
- `logger.warning("...", exc_info=True)`：把异常堆栈（traceback）也输出

---

## 3) Exception（异常）是什么？为什么要自定义？

### 核心概念
- **异常**：程序遇到错误/不满足规则时，用 `raise` 抛出，打断当前流程。
- **异常处理**：上层用 `try/except` 捕获，决定怎么处理（提示用户/重试/退出）。
- **自定义异常**：用“类型”区分错误，而不是只靠字符串。

### 在本项目中对应哪些文件
- `src/utils/exceptions.py`
  - `TaskMasterException`：项目异常基类
  - `TaskNotFoundException`：找不到任务（业务问题）
  - `InvalidTaskStatusException`：状态参数不合法（业务问题）
  - `StorageException`：存储相关失败（系统问题，例如 I/O/JSON 损坏）

### 谁负责抛异常？谁负责捕获？
- **Service 层**（`src/services/task_service.py`）
  - 找不到任务时抛 `TaskNotFoundException`
  - 入参不合法时抛 `InvalidTaskStatusException`

- **Storage 层**（`src/storage/json_storage.py`）
  - 读写文件/JSON parse/数据字段缺失时抛 `StorageException`
  - 并用 `logger.error(..., exc_info=True)` 记录堆栈

- **入口层（main/CLI）**
  - 捕获 `TaskMasterException`，给用户友好提示 + 记录日志
  - 捕获未知 `Exception`，记录 error + 堆栈

---

## 4) 结合本项目：一次运行时到底发生了什么？

以 `demo_main.py` 为例（你已经跑过，能看到输出）：

### 运行流程（按顺序）
1. `demo_main.py` 调用 `setup_logging()`
   - 读取 `settings.LOG_LEVEL / LOG_FILE`
   - 初始化控制台 + 文件日志
2. 初始化 `JSONStorage(settings.DATA_FILE)`
3. 初始化 `TaskService(storage)`
4. 调用 `service.add_task(...)`
   - service 打 INFO 日志（业务事件）
   - storage `load/save` 打 INFO 日志（技术事件）
5. 调用 `service.get_task("not-exist")`
   - service 先打 WARNING（没找到，属于可预期业务问题）
   - 然后 `raise TaskNotFoundException`
6. `demo_main.py` 用 `except TaskMasterException` 捕获
   - 再打一个 WARNING，并且 `exc_info=True` 输出 traceback（看到哪里 raise 的）

### 你看到的两种日志
- **普通日志**：只有一行 message（说明发生了什么）
- **带堆栈日志**：message + Traceback（说明从哪里一路调用到哪里出错）

---

## 5) 实战建议（你现在阶段的“最小掌握”）

你不需要把 logging/异常机制背下来，但建议至少做到：
- 看懂日志：能分辨 INFO/WARNING/ERROR
- 出错时看 traceback：能定位到是哪一个文件/哪一行 raise 的
- 知道边界：
  - 业务问题（找不到任务）一般是 `TaskNotFoundException`
  - 系统问题（读写/JSON）一般是 `StorageException`

## 异常基础知识

# 异常（Exception）基础知识：你需要知道的“最小一套”

异常可以理解成：**程序遇到问题时，用一种“标准化的方式”把错误往上抛，让上层决定怎么处理**。它比 `print("出错了")` 更强，因为可以分类型、可被捕获、还能保留出错位置（traceback）。

---

## 1) 异常是怎么产生的？
两种来源：

- **系统自动抛出**：比如除 0、文件不存在、JSON 解析失败等  
  - 例：[json.load](cci:1://file:///Users/Mac/code/project/week1-python-scaffold/src/storage/json_storage.py:8:4-20:35) 可能抛 `JSONDecodeError`
- **你主动抛出**：当业务规则不满足时你自己 `raise`  
  - 例：找不到任务就 `raise TaskNotFoundException(task_id)`

“抛出（raise）”的意思是：**当前函数立刻终止**，把控制权交给上层。

---

## 2) 异常怎么处理？（try / except / finally）
你需要知道三个关键字：

- **`try`**：把“可能出错”的代码包起来
- **`except`**：捕获某种异常类型并处理
- **`finally`**：不管是否出错都会执行（常用于清理资源，比如关闭文件/连接）

核心点：**except 是按“异常类型”匹配的**，不是按字符串。

---

## 3) Traceback（堆栈）是什么？
你运行 demo 时看到的 traceback：

- 它会告诉你：  
  - 从哪里调用到哪里  
  - 最终在哪一行 `raise` 的  
- 这是你排错最重要的线索。

你看到它通常是因为：
- 异常没被捕获（程序直接崩）
- 或你打日志时用了 `exc_info=True`（即使异常被捕获，也把堆栈打印出来）

---

## 4) 为什么要“单独一个文件定义异常类”？（你说的那个文件）
你项目里这个文件就是：

- [src/utils/exceptions.py](cci:7://file:///Users/Mac/code/project/week1-python-scaffold/src/utils/exceptions.py:0:0-0:0)

这里单独定义了一些类，比如：
- [TaskMasterException](cci:2://file:///Users/Mac/code/project/week1-python-scaffold/src/utils/exceptions.py:3:0-4:8)
- [TaskNotFoundException](cci:2://file:///Users/Mac/code/project/week1-python-scaffold/src/utils/exceptions.py:7:0-9:35)
- [InvalidTaskStatusException](cci:2://file:///Users/Mac/code/project/week1-python-scaffold/src/utils/exceptions.py:13:0-16:58)
- [StorageException](cci:2://file:///Users/Mac/code/project/week1-python-scaffold/src/utils/exceptions.py:19:0-23:33)

它们都是 Python 异常体系里的“异常类型”（本质上是继承 `Exception` 的类）。

### 为什么要单独放一个文件？
- **统一管理**：所有项目自定义错误类型集中在一处
- **可复用**：Service、Storage、未来 CLI 都能 import 用同一套异常
- **可区分处理**：上层可以写出很清晰的捕获逻辑  
  - 找不到任务 -> 提示用户换 id  
  - 存储失败 -> 提示查看日志/重试

### 在你这个项目里它是怎么用的？
- [TaskService](cci:2://file:///Users/Mac/code/project/week1-python-scaffold/src/services/task_service.py:13:0-79:70)（业务层）发现“任务不存在”时不再用 `ValueError`，而是：
  - `raise TaskNotFoundException(task_id)`
- [JSONStorage](cci:2://file:///Users/Mac/code/project/week1-python-scaffold/src/storage/json_storage.py:21:0-89:45)（存储层）读写/JSON 错误时统一：
  - `raise StorageException(... ) from e`
- [demo_main.py](cci:7://file:///Users/Mac/code/project/week1-python-scaffold/demo_main.py:0:0-0:0)（入口层）可以统一捕获：
  - `except TaskMasterException as e: ...`

---

## 5) 你现在阶段记住的“异常设计原则”（够用）
- **业务错误**（用户输入/业务规则导致）：用自定义异常（比如 [TaskNotFoundException](cci:2://file:///Users/Mac/code/project/week1-python-scaffold/src/utils/exceptions.py:7:0-9:35)）
- **系统错误**（文件/网络/JSON/权限）：用 [StorageException](cci:2://file:///Users/Mac/code/project/week1-python-scaffold/src/utils/exceptions.py:19:0-23:33) 这类异常，并记录堆栈
- **最上层（main/CLI）负责捕获并做用户提示**  
  - 底层不要“吞掉异常”（不要只 print 然后当没事发生）

---

