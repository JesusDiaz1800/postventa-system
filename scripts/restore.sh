#!/bin/bash

# Restore script for Postventa System
set -e

if [ $# -eq 0 ]; then
    echo "❌ Usage: $0 <backup_file.tar.gz>"
    echo "📋 Available backups:"
    ls -la backups/*.tar.gz 2>/dev/null || echo "   No backups found"
    exit 1
fi

BACKUP_FILE="$1"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ Backup file not found: $BACKUP_FILE"
    exit 1
fi

echo "🔄 Starting restore of Postventa System..."
echo "📦 Backup file: $BACKUP_FILE"

# Confirm restore
read -p "⚠️  This will overwrite current data. Continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Restore cancelled"
    exit 1
fi

# Stop services
echo "⏹️  Stopping services..."
docker-compose down

# Extract backup
echo "📦 Extracting backup..."
TEMP_DIR=$(mktemp -d)
tar -xzf "$BACKUP_FILE" -C "$TEMP_DIR"
BACKUP_CONTENT=$(ls "$TEMP_DIR")

# Restore database
echo "🗄️  Restoring database..."
if [ -f "$TEMP_DIR/$BACKUP_CONTENT/database.sql" ]; then
    docker-compose up -d db
    sleep 10
    docker-compose exec -T db psql -U postventa_user -d postventa_system -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
    docker-compose exec -T db psql -U postventa_user -d postventa_system < "$TEMP_DIR/$BACKUP_CONTENT/database.sql"
    echo "✅ Database restored successfully"
else
    echo "⚠️  Database backup not found, skipping..."
fi

# Restore media files
echo "📁 Restoring media files..."
if [ -d "$TEMP_DIR/$BACKUP_CONTENT/media" ]; then
    rm -rf media
    cp -r "$TEMP_DIR/$BACKUP_CONTENT/media" .
    echo "✅ Media files restored successfully"
else
    echo "⚠️  Media files backup not found, skipping..."
fi

# Restore static files
echo "📁 Restoring static files..."
if [ -d "$TEMP_DIR/$BACKUP_CONTENT/staticfiles" ]; then
    rm -rf staticfiles
    cp -r "$TEMP_DIR/$BACKUP_CONTENT/staticfiles" .
    echo "✅ Static files restored successfully"
else
    echo "⚠️  Static files backup not found, skipping..."
fi

# Restore configuration files
echo "⚙️  Restoring configuration files..."
if [ -f "$TEMP_DIR/$BACKUP_CONTENT/.env" ]; then
    cp "$TEMP_DIR/$BACKUP_CONTENT/.env" backend/
    echo "✅ Environment file restored"
fi

if [ -d "$TEMP_DIR/$BACKUP_CONTENT/templates" ]; then
    rm -rf templates
    cp -r "$TEMP_DIR/$BACKUP_CONTENT/templates" .
    echo "✅ Templates restored"
fi

# Clean up
rm -rf "$TEMP_DIR"

# Start services
echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Run migrations
echo "🔄 Running migrations..."
docker-compose exec backend python manage.py migrate

# Collect static files
echo "📁 Collecting static files..."
docker-compose exec backend python manage.py collectstatic --noinput

# Final status check
echo "🔍 Final status check..."
docker-compose ps

echo ""
echo "✅ Restore completed successfully!"
echo ""
echo "📋 Access Information:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000/api"
echo "   Admin Panel: http://localhost:8000/admin"
echo ""
echo "⚠️  Important:"
echo "   1. Verify that all data has been restored correctly"
echo "   2. Test the application functionality"
echo "   3. Update any configuration if needed"
