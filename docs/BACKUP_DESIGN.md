# 核心文件备份机制设计

## 1. 备份文件列表

需要自动备份的核心文件：
- `MEMORY.md` - 长期记忆（主会话专用，包含API Keys）
- `USER.md` - 用户信息
- `SOUL.md` - 身份定义
- `AGENTS.md` - 工作区规范

---

## 2. 备份存储位置

```
E:\OpenClaw_Workspace\
├── backups/                          # 备份根目录
│   ├── core_files/                   # 核心文件备份
│   │   ├── 2026-02-20/               # 按日期分文件夹
│   │   │   ├── 04-00-00/            # 按时间分（可选）
│   │   │   │   ├── MEMORY.md
│   │   │   │   ├── USER.md
│   │   │   │   ├── SOUL.md
│   │   │   │   ├── AGENTS.md
│   │   │   │   └── manifest.json     # 备份清单
│   │   │   └── ...
│   │   ├── latest/                   # 最新备份（软链接或复制）
│   │   │   ├── MEMORY.md → ../2026-02-20/04-00-00/MEMORY.md
│   │   │   ├── USER.md
│   │   │   ├── SOUL.md
│   │   │   ├── AGENTS.md
│   │   │   └── manifest.json
│   │   └── archive/                  # 历史版本归档
│   │       └── ...
│   └── backup_manifest.json          # 全局备份清单
```

---

## 3. 备份格式

### 3.1 manifest.json（单次备份清单）

```json
{
  "backup_id": "backup_2026-02-20_04-00-00",
  "timestamp": "2026-02-20T04:00:00+04:30",
  "files": [
    {
      "name": "MEMORY.md",
      "size": 7957,
      "md5": "a1b2c3d4e5f6...",
      "sha256": "..."
    },
    {
      "name": "USER.md",
      "size": 477,
      "md5": "...",
      "sha256": "..."
    },
    {
      "name": "SOUL.md",
      "size": 1673,
      "md5": "...",
      "sha256": "..."
    },
    {
      "name": "AGENTS.md",
      "size": 7869,
      "md5": "...",
      "sha256": "..."
    }
  ],
  "created_by": "RUNBOT-DEV",
  "version": "1.0"
}
```

### 3.2 backup_manifest.json（全局备份索引）

```json
{
  "last_backup": "2026-02-20T04:00:00+04:30",
  "total_backups": 42,
  "backups": [
    {
      "backup_id": "backup_2026-02-20_04-00-00",
      "timestamp": "2026-02-20T04:00:00+04:30",
      "file_count": 4,
      "restore_command": "restore backup_2026-02-20_04-00-00"
    },
    {
      "backup_id": "backup_2026-02-19_04-00-00",
      "timestamp": "2026-02-19T04:00:00+04:30",
      "file_count": 4,
      "restore_command": "restore backup_2026-02-19_04-00-00"
    }
  ]
}
```

---

## 4. 自动触发条件

### 4.1 触发条件（优先级从高到低）

| 条件 | 触发方式 | 说明 |
|------|----------|------|
| **文件修改检测** | 自动 | 检测到核心文件被修改时触发 |
| **定时任务** | Cron | 每天 04:00 AM 自动备份 |
| **会话开始** | 自动 | 主会话开始时执行增量备份 |
| **手动触发** | 命令 | `./scripts/backup.sh --force` |
| **版本清理** | 定时 | 保留最近30天 + 每周1个 + 每月1个 |

### 4.2 文件修改检测脚本

```powershell
# scripts/watch_core_files.ps1
# 核心文件修改监控脚本

$coreFiles = @(
    "MEMORY.md",
    "USER.md",
    "SOUL.md",
    "AGENTS.md"
)

$workspaceRoot = "E:\OpenClaw_Workspace"
$lastHashFile = "$workspaceRoot\.last_hash.json"

function Get-FileHash {
    param([string]$Path)
    $hash = Get-FileHash $Path -Algorithm SHA256 | Select-Object -ExpandProperty Hash
    return $hash.ToLower()
}

function Test-FilesChanged {
    $currentHashes = @{}
    foreach ($file in $coreFiles) {
        $path = Join-Path $workspaceRoot $file
        if (Test-Path $path) {
            $currentHashes[$file] = Get-FileHash $path
        }
    }

    if (-not (Test-Path $lastHashFile)) {
        return $true, $currentHashes
    }

    $lastHashes = Get-Content $lastHashFile | ConvertFrom-Json
    $changed = $false

    foreach ($file in $coreFiles) {
        if (-not $lastHashes.$file -or $currentHashes.$file -ne $lastHashes.$file) {
            $changed = $true
            break
        }
    }

    return $changed, $currentHashes
}

# 检测并触发备份
$changed, $hashes = Test-FilesChanged
if ($changed) {
    # 触发备份
    & "$workspaceRoot\scripts\backup_core.ps1" -ModifiedFilesOnly
    # 保存新的hash
    $hashes | ConvertTo-Json | Set-Content $lastHashFile
}
```

