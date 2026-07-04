@echo off
chcp 65001 >nul
setlocal

REM ============================================================
REM  run_ui.bat  ——  只运行 UI 自动化测试并生成 Allure 结果
REM ============================================================

cd /d "%~dp0\.."

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] 未找到 .venv\Scripts\python.exe，请先创建虚拟环境并安装依赖。
    echo         参考 docs\项目运行说明.md 第三节。
    exit /b 1
)

echo ============================================================
echo  开始运行 UI 自动化测试 (60 条)...
echo  默认 headless，调试请加 --headed --slowmo 500
echo ============================================================
.venv\Scripts\python.exe -m pytest ui_auto\testcases -q --alluredir=reports\allure-results
set RC=%ERRORLEVEL%

echo.
if %RC% equ 0 (
    echo [OK] UI 测试全部通过。可运行 scripts\open_allure.bat 查看报告。
) else (
    echo [FAIL] UI 测试存在失败，退出码 %RC%。失败截图见 screenshots\，trace 见 traces\。
)
exit /b %RC%
