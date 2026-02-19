# 长期记忆 - 重要经验总结

## 1. 历史会话清理（2026-02-19）

### 问题背景
- 存在大量过期会话（22-26个活跃会话）
- 多个DEV/ARC/ASS重复会话
- 会话管理混乱

### 解决方案

#### 步骤1：备份原文件
```powershell
Copy-Item "sessions.json" "sessions.json.backup_$(Get-Date -Format 'yyyy-MM-dd_HH-mm')"
```

#### 步骤2：使用PowerShell脚本清理
```powershell
# 读取JSON
$json = Get-Content $jsonPath | ConvertFrom-Json

# 保留的会话类型：
# 1. group (群聊会话)
# 2. main (主会话)
# 3. cron (定时任务，最新1个)
# 4. subagent (团队成员，最新各1个)

# 删除其他会话
foreach ($key in $sessions.Name) {
    if ($keepKeys -notcontains $key) {
        $json.PSObject.Properties.Remove($key)
    }
}

# 保存
$json | ConvertTo-Json -Depth 10 | Set-Content $jsonPath
```

#### 步骤3：重启Gateway
```bash
openclaw gateway restart
```

#### 步骤4：唤醒团队成员
```bash
# 唤醒ARC（青岩）
sessions_spawn(label="RUNBOT-ARC", task="高级分析、代码审核")

# 唤醒DEV（笑天）
sessions_spawn(label="RUNBOT-DEV", task="技术实施、代码开发")

# 唤醒ASS（笑瑶）
sessions_spawn(label="RUNBOT-ASS", task="文档管理、全程记录")
```

### 清理结果
| 指标 | 结果 |
|------|------|
| 清理前 | 22-26个会话 |
| 清理后 | 3-6个核心会话 |
| 删除会话 | 338个（总计） |
| 保留会话 | 6个（group + main + cron + 3个团队） |

### 关键经验
1. **先备份后操作**：任何修改前先备份原文件
2. **保留核心会话**：只保留当前活跃的会话
3. **脚本自动化**：使用PowerShell脚本确保一致性
4. **重启生效**：清理后必须重启Gateway
5. **重新唤醒**：团队成员需要重新唤醒

### 命令速查
```bash
# 查看当前会话
openclaw sessions --active 60

# 清理脚本位置
E:\OpenClaw_Workspace\scripts\cleanup_sessions.ps1

# 执行清理
powershell -ExecutionPolicy Bypass -File "E:\OpenClaw_Workspace\scripts\cleanup_sessions.ps1"

# 重启Gateway
openclaw gateway restart
```

---

## 2. GitHub Actions Workflow修复（2026-02-19）

### 问题
- 本地构建成功（APK 118MB）
- GitHub Actions失败：工作目录错误

### 解决方案
在 `.github/workflows/auto-build.yml` 的所有jobs中添加：
```yaml
working-directory: xuelema
```

### 修复的jobs
- analyze
- test
- build-android
- self-heal
- notify
- report

### 提交记录
- 提交ID: `984db657e`
- 提交信息: `fix: add working-directory for all jobs in GitHub Actions`

---

## 3. 团队职责分工（2026-02-19）

### RUNBOT（主协调）
- 任务协调，不执行代码操作
- 负责唤醒团队成员
- 执行自检清单（5项）

### RUNBOT-ARC（青岩）
- 高级分析、代码审核
- 问题根因分析
- 修复方案制定
- DEV代码质量把关

### RUNBOT-DEV（笑天）
- 技术实施、代码开发
- Git操作
- 系统构建

### RUNBOT-ASS（笑瑶）
- 文档管理、全程记录
- 跟踪项目进度
- 记录关键决策

---

## 4. 自检清单（每次启动必查）

### 5项自检
1. **团队唤醒状态** - 检查所有成员是否在线
2. **记忆文件读取** - 读取 SOUL.md、USER.md、memory/YYYY-MM-DD.md（当天+昨天）、MEMORY.md
3. **职责边界检查** - 确认无越权操作
4. **当前任务状态** - 汇报进行中的任务
5. **任务分配流程** - 确认任务已分配

### 自检汇报格式
```
## 🚨 完整自检（全部5项）

### 1. 团队唤醒状态 ✅
| 助手 | 状态 |
|------|------|
| RUNBOT-ARC | ✅ 已就位 |
| RUNBOT-DEV | ✅ 已就位 |
| RUNBOT-ASS | ✅ 已就位 |

### 2. 记忆文件读取 ✅
- ✅ SOUL.md
- ✅ USER.md
- ✅ memory/2026-02-19.md（当天）
- ✅ memory/2026-02-18.md（如存在）
- ✅ MEMORY.md

### 3. 职责边界检查 ✅
- ✅ 无越权操作

### 4. 当前任务状态
| 项目 | 状态 |
|------|------|
| 历史会话清理 | ✅ 完成 |
| 团队唤醒 | ✅ 全部就位 |
| GitHub Actions | ⏳ 等待构建 |

### 5. 任务分配流程 ✅
- ✅ 主会话 → 协调
- ✅ DEV → 技术
- ✅ ARC → 分析
- ✅ ASS → 记录
```

---

## 5. 项目状态追踪

### 学了吗APP（xuelema）
| 项目 | 状态 |
|------|------|
| 本地构建 | ✅ APK 118MB |
| GitHub Actions | ⏳ 等待验证 |
| Workflow修复 | ✅ 已推送 |

---

## 6. 定时任务管理（2026-02-19）

### 全面自动化检查
- **任务ID**: `0164a05d-d6ac-43bf-a237-6798e87ddb7a`
- **任务名称**: 全面自动化检查
- **运行频率**: 每2小时（7200000ms）
- **检查内容**:
  1. GitHub Actions 构建状态
  2. 助手在线状态
  3. 大模型使用情况
  4. 自动唤醒离线助手
  5. 更新任务文档
  6. 报告到飞书群组

### 更新定时任务命令
```bash
# 查看所有定时任务
cron list

# 更新任务运行间隔（改为2小时）
cron update --jobId "0164a05d-d6ac-43bf-a237-6798e87ddb7a" --schedule "everyMs:7200000"
```

### 其他定时任务
| 任务 | 频率 | 说明 |
|------|------|------|
| GitHub Actions自动检查 | 3分钟 | 检查构建状态 |
| 自动推送GitHub仓库 | 10分钟 | 自动推送代码 |
| Wake RUNBOT-ARC | 30分钟 | 唤醒ARC |
| Wake RUNBOT-DEV | 30分钟 | 唤醒DEV |
| Wake RUNBOT-ASS | 30分钟 | 唤醒ASS |
| AI助手状态监控V10 | 30分钟 | 状态监控 |
| 会话自动清理 | 12小时 | 清理旧会话 |
| Daily Session Check | 每天凌晨2点 | 会话归档 |
| Daily Communication Summary | 每天 | 沟通总结 |
| Weekly Session Cleanup | 每周日凌晨3点 | 周清理 |
| Memory Backup to Feishu | 每周 | 备份到飞书 |

---

*最后更新: 2026-02-19*
