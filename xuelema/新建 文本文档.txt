@echo off
chcp 65001 > nul
echo ========================================
echo 正在修复 Flutter VS 2026 生成器问题...
echo ========================================

:: 1. 清理缓存
echo [1/4] 清理项目缓存...
flutter clean

:: 2. 获取依赖
echo [2/4] 重新获取依赖...
flutter pub get

:: 3. 生成临时文件（即使报错也会生成 needed_config.cmake）
echo [3/4] 生成临时编译文件...
flutter build windows --debug --verbose > nul 2>&1

:: 4. 替换生成器版本（VS 2019 → VS 2026）
echo [4/4] 修改 CMake 生成器配置...
powershell -Command "if (Test-Path 'windows/flutter/ephemeral/generated_config.cmake') { (Get-Content 'windows/flutter/ephemeral/generated_config.cmake') -replace 'Visual Studio 16 2019', 'Visual Studio 18 2026' | Set-Content 'windows/flutter/ephemeral/generated_config.cmake'); echo '✅ 配置修改成功' } else { echo '❌ 未找到 generated_config.cmake，跳过修改' }"

echo.
echo ========================================
echo 修复完成！现在运行：flutter run -d windows
echo ========================================
pause