### 4.3 定时备份脚本

```powershell
# scripts/scheduled_backup.ps1
# 定时备份脚本（通过Windows Task Scheduler调用）

param(
    [switch]$Force,
    [switch]$Daily,
    [switch]$Weekly,
    [switch]$Monthly
)

$workspaceRoot = "E:\OpenClaw_Workspace"
$backupRoot = "$workspaceRoot\backups\core_files"

# 创建备份目录
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$backupPath = Join-Path $backupRoot $timestamp

if (-not (Test-Path $backupPath)) {
    New-Item -ItemType Directory -Path $backupPath -Force | Out-Null
}

# 备份核心文件
$coreFiles = @("MEMORY.md", "USER.md", "SOUL.md", "AGENTS.md")
$manifest = @{
    backup_id = "backup_$timestamp"
    timestamp = (Get-Date -Format "o")
    files = @()
    created_by = "RUNBOT-DEV"
    version = "1.0"
}

foreach ($file in $coreFiles) {
    $srcPath = Join-Path $workspaceRoot $file
    $dstPath = Join-Path $backupPath $file

    if (Test-Path $srcPath) {
        Copy-Item $srcPath $dstPath -Force

        $fileInfo = @{
            name = $file
            size = (Get-Item $srcPath).Length
            md5 = (Get-FileHash $srcPath -Algorithm MD5).Hash.ToLower()
            sha256 = (Get-FileHash $srcPath -Algorithm SHA256).Hash.ToLower()
        }
        $manifest.files += $fileInfo
    }
}

# 保存manifest
$manifest | ConvertTo-Json -Depth 10 | Set-Content (Join-Path $backupPath "manifest.json")

# 更新全局索引
$globalManifestPath = Join-Path $backupRoot "backup_manifest.json"
if (Test-Path $globalManifestPath) {
    $globalManifest = Get-Content $globalManifestPath | ConvertFrom-Json
} else {
    $globalManifest = @{
        last_backup = $null
        total_backups = 0
        backups = @()
    }
}

$globalManifest.last_backup = $manifest.timestamp
$globalManifest.total_backups += 1
$globalManifest.backups = @(@{
    backup_id = $manifest.backup_id
    timestamp = $manifest.timestamp
    file_count = $manifest.files.Count
    restore_command = "restore $($manifest.backup_id)"
}) + $globalManifest.backups

$globalManifest | ConvertTo-Json -Depth 5 | Set-Content $globalManifestPath

# 清理旧版本
. "$workspaceRoot\scripts\cleanup_old_backups.ps1"

Write-Host "Backup completed: $backupPath"
```

---

## 5. 一键恢复功能

### 5.1 恢复脚本

```powershell
# scripts/restore_backup.ps1
# 一键恢复脚本

param(
    [Parameter(Mandatory=$false)]
    [string]$BackupId,
    
    [Parameter(Mandatory=$false)]
    [switch]$List,
    
    [Parameter(Mandatory=$false)]
    [switch]$Latest
)

$workspaceRoot = "E:\OpenClaw_Workspace"
$backupRoot = "$workspaceRoot\backups\core_files"
$globalManifestPath = Join-Path $backupRoot "backup_manifest.json"

if (-not (Test-Path $globalManifestPath)) {
    Write-Error "No backup manifest found!"
    exit 1
}

$globalManifest = Get-Content $globalManifestPath | ConvertFrom-Json

# 列出所有备份
if ($List) {
    Write-Host "`n=== Available Backups ===`n" -ForegroundColor Cyan
    $globalManifest.backups | ForEach-Object {
        Write-Host "Backup ID: $($_.backup_id)" -ForegroundColor Yellow
        Write-Host "  Timestamp: $($_.timestamp)"
        Write-Host "  Files: $($_.file_count)"
        Write-Host "  Restore: restore $($_.backup_id)`n"
    }
    exit 0
}

