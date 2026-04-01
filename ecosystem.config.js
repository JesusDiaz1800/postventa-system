/**
 * PM2 Ecosystem Configuration for Postventa System
 * 
 * This file replaces INICIAR_SISTEMA.bat with a professional process manager.
 * 
 * Commands:
 *   pm2 start ecosystem.config.js        - Start all processes
 *   pm2 stop all                         - Stop all processes
 *   pm2 restart all                      - Restart all processes
 *   pm2 logs                             - View unified logs
 *   pm2 monit                            - Real-time monitoring dashboard
 *   pm2 save                             - Save process list for auto-start
 *   pm2-startup install                  - Configure auto-start on Windows boot
 */

module.exports = {
    apps: [
        // ==================== BACKEND (Django + Daphne ASGI) ====================
        {
            name: "backend",
            script: "python-portable/python/python.exe",
            args: "-m daphne -b 0.0.0.0 -p 8000 postventa_system.asgi:application",
            cwd: "./backend",
            interpreter: "none",

            // Auto-restart configuration
            autorestart: true,
            watch: false, // Disable file watching in production
            max_restarts: 10,
            restart_delay: 3000, // 3 seconds between restarts

            // Environment variables
            env: {
                DJANGO_SETTINGS_MODULE: "apps.core.settings",
                PYTHONUNBUFFERED: "1",
                PATH: "C:\\Users\\jdiaz\\Desktop\\postventa-system;C:\\Users\\jdiaz\\Desktop\\postventa-system\\python312\\Scripts;" + process.env.PATH,
            },

            // Logging
            error_file: "./logs/backend-error.log",
            out_file: "./logs/backend-out.log",
            log_date_format: "YYYY-MM-DD HH:mm:ss Z",
            merge_logs: true,

            // Health monitoring
            max_memory_restart: "500M",
        },

        // ==================== FRONTEND (React + Vite) ====================
        {
            name: "frontend",
            script: "npm",
            args: "run dev -- --host 0.0.0.0",
            cwd: "./frontend",
            interpreter: "none",

            // Auto-restart configuration
            autorestart: true,
            watch: false,
            max_restarts: 10,
            restart_delay: 2000,

            // Logging
            error_file: "./logs/frontend-error.log",
            out_file: "./logs/frontend-out.log",
            log_date_format: "YYYY-MM-DD HH:mm:ss Z",
            merge_logs: true,

            // Health monitoring
            max_memory_restart: "300M",
        },
    ],
};
