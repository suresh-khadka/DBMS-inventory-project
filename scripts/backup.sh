#!/bin/bash
echo "Creating database backup..."
timestamp=$(date +%Y%m%d_%H%M%S)
mysqldump -u root -p inventory_db > ../database/backup_$timestamp.sql
echo "Backup created: backup_$timestamp.sql"
