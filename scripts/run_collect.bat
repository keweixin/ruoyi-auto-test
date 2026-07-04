@echo off
chcp 65001 >nul
setlocal

REM ============================================================
REM  run_collect.bat  ——  只收集用例不执行（验证用例可正确加载）
REM ============================================================

cd /d "%~dp0\.."

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] 未找到 .venv\Scripts\python.exe，请先创建虚拟环境并安装依赖。
    echo         参考 docs\项目运行说明.md 第三节。
    exit /b 1
)

echo ============================================================
echo  收集用例（不执行）...
echo ============================================================
.venv\Scripts\python.exe -m pytest --collect-only -q
set RC=%ERRORLEVEL%

echo.
if %RC% equ 0 (
    echo [OK] 用例收集成功。期望 155 条。
) else (
    echo [FAIL] 用例收集失败，退出码 %RC%，请检查导入错误或语法错误。
)
exit /b %RC%