# 确定恢复哪个备份
$backupPath = $null

if ($Latest) {
    # 恢复最新备份
    $latestBackup = $globalManifest.backups[0]
    $backupPath = Join-Path $backupRoot $latestBackup.backup_id.Replace("backup_", "")
} elseif ($BackupId) {
    $backupPath = Join-Path $backupRoot $BackupId.Replace("backup_", "")
} else {
    Write-Host "Please specify a backup ID or use -Latest" -ForegroundColor Yellow
    Write-Host "Usage:" -ForegroundColor Cyan
    Write-Host "  restore -Latest        # Restore latest backup"
    Write-Host "  restore backup_2026-02-20_04-00-00  # Restore specific backup"
    Write-Host "  restore -List          # List all backups"
    exit 1
}

if (-not (Test-Path $backupPath)) {
    Write-Error "Backup not found: $backupPath"
    exit 1
}

# 读取manifest
$manifestPath = Join-Path $backupPath "manifest.json"
if (-not (Test-Path $manifestPath)) {
    Write-Error "Backup manifest not found!"
    exit 1
}

$manifest = Get-Content $manifestPath | ConvertFrom-Json

# 确认恢复
Write-Host "`n=== Backup Details ===" -ForegroundColor Cyan
Write-Host "Backup ID: $($manifest.backup_id)"
Write-Host "Timestamp: $($manifest.timestamp)"
Write-Host "Files: $($manifest.files.Count)"
Write-Host "`nFiles to restore:"
$manifest.files | ForEach-Object { Write-Host "  - $($_.name)" }

Write-Host "`n" -ForegroundColor Red
Read-Host "Are you sure you want to restore? (y/n)"
if ($_ -ne 'y') {
    Write-Host "Restore cancelled."
    exit 0
}

# 执行恢复
Write-Host "`nRestoring files..." -ForegroundColor Cyan

foreach ($file in $manifest.files) {
    $srcPath = Join-Path $backupPath $file.name
    $dstPath = Join-Path $workspaceRoot $file.name

    if (Test-Path $srcPath) {
        Copy-Item $srcPath $dstPath -Force
        Write-Host "  ✓ Restored: $($file.name)"
    } else {
        Write-Warning "  ✗ File not found in backup: $($file.name)"
    }
}

Write-Host "`n✅ Restore completed successfully!" -ForegroundColor Green
Write-Host "Restored $($manifest.files.Count) files from $($manifest.backup_id)"
```

### 5.2 使用方式

```powershell
# 列出所有备份
.\scripts\restore_backup.ps1 -List

# 恢复最新备份
.\scripts\restore_backup.ps1 -Latest

# 恢复指定备份
.\scripts\restore_backup.ps1 backup_2026-02-20_04-00-00
```

---

## 6. 版本保留策略

```powershell
# scripts/cleanup_old_backups.ps1
# 旧版本清理脚本

param(
    [int]$DailyKeep = 7,      # 保留最近7天
    [int]$WeeklyKeep = 4,     # 保留最近4周
    [int]$MonthlyKeep = 12    # 保留最近12个月
)

$backupRoot = "E:\OpenClaw_Workspace\backups\core_files"
$backups = Get-ChildItem -Path $backupRoot -Directory | Where-Object { $_.Name -match '^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}$' } | Sort-Object Name -Descending

if ($backups.Count -le ($DailyKeep + $WeeklyKeep + $MonthlyKeep)) {
    Write-Host "No cleanup needed. Total backups: $($backups.Count)"
    exit 0
}

# 按日期分组
$today = Get-Date
$dailyCutoff = $today.AddDays(-$DailyKeep)
$weeklyCutoff = $today.AddDays(-($DailyKeep + 7 * $WeeklyKeep))
$monthlyCutoff = $today.AddDays(-($DailyKeep + 7 * 4 * $MonthlyKeep))

# 分类备份
$toDelete = @()
$kept = @{}

