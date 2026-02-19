# Persistent Memory System - 快速使用指南

## 安装

直接将 `persistent_memory.py` 复制到你的项目中即可使用。

## 基本用法

### 方法 1: 使用类实例

```python
from persistent_memory import Memory

# 创建实例（指定存储路径）
mem = Memory("./data/memory")

# 保存数据
mem.save("user_name", "张三")
mem.save("user_age", 25)
mem.save("user_preferences", {"theme": "dark", "lang": "zh"})

# 加载数据
name = mem.load("user_name")  # "张三"
age = mem.load("user_age")   # 25

# 检查存在
if mem.exists("user_name"):
    print("用户已登录")

# 列出所有键
keys = mem.list_keys()

# 获取所有数据
all_data = mem.list_all()

# 删除数据
mem.delete("user_name")

# 清空所有
mem.clear()
```

### 方法 2: 使用便捷函数（全局默认实例）

```python
from persistent_memory import save, load, delete, list_keys

# 直接调用，无需创建实例
save("theme", "dark")
theme = load("theme")
delete("theme")
```

## 高级功能

### 设置过期时间

```python
# 保存 1 小时后过期的数据
mem.save("temp_code", "123456", expire_seconds=3600)

# 加载时自动检查过期
value = mem.load("temp_code")  # 1小时后返回 None
```

### 带元数据加载

```python
meta = mem.load_with_meta("user_name")
if meta:
    print(f"值: {meta['value']}")
    print(f"创建时间: {meta['created_at']}")
    print(f"过期时间: {meta['expire_at']}")
```

### 清理过期数据

```python
# 手动清理过期数据
count = mem.cleanup_expired()
print(f"清理了 {count} 条过期数据")
```

### 自动清理过期

```python
# 每次操作前自动清理（可选）
mem = Memory("./data/memory")
mem.cleanup_expired()  # 在 save/load 前调用
```

## 存储结构

数据存储在 `./data/memory/` 目录下：

```
data/memory/
├── _index.json          # 索引文件
├── user_name.json       # 键值对文件
├── user_age.json
└── ...
```

每個 `.json` 文件内容示例：

```json
{
  "key": "user_name",
  "value": "张三",
  "created_at": "2024-01-15T10:30:00.000000",
  "expire_at": null
}
```

## 线程安全

所有操作都使用线程锁，可以在多线程环境中安全使用。

## 命令行工具

```bash
# 保存
python persistent_memory.py save user_name "张三"

# 加载
python persistent_memory.py load user_name

# 列出所有
python persistent_memory.py list

# 清空
python persistent_memory.py clear
```

## OpenClaw Skill 集成

创建 `SKILL.md`：

```markdown
# Memory Skill

## 描述
本地持久化记忆系统

## 文件
- `persistent_memory.py`: 核心模块

## 依赖
无（纯 Python 标准库）

## 配置
```python
from persistent_memory import Memory

# 默认存储路径
mem = Memory("./data/memory")
```

## 使用示例
```python
mem.save("context", {...})
```

## 清理策略
自动清理过期数据（可选配置）
```

## 最佳实践

1. **键名规范**：使用有意义的键名，如 `user_name`, `session_id`
2. **定期清理**：在应用启动时调用 `cleanup_expired()`
3. **备份**：重要数据建议单独备份 `data/memory/` 目录
4. **错误处理**：检查返回值，避免程序因文件权限等问题崩溃
