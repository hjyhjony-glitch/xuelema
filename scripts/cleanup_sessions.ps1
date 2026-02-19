# 清理历史会话脚本
# 目标：只保留最新的活跃会话

$jsonPath = "C:\Users\y\.openclaw\agents\main\sessions\sessions.json"
$backupPath = "C:\Users\y\.openclaw\agents\main\sessions\sessions.json.backup_$(Get-Date -Format 'yyyy-MM-dd_HH-mm')"

# 1. 备份
Copy-Item $jsonPath $backupPath
Write-Host "✅ 备份完成: $backupPath"

# 2. 读取JSON
$json = Get-Content $jsonPath | ConvertFrom-Json
$sessions = $json.PSObject.Properties | Where-Object { $_.Name -ne "agent:main:subagent:437b790a-ce06-4735-9129-154dff825a09" }

# 3. 获取所有subagent keys
$subagentKeys = $sessions.Name | Where-Object { $_ -like "*:subagent:*" }

Write-Host "`n发现 $subagentKeys.Count 个 subagent 会话"

# 4. 分类统计
$devKeys = $subagentKeys | Where-Object { $_ -like "*:subagent:*dev*" }
$arcKeys = $subagentKeys | Where-Object { $_ -like "*:subagent:*arc*" }
$assKeys = $subagentKeys | Where-Object { $_ -like "*:subagent:*ass*" }

Write-Host "`nDEV: $($devKeys.Count) 个"
Write-Host "ARC: $($arcKeys.Count) 个"
Write-Host "ASS: $($assKeys.Count) 个"

# 5. 找出每个类型中updatedAt最大的（最新的）
function Get-LatestKey {
    param($keys)
    $latestKey = $null
    $latestTime = 0
    foreach ($key in $keys) {
        $session = $json.$key
        if ($session.updatedAt -gt $latestTime) {
            $latestTime = $session.updatedAt
            $latestKey = $key
        }
    }
    return $latestKey
}

$latestDev = Get-LatestKey $devKeys
$latestArc = Get-LatestKey $arcKeys
$latestAss = Get-LatestKey $assKeys

Write-Host "`n最新会话："
Write-Host "DEV: $latestDev"
Write-Host "ARC: $latestArc"
Write-Host "ASS: $latestAss"

# 6. 构建要保留的keys列表
$keepKeys = @(
    "agent:main:feishu:group:oc_962aed74063bf1621ebe0387d94d6c54"  # 飞书群
    "agent:main:main"  # 主会话
    $latestDev
    $latestArc
    $latestAss
)

# 7. 保留主会话和cron任务（保留最近活跃的）
$cronKeys = $sessions.Name | Where-Object { $_ -like "*:cron:*" }
$latestCron = Get-LatestKey $cronKeys
$keepKeys += $latestCron

Write-Host "`n保留的会话keys："
$keepKeys | ForEach-Object { Write-Host $_ }

# 8. 删除不保留的会话
$removedCount = 0
foreach ($key in $sessions.Name) {
    if ($keepKeys -notcontains $key) {
        $json.PSObject.Properties.Remove($key)
        $removedCount++
    }
}

# 9. 保存
$json | ConvertTo-Json -Depth 10 | Set-Content $jsonPath
Write-Host "`n✅ 清理完成！删除了 $removedCount 个会话"
Write-Host "保留了 $($keepKeys.Count) 个活跃会话"