foreach ($backup in $backups) {
    $dateStr = $backup.Name -replace '_\d{2}-\d{2}-\d{2}$', ''
    $backupDate = [DateTime]::ParseExact($dateStr, 'yyyy-MM-dd', $null)

    if ($backupDate -ge $dailyCutoff) {
        # 每天保留
        $kept[$backup.Name] = "daily"
    } elseif ($backupDate -ge $weeklyCutoff) {
        # 每周保留1个
        $weekStr = $backupDate.ToString('yyyy-ww')
        if (-not $kept.ContainsKey($weekStr)) {
            $kept[$backup.Name] = "weekly"
            $kept[$weekStr] = $backup.Name
        } else {
            $toDelete += $backup.FullName
        }
    } elseif ($backupDate -ge $monthlyCutoff) {
        # 每月保留1个
        $monthStr = $backupDate.ToString('yyyy-MM')
        if (-not $kept.ContainsKey($monthStr)) {
            $kept[$backup.Name] = "monthly"
            $kept[$monthStr] = $backup.Name
        } else {
            $toDelete += $backup.FullName
        }
    } else {
        # 超过保留期限
        $toDelete += $backup.FullName
    }
}

# 删除旧备份
foreach ($path in $toDelete) {
    Remove-Item -Path $path -Recurse -Force
    Write-Host "Deleted: $path"
}

Write-Host "`nCleanup completed. Deleted $($toDelete.Count) old backups."
Write-Host "Kept $($kept.Count) backups."
```

---

## 7. 完整集成

### 7.1 主备份脚本

```powershell
# scripts/backup_core.ps1
# 核心文件备份主脚本

param(
    [switch]$Force,
    [switch]$ModifiedFilesOnly,
    [switch]$List,
    [switch]$Restore,
    [string]$BackupId
)

$ErrorActionPreference = "Stop"

$workspaceRoot = "E:\OpenClaw_Workspace"
$backupRoot = "$workspaceRoot\backups\core_files"
$coreFiles = @("MEMORY.md", "USER.md", "SOUL.md", "AGENTS.md")

# 确保备份目录存在
if (-not (Test-Path $backupRoot)) {
    New-Item -ItemType Directory -Path $backupRoot -Force | Out-Null
}

switch ($true) {
    $List { . "$PSScriptRoot\restore_backup.ps1" -List }
    $Restore { . "$PSScriptRoot\restore_backup.ps1" -BackupId $BackupId }
    default { . "$PSScriptRoot\scheduled_backup.ps1" -Force:$Force }
}
```

### 7.2 使用示例

```powershell
# 手动触发完整备份
.\scripts\backup_core.ps1 -Force

# 检测修改并增量备份
.\scripts\backup_core.ps1 -ModifiedFilesOnly

# 列出所有备份
.\scripts\backup_core.ps1 -List

# 恢复备份
.\scripts\backup_core.ps1 -Restore -BackupId backup_2026-02-20_04-00-00
.\scripts\backup_core.ps1 -Restore -Latest
```

---

## 8. 定时任务设置

```powershell
# scripts/setup_scheduled_task.ps1
# 设置定时备份任务

$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File `"E:\OpenClaw_Workspace\scripts\scheduled_backup.ps1`""
$trigger = New-ScheduledTaskTrigger -Daily -At "4:00 AM"
$settings = New-ScheduledTaskSettingsSet -RunOnlyIfNetworkAvailable

Register-ScheduledTask -TaskName "OpenClaw_Backup" -Action $action -Trigger $trigger -Settings $settings -Description "OpenClaw core files daily backup"

Write-Host "Scheduled task 'OpenClaw_Backup' created. Runs daily at 4:00 AM."
```

---

## 9. 设计总结

| 特性 | 实现方案 |
|------|----------|
| **存储位置** | `backups/core_files/` |
| **备份格式** | JSON manifest + 原始文件 |
| **自动触发** | 文件修改检测 + 定时Cron |
| **历史版本** | 按日期分文件夹，保留策略 |
| **一键恢复** | `restore -Latest` 或指定ID |
| **文件完整性** | MD5/SHA256 校验 |

---

## 10. 下一步实现

1. ✅ 备份机制设计完成
2. ⬜ 创建 `scripts/backup_core.ps1`
3. ⬜ 创建 `scripts/restore_backup.ps1`
4. ⬜ 创建 `scripts/cleanup_old_backups.ps1`
5. ⬜ 创建 `scripts/watch_core_files.ps1`
6. ⬜ 设置Windows定时任务
7. ⬜ 首次运行备份
