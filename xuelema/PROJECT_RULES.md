# 项目规则

## 1. 项目目录结构

**唯一项目目录**: `E:\xueliao\xuelema\`

所有代码、测试、配置都在此目录下，不创建子项目目录。

```
E:\xueliao\xuelema\
├── lib\                ← 所有代码
├── test\               ← 所有测试
├── .github\            ← CI/CD配置
├── docs\               ← 项目文档
├── CHANGELOG.md        ← 变更记录
└── VERSION.md          ← 版本管理规范
```

---

## 2. 任务自动化流程

### 标准流程
```
代码修复/开发 → ARC代码审核 → DEV构建验证 → ASS记录归档
     ↓               ↓              ↓              ↓
  RUNBOT-DEV    RUNBOT-ARC     RUNBOT-DEV    RUNBOT-ASS
```

### 启动命令
```bash
# 开始新任务
python E:\OpenClaw_Workspace\scripts\task_coordinator.py --start

# 查看状态
python E:\OpenClaw_Workspace\scripts\task_coordinator.py --status

# 重置流程
python E:\OpenClaw_Workspace\scripts\task_coordinator.py --reset
```

### 状态文件
`E:\OpenClaw_Workspace\memory\projects\学了吗APP\.task_status.json`

---

## 3. 版本迭代管理原则

### 版本号规则
**格式**: `主版本.次版本.修订版本` (Semantic Versioning)

```
版本号示例: 1.0.0

- 主版本 (1): 重大功能变更或架构调整
- 次版本 (0): 新功能添加
- 修订版本 (0): Bug修复或小改进
```

### 版本更新流程

**步骤1**: 更新版本号
编辑 `pubspec.yaml`:
```yaml
version: 1.1.0
```

**步骤2**: 记录变更
更新 `CHANGELOG.md`:
```markdown
## [1.1.0] - 2026-02-19

### 新增
- xxx功能

### 修复
- xxx问题

### 优化
- xxx改进
```

**步骤3**: 提交代码
```bash
git add -A
git commit -m "feat: version 1.1.0 - 新增功能描述"
git push
```

**步骤4**: 打标签
```bash
git tag v1.1.0
git push origin v1.1.0
```

### 发布检查清单
- [ ] 更新 `pubspec.yaml` 版本号
- [ ] 更新 `CHANGELOG.md`
- [ ] 运行测试 (`flutter test`)
- [ ] 构建验证 (`flutter build apk --debug`)
- [ ] ARC 代码审核通过
- [ ] 更新文档
- [ ] 创建 Git Tag

---

## 4. 团队职责

| 助手 | 模型 | 职责 |
|------|------|------|
| RUNBOT | MiniMax-m2.1 | 任务接收、团队协调 |
| RUNBOT-ARC | DeepSeek-V3.2 | 任务分析、代码审核 |
| RUNBOT-DEV | DeepSeek-V3.2 | 技术实施、代码开发 |
| RUNBOT-ASS | MiniMax-m2.1 | 文档管理、记录归档 |

---

## 5. 定时汇报

**时间**: 08:00 / 12:00 / 18:00 (喀布尔时区)  
**渠道**: 飞书群组 `oc_cbb996632b133b482c6c1b531bbd63dc`

---

*最后更新: 2026-02-18*
