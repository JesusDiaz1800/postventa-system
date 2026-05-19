# Postventa System - Backend Production Guide

## Overview
This guide explains how to run the Django backend in production with SQL Server, using Python 3.12 and a dedicated virtual environment.

## Requirements
- Windows Server 2019/2022 or Linux (Ubuntu 22.04)
- Python 3.12 (64-bit)
- SQL Server (Express or Standard/Enterprise)
- ODBC Driver 18 for SQL Server
- Environment file `backend/.env` based on `env.example`

## Setup (Windows)
1) Install Python 3.12 (x64) and ODBC Driver 18 for SQL Server.
2) Configure `backend/.env` with SQL Server credentials.
3) From the project root, run:
```powershell
scripts\setup_backend_env.ps1
```
This creates a `venv312`, installs dependencies, runs migrations and starts the server.

## Environment Variables
- `DATABASE_URL`: mssql+pyodbc connection string with ODBC 18.
- `DJANGO_SETTINGS_MODULE`: `postventa_system.settings-sqlserver` for SQL Server profile.

## Hardening
- Set `DEBUG=False` in production settings.
- Configure `ALLOWED_HOSTS` and CORS origins for your domain.
- Use HTTPS with a reverse proxy (e.g., Nginx) and HSTS.
- Restrict admin access and rotate secrets regularly.

## Non-Production Scripts
Files importing or using `sqlite3` are for local testing only and must not be executed in production.

## Monitoring and Logs
- Use Windows Event Viewer or file logs under `backend/logs/` if configured.
- Add a process manager (NSSM, pm2-windows-service, or systemd on Linux) to keep Django alive.

## Static/Media
- Serve static files via Whitenoise or Nginx.
- Ensure media (documents) paths have proper read/write permissions.

## Upgrades
- Activate the venv: `venv312\Scripts\Activate.ps1`
- Update packages: `pip install -r backend/requirements.txt --upgrade`
