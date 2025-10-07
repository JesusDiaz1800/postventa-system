-- Tablas para Celery en SQL Server
CREATE TABLE celery_taskmeta (
    id INT IDENTITY(1,1) PRIMARY KEY,
    task_id VARCHAR(255) NOT NULL UNIQUE,
    status VARCHAR(50),
    result NTEXT,
    date_done DATETIME,
    traceback NTEXT,
    name VARCHAR(255),
    args NTEXT,
    kwargs NTEXT,
    worker VARCHAR(255),
    retries INT,
    queue VARCHAR(255)
);

CREATE TABLE celery_tasksetmeta (
    id INT IDENTITY(1,1) PRIMARY KEY,
    taskset_id VARCHAR(255) NOT NULL UNIQUE,
    result NTEXT,
    date_done DATETIME,
    group_id VARCHAR(255)
);

-- Tabla para resultados periódicos
CREATE TABLE periodic_tasks (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    task VARCHAR(255),
    schedule NTEXT,
    args NTEXT,
    kwargs NTEXT,
    enabled BIT NOT NULL DEFAULT 1,
    last_run_at DATETIME,
    total_run_count INT DEFAULT 0,
    date_changed DATETIME
);

-- Índices para mejorar el rendimiento
CREATE INDEX idx_celery_taskmeta_date_done ON celery_taskmeta(date_done);
CREATE INDEX idx_celery_tasksetmeta_date_done ON celery_tasksetmeta(date_done);
CREATE INDEX idx_periodic_tasks_enabled ON periodic_tasks(enabled);
CREATE INDEX idx_periodic_tasks_last_run ON periodic_tasks(last_run_at);