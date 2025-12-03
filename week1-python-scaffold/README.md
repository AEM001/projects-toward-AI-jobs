# Week 1: 个人任务管理 CLI 工具 (TaskMaster)

## 📋 项目概述

**TaskMaster** 是一个命令行任务管理工具，让你可以通过终端快速管理日常任务。通过开发这个实用工具，你将学习 Python 工程化的核心技能：项目结构、日志系统、异常处理、数据持久化、CLI 开发等。

### 🎬 项目演示
```bash
# 添加任务
$ python task.py add "完成 Python 项目" --priority high

# 列出所有任务
$ python task.py list
ID  | 任务                    | 优先级 | 状态      | 创建时间
1   | 完成 Python 项目        | high   | pending   | 2024-12-03 10:00

# 完成任务
$ python task.py done 1

# 删除任务
$ python task.py delete 1
```

## 🎯 项目目标

### 功能目标
1. **任务增删改查** - 添加、删除、更新、查询任务
2. **任务状态管理** - pending（待办）、in_progress（进行中）、done（已完成）
3. **优先级设置** - low、medium、high 三个级别
4. **数据持久化** - 使用 JSON 文件存储任务数据
5. **日志记录** - 记录所有操作日志，便于调试和审计
6. **友好的 CLI** - 清晰的命令行界面和帮助信息

### 工程化目标
1. **标准项目结构** - 符合 Python 最佳实践的目录组织
2. **完整日志系统** - 文件日志 + 控制台输出
3. **异常处理机制** - 统一的错误处理和友好的错误提示
4. **配置管理** - 可配置的数据存储路径、日志级别等
5. **单元测试** - 核心功能的测试覆盖
6. **完整文档** - 使用说明和开发文档

### 学习成果
- ✅ 开发一个完整的实用 CLI 工具
- ✅ 掌握 Python 项目的标准结构
- ✅ 实现企业级日志系统
- ✅ 学会数据持久化（JSON）
- ✅ 掌握 argparse 命令行开发
- ✅ 学习单元测试编写
- ✅ 建立可复用的项目模板

## 📁 项目结构

```
taskmaster/
├── README.md                 # 项目说明文档
├── requirements.txt          # 项目依赖列表
├── .gitignore               # Git 忽略文件配置
├── task.py                  # 主程序入口（快捷启动）
├── config/                  # 配置文件目录
│   ├── __init__.py
│   ├── settings.py          # 应用配置（数据路径、日志级别等）
│   └── logging_config.py    # 日志配置
├── src/                     # 源代码目录
│   ├── __init__.py
│   ├── cli.py               # 命令行接口（argparse）
│   ├── models/              # 数据模型
│   │   ├── __init__.py
│   │   └── task.py          # Task 类定义
│   ├── services/            # 业务逻辑层
│   │   ├── __init__.py
│   │   └── task_service.py  # 任务管理服务
│   ├── storage/             # 数据持久化
│   │   ├── __init__.py
│   │   └── json_storage.py  # JSON 存储实现
│   └── utils/               # 工具模块
│       ├── __init__.py
│       ├── logger.py        # 日志工具
│       └── exceptions.py    # 自定义异常
├── tests/                   # 测试目录
│   ├── __init__.py
│   ├── test_task_model.py   # 测试 Task 模型
│   ├── test_task_service.py # 测试任务服务
│   └── test_storage.py      # 测试存储功能
├── docs/                    # 文档目录
│   ├── usage.md             # 使用说明
│   └── development.md       # 开发指南
├── data/                    # 数据存储目录（运行时生成）
│   └── tasks.json           # 任务数据文件
└── logs/                    # 日志输出目录（运行时生成）
    └── taskmaster.log       # 应用日志
```

## � 7 天学习计划（每天 2-3 小时）

### Day 1: 项目初始化 + 数据模型（周一）
**学习重点**: 项目结构、Python 类设计、数据模型  
**今日目标**: 搭建项目骨架，创建 Task 数据模型

#### 任务清单
- [ ] 创建项目目录结构
- [ ] 配置 `.gitignore` 和 `requirements.txt`
- [ ] 初始化 Git 仓库
- [ ] 创建 `Task` 类（models/task.py）
  - 属性：id, title, priority, status, created_at, updated_at
  - 方法：to_dict(), from_dict()
- [ ] 编写 Task 模型的单元测试

