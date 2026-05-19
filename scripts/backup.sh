#!/bin/bash

# Backup script for Postventa System
set -e

BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "📦 Starting backup of Postventa System..."
echo "📁 Backup directory: $BACKUP_DIR"

# Backup database
echo "🗄️  Backing up database..."
docker-compose exec -T db pg_dump -U postventa_user postventa_system > "$BACKUP_DIR/database.sql"

# Backup media files
echo "📁 Backing up media files..."
if [ -d "media" ]; then
    cp -r media "$BACKUP_DIR/"
fi

# Backup static files
echo "📁 Backing up static files..."
if [ -d "staticfiles" ]; then
    cp -r staticfiles "$BACKUP_DIR/"
fi

# Backup configuration files
echo "⚙️  Backing up configuration files..."
cp docker-compose.yml "$BACKUP_DIR/" 2>/dev/null || true
cp backend/.env "$BACKUP_DIR/" 2>/dev/null || true
cp -r templates "$BACKUP_DIR/" 2>/dev/null || true

# Create backup info file
echo "📋 Creating backup info..."
cat > "$BACKUP_DIR/backup_info.txt" << EOF
Postventa System Backup
=======================
Date: $(date)
Version: 1.0.0
Database: PostgreSQL
Media Files: $(du -sh media 2>/dev/null | cut -f1 || echo "N/A")
Static Files: $(du -sh staticfiles 2>/dev/null | cut -f1 || echo "N/A")

Services Status:
$(docker-compose ps 2>/dev/null || echo "Docker Compose not available")

Backup Contents:
- database.sql (PostgreSQL dump)
- media/ (uploaded files)
- staticfiles/ (collected static files)
- docker-compose.yml (service configuration)
- .env (environment variables)
- templates/ (document templates)
EOF

# Compress backup
echo "🗜️  Compressing backup..."
cd backups
tar -czf "$(basename "$BACKUP_DIR").tar.gz" "$(basename "$BACKUP_DIR")"
cd ..

# Remove uncompressed directory
rm -rf "$BACKUP_DIR"

echo "✅ Backup completed successfully!"
echo "📦 Backup file: backups/$(basename "$BACKUP_DIR").tar.gz"
echo "📏 Backup size: $(du -sh "backups/$(basename "$BACKUP_DIR").tar.gz" | cut -f1)"
