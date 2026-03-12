@echo off
echo Creating database backup...
set timestamp=%date:~-4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%
set timestamp=%timestamp: =0%
mysqldump -u root -p inventory_db > ..\database\backup_%timestamp%.sql
echo Backup created: backup_%timestamp%.sql
pause