**学习资料**:
- [Python 类和对象](https://docs.python.org/3/tutorial/classes.html)
- [dataclass 装饰器](https://docs.python.org/3/library/dataclasses.html)
- [datetime 模块](https://docs.python.org/3/library/datetime.html)

**交付物**: 可运行的 Task 类 + 测试通过

---

### Day 2: 数据持久化（周二）
**学习重点**: JSON 文件操作、数据序列化、文件 I/O  
**今日目标**: 实现任务数据的保存和读取

#### 任务清单
- [ ] 创建 `JSONStorage` 类（storage/json_storage.py）
  - 方法：save(), load(), exists()
- [ ] 实现任务数据的 JSON 序列化
- [ ] 处理文件不存在的情况
- [ ] 编写存储层的单元测试
- [ ] 学习 Python 异常处理基础

**学习资料**:
- [JSON 模块](https://docs.python.org/3/library/json.html)
- [文件操作](https://docs.python.org/3/tutorial/inputoutput.html#reading-and-writing-files)
- [pathlib 模块](https://docs.python.org/3/library/pathlib.html)
- [异常处理](https://docs.python.org/3/tutorial/errors.html)

**交付物**: 可以保存和读取任务数据的存储层

---

### Day 3: 业务逻辑层（周三）
**学习重点**: 服务层设计、CRUD 操作、ID 生成  
**今日目标**: 实现任务管理的核心业务逻辑

#### 任务清单
- [ ] 创建 `TaskService` 类（services/task_service.py）
  - add_task(title, priority) - 添加任务
  - get_task(task_id) - 获取单个任务
  - list_tasks(status=None) - 列出任务（可按状态筛选）
  - update_task_status(task_id, status) - 更新状态
  - delete_task(task_id) - 删除任务
- [ ] 实现自动 ID 生成（UUID 或自增 ID）
- [ ] 编写业务逻辑的单元测试

**学习资料**:
- [UUID 模块](https://docs.python.org/3/library/uuid.html)
- [列表推导式](https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions)
- [filter() 函数](https://docs.python.org/3/library/functions.html#filter)

**交付物**: 完整的任务管理服务层

---

### Day 4: 日志系统 + 异常处理（周四）
**学习重点**: logging 模块、自定义异常、装饰器  
**今日目标**: 为项目添加完整的日志和异常处理

#### 任务清单
- [ ] 创建日志配置（config/logging_config.py）
  - 配置文件日志（logs/taskmaster.log）
  - 配置控制台日志
  - 设置日志格式和级别
- [ ] 创建日志工具类（utils/logger.py）
- [ ] 定义自定义异常（utils/exceptions.py）
  - TaskNotFoundException
  - InvalidTaskStatusException
  - StorageException
- [ ] 在 Service 层集成日志和异常
- [ ] 创建应用配置（config/settings.py）

**学习资料**:
- [logging 模块](https://docs.python.org/3/library/logging.html)
- [logging HOWTO](https://docs.python.org/3/howto/logging.html)
- [自定义异常](https://docs.python.org/3/tutorial/errors.html#user-defined-exceptions)
- [装饰器基础](https://realpython.com/primer-on-python-decorators/)

**交付物**: 带日志和异常处理的完整后端

---

### Day 5: CLI 命令行界面（周五）
**学习重点**: argparse 模块、子命令、命令行参数  
**今日目标**: 实现完整的命令行界面

#### 任务清单
- [ ] 创建 CLI 模块（src/cli.py）
- [ ] 使用 argparse 实现子命令：
  - `add` - 添加任务
  - `list` - 列出任务
  - `done` - 标记完成
  - `delete` - 删除任务
  - `update` - 更新任务状态
- [ ] 添加命令行参数（--priority, --status, --all）
- [ ] 实现漂亮的表格输出
- [ ] 创建主入口文件（task.py）

**学习资料**:
- [argparse 教程](https://docs.python.org/3/howto/argparse.html)
- [argparse 文档](https://docs.python.org/3/library/argparse.html)
- [tabulate 库](https://pypi.org/project/tabulate/) - 表格输出
- [colorama 库](https://pypi.org/project/colorama/) - 彩色输出

**交付物**: 可用的命令行工具

---

### Day 6: 测试完善 + 代码优化（周六）
**学习重点**: pytest 框架、测试覆盖率、代码重构  
**今日目标**: 完善测试，优化代码质量

#### 任务清单
- [ ] 安装和配置 pytest
- [ ] 完善所有模块的单元测试
- [ ] 编写集成测试
- [ ] 运行测试覆盖率分析（pytest-cov）
- [ ] 代码重构和优化
- [ ] 添加类型注解（Type Hints）
- [ ] 代码风格检查（flake8 或 black）

**学习资料**:
- [pytest 文档](https://docs.pytest.org/)
- [pytest 教程](https://realpython.com/pytest-python-testing/)
- [Type Hints](https://docs.python.org/3/library/typing.html)
- [PEP 8 风格指南](https://pep8.org/)
- [Black 代码格式化](https://black.readthedocs.io/)

**交付物**: 测试覆盖率 > 80% 的高质量代码

---

### Day 7: 文档编写 + 项目发布（周日）
**学习重点**: 文档编写、Git 工作流、项目打包  
**今日目标**: 完善文档，发布到 GitHub

#### 任务清单
- [ ] 完善 README.md
  - 项目介绍
  - 安装说明
  - 使用示例
  - 功能特性
- [ ] 编写使用文档（docs/usage.md）
- [ ] 编写开发文档（docs/development.md）
- [ ] 添加代码注释和 docstring
- [ ] 提交代码到 GitHub
- [ ] 编写 CHANGELOG.md
- [ ] 打标签发布 v1.0.0

**学习资料**:
- [编写好的 README](https://www.makeareadme.com/)
- [Markdown 语法](https://www.markdownguide.org/)
- [Git 基础](https://git-scm.com/book/zh/v2)
- [语义化版本](https://semver.org/lang/zh-CN/)
- [Python Docstring](https://peps.python.org/pep-0257/)

**交付物**: 完整的 GitHub 项目，可供他人使用

## 📚 学习资料

### Python 项目结构
- [Python 官方打包指南](https://packaging.python.org/tutorials/packaging-projects/)
- [The Hitchhiker's Guide to Python - Structuring Your Project](https://docs.python-guide.org/writing/structure/)
- [Real Python - Python Application Layouts](https://realpython.com/python-application-layouts/)
- [Python 项目结构最佳实践](https://docs.python-guide.org/writing/structure/)

### Logging 日志系统
- [Python 官方 logging 文档](https://docs.python.org/3/library/logging.html)
- [Python Logging HOWTO](https://docs.python.org/3/howto/logging.html)
- [Real Python - Logging in Python](https://realpython.com/python-logging/)
- [Logging Cookbook](https://docs.python.org/3/howto/logging-cookbook.html)
- [loguru - 现代化日志库](https://github.com/Delgan/loguru)

### 异常处理
- [Python 官方异常文档](https://docs.python.org/3/tutorial/errors.html)
- [Real Python - Python Exceptions](https://realpython.com/python-exceptions/)
- [Python 异常处理最佳实践](https://docs.python.org/3/tutorial/errors.html#user-defined-exceptions)

### 环境管理
- [venv - Python 虚拟环境](https://docs.python.org/3/library/venv.html)
- [pip 和 requirements.txt](https://pip.pypa.io/en/stable/user_guide/#requirements-files)
- [python-dotenv - 环境变量管理](https://github.com/theskumar/python-dotenv)
- [Poetry - 现代依赖管理工具](https://python-poetry.org/)

### CLI 开发
- [argparse 官方文档](https://docs.python.org/3/library/argparse.html)
- [Click - 命令行框架](https://click.palletsprojects.com/)
- [Typer - 现代 CLI 框架](https://typer.tiangolo.com/)
- [Building Command Line Tools with Python](https://realpython.com/command-line-interfaces-python-argparse/)

### 测试
- [pytest 官方文档](https://docs.pytest.org/)
- [unittest - Python 标准测试库](https://docs.python.org/3/library/unittest.html)
- [Real Python - Testing in Python](https://realpython.com/python-testing/)

### Git 和版本控制
- [gitignore.io - .gitignore 生成器](https://www.toptal.com/developers/gitignore)
- [GitHub Python .gitignore 模板](https://github.com/github/gitignore/blob/main/Python.gitignore)

### 代码质量
- [PEP 8 - Python 代码风格指南](https://pep8.org/)
- [Black - 代码格式化工具](https://github.com/psf/black)
- [Flake8 - 代码检查工具](https://flake8.pycqa.org/)
- [mypy - 类型检查工具](http://mypy-lang.org/)

## 🚀 快速开始

### 环境准备
```bash
# 1. 克隆项目（或创建新目录）
cd week1-python-scaffold

# 2. 创建虚拟环境
python3 -m venv venv

# 3. 激活虚拟环境
# macOS/Linux:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# 4. 安装依赖
pip install -r requirements.txt
```

### 使用示例
```bash
# 添加任务
python task.py add "学习 Python logging 模块" --priority high

# 列出所有任务
python task.py list

# 只列出待办任务
python task.py list --status pending

# 标记任务完成
python task.py done 1

# 更新任务状态
python task.py update 1 --status in_progress

# 删除任务
python task.py delete 1

# 查看帮助
python task.py --help
python task.py add --help
```

### 运行测试
```bash
# 运行所有测试
pytest tests/

# 运行特定测试文件
pytest tests/test_task_model.py

# 查看测试覆盖率
pytest --cov=src tests/

# 详细输出
pytest -v tests/
```

## 💡 每日学习建议

### 学习方法
1. **先看文档，再写代码** - 每天先阅读相关学习资料（30分钟）
2. **边学边测** - 写一个功能就写一个测试
3. **遇到问题先搜索** - 学会使用官方文档和 Stack Overflow
4. **代码提交规范** - 每完成一个功能就 commit 一次
5. **写注释和文档** - 养成良好的文档习惯

### 时间分配建议（每天 2-3 小时）
- **阅读学习** (30-45 分钟) - 阅读文档和教程
- **编码实现** (60-90 分钟) - 实现当天的功能
- **测试调试** (30-45 分钟) - 编写测试和调试代码
- **总结记录** (15 分钟) - 记录学习笔记和遇到的问题

### 遇到困难怎么办？
1. **查看错误信息** - Python 的错误提示很友好，仔细阅读
2. **使用 print 调试** - 在关键位置打印变量值
3. **查阅官方文档** - Python 文档非常详细
4. **搜索问题** - Google/Stack Overflow
5. **简化问题** - 把复杂问题拆解成小问题
6. **参考示例代码** - 学习别人的实现方式

## 📦 项目交付标准

### Week 1 最终交付物
1. **完整的项目代码**
   - 所有功能模块实现完整
   - 代码结构清晰，符合 Python 规范
   - 包含完整的 `__init__.py` 文件

2. **测试覆盖**
   - 单元测试覆盖率 > 80%
   - 所有测试通过
   - 包含测试文档

3. **文档完善**
   - README.md（项目介绍、安装、使用）
   - docs/usage.md（详细使用说明）
   - docs/development.md（开发指南）
   - 代码注释和 docstring

4. **Git 仓库**
   - 提交到 GitHub
   - 清晰的 commit 历史
   - 合理的 .gitignore
   - 标签 v1.0.0

### 功能验收清单
- [ ] 可以添加任务（带优先级）
- [ ] 可以列出所有任务
- [ ] 可以按状态筛选任务
- [ ] 可以标记任务完成
- [ ] 可以删除任务
- [ ] 任务数据持久化（重启后数据不丢失）
- [ ] 日志记录到文件
- [ ] 友好的错误提示
- [ ] 命令行帮助信息完整
- [ ] 所有测试通过

### 代码质量标准
- [ ] 遵循 PEP 8 代码风格
- [ ] 函数和类有 docstring
- [ ] 变量命名清晰易懂
- [ ] 没有硬编码的配置
- [ ] 异常处理完善
- [ ] 日志记录合理

## 🎓 进阶扩展（Week 2+）

完成基础项目后，可以考虑以下扩展功能：

### 功能扩展
- [ ] 任务标签系统（tags）
- [ ] 任务截止日期和提醒
- [ ] 任务搜索功能
- [ ] 任务统计报表
- [ ] 导出任务（CSV/Excel）
- [ ] 任务分类/项目管理

### 技术扩展
- [ ] 使用 SQLite 数据库替代 JSON
- [ ] 使用 Click 框架重构 CLI
- [ ] 添加配置文件支持（YAML/TOML）
- [ ] 实现插件系统
- [ ] 添加 Web 界面（Flask）
- [ ] 容器化部署（Docker）
- [ ] CI/CD 集成（GitHub Actions）
- [ ] 发布到 PyPI

## 📝 注意事项

1. **代码规范**：遵循 PEP 8 代码风格
2. **注释文档**：关键函数添加 docstring
3. **版本控制**：及时提交代码，写清楚 commit message
4. **模块化设计**：保持代码的可维护性和可扩展性
5. **安全性**：不要在代码中硬编码敏感信息

## 🤝 贡献指南

本项目是学习项目，欢迎：
- 提出改进建议
- 报告问题和 bug
- 分享你的实现方案
- 添加新的功能模块

---

**开始时间**: Week 1  
**预计完成**: 7 天  
**难度等级**: ⭐⭐⭐ (中级)

祝你学习愉快！🚀
