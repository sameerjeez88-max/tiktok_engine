@echo off
title TikTok System Dual Launcher

echo Starting Web Interface (Flask)...
start "TikTok App (Flask)" cmd /k "cd /d F:\laragon\www\tiktok_engine && python app.py"

echo Starting Auto-Pilot Scheduler (Engine)...
start "TikTok Engine (Scheduler)" cmd /k "cd /d F:\laragon\www\tiktok_engine && python engine.py"

exit