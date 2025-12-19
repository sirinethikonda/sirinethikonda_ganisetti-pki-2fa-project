
set -e
echo "Starting cron service..."
/usr/sbin/cron -f & 

echo "Starting FastAPI server..."
# exec uvicorn runs uvicorn as the main process, which is good practice.
# app.main:app assumes main.py contains the FastAPI instance named 'app'.
exec uvicorn app.main:app --host 0.0.0.0 --port 8080