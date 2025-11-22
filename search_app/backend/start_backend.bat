@echo off
REM Сбрасываем переменную ELASTICSEARCH_USE_SSL для использования HTTP
set ELASTICSEARCH_USE_SSL=
cd /d %~dp0
echo Запуск бэкенда на HTTP...
python main.py
pause

