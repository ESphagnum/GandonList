@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
title WashiBot - Control Panel

:: Проверка зависимостей
where /q git || (
    echo [X] Git не установлен. Скачайте с: https://git-scm.com/downloads
    pause
    exit /b 1
)

:: Инициализация .env
if not exist ".env" (
    echo [i] Создаем .env файл...
    set /p GUILD_ID="[?] Введите ID вашего сервера: "
    set /p DEV_ROLE_ID="[?] Введите ID роли разработчика: "
    set /p ADMIN_ROLE_ID="[?] Введите ID роли админа: "
    set /p TOKEN="[?] Введите Токен бота: "
    set /p DB_HOST="[?] Введите Host вашего PostgreSQL (по умолчанию: localhost): "
    set /p DB_PORT="[?] Введите Port (по умолчанию: 5432): "
    set /p DB_NAME="[?] Введите Name (по умолчанию: ss14): "
    set /p DB_USER="[?] Введите User: "
    set /p DB_PASSWORD="[?] Введите Password: "
    if "!DB_HOST!"=="" set DB_HOST=localhost
    if "!DB_PORT!"=="" set DB_PORT=5432
    if "!DB_NAME!"=="" set DB_NAME=ss14
    (
        echo.
        echo #Settings:
        echo.
        echo guild_id=!GUILD_ID!
        echo admin_role_id=!ADMIN_ROLE_ID!
        echo developer_role_id=!DEV_ROLE_ID!
        echo.
        echo #Bot Tokens:
        echo.
        echo TOKEN=!TOKEN!
        echo.
        echo #MySQL Data Base:
        echo.
	    echo pg_host=!DB_HOST!
	    echo pg_port=!DB_PORT!
        echo pg_database=!DB_NAME!
        echo pg_username=!DB_USER!
        echo pg_password=!DB_PASSWORD!
        echo pg_echo=False
    ) > .env
)

echo [i] Проверка версии Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    python3 --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo [X] Python не установлен
        pause
        exit /b 1
    )
)

:: Проверка версии Python
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set py_ver=%%i
if not defined py_ver (
    for /f "tokens=2" %%i in ('python3 --version 2^>^&1') do set py_ver=%%i
)

echo [i] Найдена версия Python: !py_ver!

:: Извлечение номеров версии
for /f "tokens=1,2,3 delims=." %%a in ("!py_ver!") do (
    set major=%%a
    set minor=%%b
    set patch=%%c
)

:: Удаление нечисловых символов
set major=%major:~-1%
set minor=%minor:~0,2%

:: Проверка соответствия версии 3.11+
if !major! lss 3 (
    [X] Требуется Python 3.11 или выше!
    pause
    exit /b 1
)

if !major! equ 3 (
    if !minor! lss 11 (
        [i] Требуется Python 3.11 или выше!
        pause
        exit /b 1
    )
)

echo [✓] Версия Python соответствует требованиям

echo.
echo [i]Проверка установки Poetry...
poetry --version >nul 2>&1

if %errorlevel% neq 0 (
    echo [X] Poetry не установлен
    echo.
    set /p "install_poetry=[?] Хотите полуавтоматический установить Poetry? (yes/no): "

    if /i "!install_poetry!"=="yes" (
        echo Установка Poetry с помощью pip...
        %py_cmd% -m pip install --user poetry

        :: Проверяем, успешно ли установлен Poetry
        poetry --version >nul 2>&1
        if %errorlevel% neq 0 (
            echo Предупреждение: Poetry не добавлен в PATH.
            echo Добавьте путь к Poetry в переменную окружения PATH.
            echo Обычно Poetry устанавливается в: %%APPDATA%%\Python\Python!major!!minor!\Scripts
            echo Инструкции по добавлению в PATH:
            echo 1. Нажмите Win+X и выберите 'Система'
            echo 2. Выберите 'Дополнительные параметры системы'
            echo 3. Нажмите 'Переменные среды'
            echo 4. В разделе 'Системные переменные' найдите и выберите Path, нажмите 'Изменить'
            echo 5. Нажмите 'Создать' и добавьте путь: %%APPDATA%%\Python\Python!major!!minor!\Scripts
            echo 6. Нажмите 'OK' и перезапустите терминал.
        ) else (
            for /f "tokens=3" %%i in ('poetry --version') do set poetry_ver=%%i
            echo [✓] Poetry успешно установлен (версия !poetry_ver!)
        )
    ) else if /i "!install_poetry!"=="no" (
        echo [i] Установка Poetry отменена.
        echo [i] Установите Poetry вручную, следуя инструкциям на https://python-poetry.org/docs/#installation
        pause
        exit /b 1
    ) else (
        echo [X] Пожалуйста, введите 'yes' или 'no'.
        goto install_choice
    )

for /f "tokens=1,2,3 delims= " %%i in ('poetry --version') do (
    set poetry_ver=%%k
)

echo [✓] Poetry установлен (версия !poetry_ver!)
poetry sync
start main.py

:: Вывод информации
echo.
echo ==================================================
echo [√] Система запущена
echo ==================================================
pause