@echo off
setlocal ENABLEDELAYEDEXPANSION
cd /d "%~dp0"

echo.
echo === Preparing piper_runtime ===
mkdir piper_runtime 2>nul

REM --- 1) Piper model (LibriTTS-R medium, US English) ---
echo.
echo === Downloading Piper LibriTTS-R medium model ===
powershell -NoProfile -Command ^
  "Invoke-WebRequest https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/libritts_r/medium/en_US-libritts_r-medium.onnx -OutFile piper_runtime\en_US-libritts_r-medium.onnx"
powershell -NoProfile -Command ^
  "Invoke-WebRequest https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/libritts_r/medium/en_US-libritts_r-medium.onnx.json -OutFile piper_runtime\en_US-libritts_r-medium.onnx.json"

REM --- 2) Piper binary (skip if you already have piper.exe here) ---
if not exist "piper_runtime\piper.exe" (
  echo.
  echo === Downloading Piper Windows binary ===
  powershell -NoProfile -Command ^
    "Invoke-WebRequest https://github.com/rhasspy/piper/releases/latest/download/piper_windows_x64.zip -OutFile piper_runtime\piper.zip"
  powershell -NoProfile -Command ^
    "Expand-Archive -Force piper_runtime\piper.zip piper_runtime"
  del /q piper_runtime\piper.zip 2>nul
)

REM --- 3) Portable FFmpeg (gyan.dev essentials build) ---
echo.
echo === Downloading portable FFmpeg (essentials) ===
mkdir piper_runtime\ffmpeg 2>nul
powershell -NoProfile -Command ^
  "$u='https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip';" ^
  "Invoke-WebRequest $u -OutFile piper_runtime\ffmpeg\ffmpeg.zip"
powershell -NoProfile -Command ^
  "Expand-Archive -Force piper_runtime\ffmpeg\ffmpeg.zip piper_runtime\ffmpeg"
del /q piper_runtime\ffmpeg\ffmpeg.zip 2>nul

REM move ffmpeg.exe into piper_runtime\ffmpeg\bin (path may contain version folder)
for /d %%D in (piper_runtime\ffmpeg\ffmpeg-*) do (
  if exist "%%D\bin\ffmpeg.exe" (
    rem already in bin
    set "FFMPEGBIN=%%D\bin"
  ) else if exist "%%D\ffmpeg.exe" (
    mkdir "%%D\bin" 2>nul
    move /y "%%D\ffmpeg.exe" "%%D\bin\ffmpeg.exe" >nul
    set "FFMPEGBIN=%%D\bin"
  )
)
if not defined FFMPEGBIN (
  echo [WARN] Could not find ffmpeg.exe after extraction. Please check piper_runtime\ffmpeg\.
) else (
  echo Found ffmpeg in: !FFMPEGBIN!
)

echo.
echo === Done. Test render: ===
echo manim -pql .\FinalAnimation.py FinalAnimation
echo.
pause
