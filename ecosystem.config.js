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
        // ==================== SISTEMA UNIFICADO (Backend + Frontend) ====================
        {
            name: "postventa-unificado",
            script: "python-portable/python/python.exe",
            args: "-m daphne -e ssl:8000:privateKey=../frontend/ssl/key.pem:certKey=../frontend/ssl/cert.pem postventa_system.asgi:application",
            cwd: "./backend",
            interpreter: "none",

            // Auto-restart configuration
            autorestart: true,
            watch: false,
            max_restarts: 10,
            restart_delay: 3000,

            // Environment variables
            env: {
                DJANGO_SETTINGS_MODULE: "apps.core.settings",
                PYTHONUNBUFFERED: "1",
                PATH: "C:\\Users\\jdiaz\\Desktop\\postventa-system;C:\\Users\\jdiaz\\Desktop\\postventa-system\\python312\\Scripts;" + process.env.PATH,
            },

            // Logging
            error_file: "../logs/backend-error.log",
            out_file: "../logs/backend-out.log",
            log_date_format: "YYYY-MM-DD HH:mm:ss Z",
            merge_logs: true,

            // Health monitoring
            max_memory_restart: "600M",
        },
        // ==================== TÚNEL DE CLOUDFLARE (Para accesos desde Internet) ====================
        {
            name: "postventa-tunnel",
            script: "cloudflared.exe",
            args: "tunnel run postventa-tunnel",
            cwd: "./",
            interpreter: "none",
            autorestart: true,
            max_restarts: 10,
            restart_delay: 5000,
            error_file: "./logs/tunnel-error.log",
            out_file: "./logs/tunnel-out.log",
            log_date_format: "YYYY-MM-DD HH:mm:ss Z"
        }
    ],
};
