/**
 * PM2 Ecosystem Configuration for SERTEC SYSTEM
 * 
 * Gestiona el ciclo de vida de la aplicación, asegurando que el servidor
 * y el túnel de internet estén siempre activos y se reinicien ante fallos.
 */

module.exports = {
    apps: [
        {
            name: "sertec-server",
            script: "python-portable/python/python.exe",
            // Daphne es ideal para WebSockets y concurrencia
            args: "-m daphne -p 8001 -b 0.0.0.0 postventa_system.asgi:application",
            cwd: "./backend",
            interpreter: "none",
            autorestart: true,
            watch: false,
            max_restarts: 50,
            restart_delay: 2000,
            env: {
                DJANGO_SETTINGS_MODULE: "apps.core.settings",
                PYTHONUNBUFFERED: "1",
            },
            error_file: "../logs/sertec-server-error.log",
            out_file: "../logs/sertec-server-out.log",
            log_date_format: "YYYY-MM-DD HH:mm:ss",
            max_memory_restart: "1G",
        },
        {
            name: "sertec-tunnel",
            script: "cloudflared.exe",
            // Usa el archivo de configuración generado por configurar_dominio_sertec.py
            args: "tunnel run sertec-tunnel",
            cwd: "./",
            interpreter: "none",
            autorestart: true,
            max_restarts: 100,
            restart_delay: 5000,
            error_file: "./logs/sertec-tunnel-error.log",
            out_file: "./logs/sertec-tunnel-out.log",
            log_date_format: "YYYY-MM-DD HH:mm:ss"
        }
    ],
};
