@echo off
REM Convert a single document file to markdown (Windows)
REM Usage: convert.bat <input-file> [output-file]

setlocal enabledelayedexpansion

if "%~1"=="" (
    echo Error: No input file specified
    echo.
    echo Usage: %~nx0 ^<input-file^> [output-file]
    echo.
    echo Examples:
    echo   %~nx0 document.pdf
    echo   %~nx0 document.pdf output\document.md
    echo   %~nx0 "C:\Documents\report.docx"
    echo.
    echo Supported formats: PDF, DOCX, PPTX, HTML
    exit /b 1
)

set INPUT_FILE=%~1
set OUTPUT_FILE=%~2

if not exist "%INPUT_FILE%" (
    echo Error: File not found: %INPUT_FILE%
    exit /b 1
)

REM Get absolute paths
set INPUT_FILE=%~f1
set INPUT_DIR=%~dp1
set INPUT_BASENAME=%~nx1

REM Check if Ollama is running
docker ps | findstr myfiles_ollama >nul
if errorlevel 1 (
    echo Starting Ollama service...
    docker-compose up -d ollama
    echo Waiting for Ollama to be ready...
    timeout /t 5 >nul
)

REM Build container if needed
docker images | findstr myfiles_to_markdown-converter >nul
if errorlevel 1 (
    echo Building converter container...
    docker-compose build converter
)

echo.
echo Converting: %INPUT_FILE%
echo.

if "%OUTPUT_FILE%"=="" (
    REM Default output
    docker run --rm ^
        --network myfiles_to_markdown_myfiles_network ^
        -v "%INPUT_DIR%:/app/input:ro" ^
        -v "%~dp0output:/app/output" ^
        -v "%~dp0config:/app/config:ro" ^
        -v "%~dp0logs:/app/logs" ^
        -e OLLAMA_HOST=http://ollama:11434 ^
        myfiles_to_markdown-converter ^
        python src/main.py "/app/input/%INPUT_BASENAME%"
    
    set OUTPUT_NAME=%~n1.md
    set OUTPUT_FILE=%~dp0output\!OUTPUT_NAME!
) else (
    REM Custom output
    set OUTPUT_FILE=%~f2
    set OUTPUT_DIR=%~dp2
    
    docker run --rm ^
        --network myfiles_to_markdown_myfiles_network ^
        -v "%INPUT_DIR%:/app/input:ro" ^
        -v "!OUTPUT_DIR!:/app/output" ^
        -v "%~dp0config:/app/config:ro" ^
        -v "%~dp0logs:/app/logs" ^
        -e OLLAMA_HOST=http://ollama:11434 ^
        myfiles_to_markdown-converter ^
        python src/main.py "/app/input/%INPUT_BASENAME%" -o "/app/output/%~nx2"
)

if errorlevel 1 (
    echo.
    echo Conversion failed!
    exit /b 1
)

echo.
echo Success!
echo Output: !OUTPUT_FILE!
echo.

