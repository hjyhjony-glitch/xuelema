$r = Invoke-RestMethod -Uri 'https://api.github.com/repos/hjyhjony-glitch/xuelema/actions/workflows/flutter.yml/runs?per_page=5' -Headers @{'Accept'='application/vnd.github.v3+json'}
if ($r.workflow_runs.Count -eq 0) {
    Write-Output "无构建"
} else {
    foreach ($run in $r.workflow_runs) {
        Write-Output "构建号: $($run.run_number), 状态: $($run.status), 结论: $($run.conclusion)"
    }
}
