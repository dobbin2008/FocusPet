@echo off
setlocal
cd /d "%~dp0"

if not exist ".env" (
    copy ".env.example" ".env" >nul
    echo Arquivo .env criado a partir do modelo.
    echo Configure as chaves do Cloudflare Turnstile no .env para habilitar o cadastro.
    echo.
)

if not exist ".venv\Scripts\python.exe" (
    echo Preparando o ambiente Python do projeto...
    py -3 -m venv ".venv"
    if errorlevel 1 (
        echo Nao foi possivel criar o ambiente. Instale o Python 3 e tente novamente.
        pause
        exit /b 1
    )

    echo Instalando as dependencias. Isso acontece apenas na primeira inicializacao...
    ".venv\Scripts\python.exe" -m pip install -r "requirements.txt"
    if errorlevel 1 (
        echo Nao foi possivel instalar as dependencias. Verifique sua conexao e tente novamente.
        pause
        exit /b 1
    )
)

echo Iniciando Study Buddy...
start "" powershell.exe -NoProfile -WindowStyle Hidden -Command "for ($i = 0; $i -lt 60; $i++) { $c = New-Object Net.Sockets.TcpClient; try { $c.Connect('127.0.0.1', 5000); if ($c.Connected) { Start-Process 'http://127.0.0.1:5000'; exit } } catch { } finally { $c.Dispose() }; Start-Sleep -Seconds 1 }"
".venv\Scripts\python.exe" "app.py"

echo.
echo O servidor Study Buddy foi encerrado.
pause
