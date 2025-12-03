# mkdir 命令
- **常用选项**：  
  - `-p`：递归创建多级目录，避免报错。  
    ```bash
    mkdir -p /home/user/project/src
    ```
  - `-m`：指定目录权限。  
    ```bash
    mkdir -m 755 newdir
    ```
  - `-v`：显示创建过程。  
    ```bash
    mkdir -v testdir
    ```

### 🔗 与 mkdir 相关的命令
这些命令常与目录管理配合使用：  

| 命令 | 功能 | 示例 |
|------|------|------|
| `rmdir` | 删除空目录 | `rmdir olddir` |
| `rm -r` | 删除目录及其内容 | `rm -r project` |
| `ls` | 查看目录内容 | `ls -l` |
| `cd` | 切换目录 | `cd /home/user` |
| `pwd` | 显示当前目录路径 | `pwd` |
| `touch` | 创建空文件（常与 mkdir 配合） | `touch file.txt` |

---
# conda
### 🛠️ 常用命令
- **删除指定环境**  
  ```bash
  conda remove --name myenv --all
  ```
  - `--name myenv` 指定要删除的环境名称  
  - `--all` 表示删除该环境中的所有包和环境本身  

- **另一种写法（等价）**  
  ```bash
  conda env remove -n myenv
  ```
  这里 `-n` 是 `--name` 的缩写。  

---

### 🔍 辅助命令
- **查看已有环境**  
  ```bash
  conda env list
  ```
  或  
  ```bash
  conda info --envs
  ```
  可以确认你要删除的环境名称。  

- **确认删除**  
  删除后再运行 `conda env list`，确保该环境已不在列表中。  

---

### 📌 注意事项
- 删除环境不会影响其他环境或 base 环境。  
- 如果你在某个环境中运行删除命令，最好先退出该环境：  
  ```bash
  conda deactivate
  ```  

---

- to_dict 方法把对象属性转成字典，方便存储或传输（例如 JSON）。
- 常见用途：
  - 保存到数据库
  - 转换为 JSON 通过 API 传输
  - 日志记录

- created_at.isoformat() → 把 datetime 转成 ISO 8601 格式字符串，例如 "2025-12-03T10:50:00".
- datetime.fromisoformat(...) → 把 ISO 格式字符串解析回 datetime 对象。
- 这是 Python 3.7+ 的标准方法，常用于序列化/反序列化时间。

---
啊，明白了，你是第一次看到 Python 里方法上面有个 **@** 符号的写法。这个其实叫 **装饰器 (decorator)**。  

---

## 🌀 什么是装饰器？
- 在 Python 中，`@something` 的语法就是在函数或方法定义前应用一个装饰器。  
- 装饰器本质上是一个 **函数或类**，它接收一个函数/方法作为输入，然后返回一个“增强过的”函数/方法。  
- 常见用途：修改函数行为、注册函数、增加功能（比如日志、权限检查、缓存）。

---
## 📌 在你代码里的两个例子
1. **`@classmethod`**
   - 把一个普通方法变成 **类方法**。
   - 类方法的第一个参数是 `cls`（类本身），而不是 `self`（实例）。
   - 用途：通常作为工厂方法，用类来创建对象。
   - 示例：
     ```python
     class Task:
         @classmethod
         def from_dict(cls, data):
             return cls(**data)
     ```
     这里 `cls` 就是 `Task` 类本身。

2. **`@staticmethod`**（你没用到，但常见）
   - 定义一个和类相关但不依赖实例或类的函数。
   - 没有 `self` 或 `cls` 参数。
   - 示例：
     ```python
     class Math:
         @staticmethod
         def add(a, b):
             return a + b
     ```

3. **`@property`**（也很常见）
   - 把方法伪装成属性调用。
   - 示例：
     ```python
     class User:
         def __init__(self, name):
             self._name = name

         @property
         def name(self):
             return self._name
     ```
     使用时：`user.name` 而不是 `user.name()`。

---

## 🧩 装饰器的工作原理
等价于：
```python
def func(...):
    ...

func = decorator(func)
```
所以 `@classmethod` 就是：
```python
from_dict = classmethod(from_dict)
```

---

## 🚀 总结
- `@` 开头的是 **装饰器**，用来改变函数/方法的行为。  
- 在你的例子里：
  - `@classmethod` → 让方法接收类作为第一个参数，用于工厂模式。  
  - 普通方法（没有 @）→ 接收实例作为第一个参数。  
