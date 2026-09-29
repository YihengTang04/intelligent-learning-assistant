@echo off
chcp 65001
echo ======================================
echo   深度学习知识管理系统 启动脚本
echo   执行命令: streamlit run main.py
echo ======================================
echo.

:: 优先尝试streamlit命令
streamlit run main.py

:: 如果上面执行失败，使用python -m方式兜底
if %errorlevel% neq 0 (
    echo streamlit命令未找到，尝试使用python -m streamlit启动
    python -m streamlit run main.py
)

pause
