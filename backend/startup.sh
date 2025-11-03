#!/bin/bash
# Backend startup script
# Automatically loads data into database if it's empty

set -e

echo "==================================================="
echo "Backend startup script"
echo "==================================================="

echo "Waiting for database to be ready..."
MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if pg_isready -h db -p 5432 -U postgres > /dev/null 2>&1; then
        echo "✓ Database is ready!"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "Waiting for database... ($RETRY_COUNT/$MAX_RETRIES)"
    sleep 1
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "✗ Database failed to become ready in time"
    exit 1
fi

echo ""
echo "Checking if database needs to be populated..."

EVENT_COUNT=$(psql $DATABASE_URL -t -c "SELECT COUNT(*) FROM events;" 2>/dev/null || echo "0")
EVENT_COUNT=$(echo $EVENT_COUNT | xargs)

echo "Current events in database: $EVENT_COUNT"

JSON_FILE="/data/scraped_events.json"

if [ ! -f "$JSON_FILE" ]; then
    echo "⚠ Warning: No scraped data found at $JSON_FILE"
    echo "⚠ Run the scraper first: python utils/scraper.py"
    echo ""
    echo "Starting Flask application anyway..."
else
    if [ "$EVENT_COUNT" = "0" ]; then
        echo ""
        echo "Database is empty. Loading data automatically..."
        python /database/load_data.py
        echo ""
        echo "✓ Data loaded successfully!"
    else
        echo "✓ Database already has data. Skipping automatic load."
        echo "  (Run 'make db-reset' then 'make db-load' to reload data)"
    fi
fi

echo ""
echo "==================================================="
echo "Starting Flask application..."
echo "==================================================="
echo ""

exec python main.py
