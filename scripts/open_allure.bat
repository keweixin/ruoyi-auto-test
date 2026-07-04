@echo off
chcp 65001 >nul
setlocal

REM ============================================================
REM  open_allure.bat  ——  生成并打开 Allure 报告
REM ============================================================

cd /d "%~dp0\.."

if not exist "reports\allure-results" (
    echo [ERROR] 未找到 reports\allure-results，请先运行测试生成结果。
    echo         可运行 scripts\run_all.bat 执行全量测试。
    exit /b 1
)

REM 优先使用 PATH 中的 allure，否则尝试常见安装位置
where allure >nul 2>nul
if %ERRORLEVEL% equ 0 (
    set "ALLURE_CMD=allure"
) else (
    if exist "E:\allure-2.37.0\allure-2.37.0\bin\allure.bat" (
        set "ALLURE_CMD=E:\allure-2.37.0\allure-2.37.0\bin\allure.bat"
    ) else (
        echo [ERROR] 未找到 allure 命令。请安装 Allure 并加入 PATH。
        echo         参考 https://allurereport.org/docs/install/
        exit /b 1
    )
)

echo ============================================================
echo  生成 Allure 静态报告...
echo ============================================================
%ALLURE_CMD% generate reports\allure-results -o reports\allure-report --clean
set RC=%ERRORLEVEL%
if %RC% neq 0 (
    echo [FAIL] 报告生成失败，退出码 %RC%。
    exit /b %RC%
)

echo ============================================================
echo  打开报告（启动本地服务，浏览器自动弹出）...
echo  按 Ctrl+C 关闭服务。
echo ============================================================
%ALLURE_CMD% open reports\allure-report
exit /b 0
