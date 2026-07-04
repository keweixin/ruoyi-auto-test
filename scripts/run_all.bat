@echo off
chcp 65001 >nul
setlocal

REM ============================================================
REM  run_all.bat  ——  全量运行 155 条测试并生成 Allure 结果
REM ============================================================

cd /d "%~dp0\.."

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] 未找到 .venv\Scripts\python.exe，请先创建虚拟环境并安装依赖。
    echo         参考 docs\项目运行说明.md 第三节。
    exit /b 1
)

echo ============================================================
echo  开始全量运行测试 (API 75 + UI 60 + Integration 20 = 155)...
echo ============================================================
.venv\Scripts\python.exe -m pytest -q --alluredir=reports\allure-results
set RC=%ERRORLEVEL%

echo.
if %RC% equ 0 (
    echo [OK] 全量测试全部通过。可运行 scripts\open_allure.bat 查看报告。
) else (
    echo [FAIL] 存在失败用例，退出码 %RC%。
)
exit /b %RC%
