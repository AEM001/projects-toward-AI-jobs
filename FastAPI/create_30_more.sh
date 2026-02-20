#!/bin/bash

# Create 30 more todos (continuing from #21 to #50)
API_URL="http://localhost:8000"
EMAIL="testuser@example.com"
PASSWORD="testpass123"

# Login to get token
TOKEN_RESPONSE=$(curl -s -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"$EMAIL\", \"password\": \"$PASSWORD\"}")

TOKEN=$(echo $TOKEN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo "Failed to get token"
    exit 1
fi

echo "Creating todos #21-50..."

TITLES=(
    "Plan sprint" "Research new tech" "Attend conference" "Prepare presentation"
    "Review budget" "Update resume" "Network with peers" "Mentor junior"
    "Practice interview" "Learn Docker" "Setup monitoring" "Configure logging"
    "Improve security" "Add rate limiting" "Implement caching" "Design API schema"
    "Create migrations" "Backup database" "Analyze metrics" "Fix broken links"
    "Update privacy policy" "Write blog post" "Create video tutorial" "Answer emails"
    "Organize files" "Declutter workspace" "Plan vacation" "Book flight tickets"
    "Research hotels" "Make dinner reservation"
)

for i in {21..50}; do
    TITLE_INDEX=$(( (i - 21) % ${#TITLES[@]} ))
    TITLE="${TITLES[$TITLE_INDEX]} #$i"
    
    DAYS=$(( RANDOM % 14 ))
    HOUR=$(( 9 + RANDOM % 12 ))
    DDL=$(date -v+${DAYS}d "+%Y-%m-%d $HOUR:00")
    
    RESPONSE=$(curl -s -X POST "$API_URL/todos" \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $TOKEN" \
      -d "{\"title\": \"$TITLE\", \"ddl\": \"$DDL\"}")
    
    TODO_ID=$(echo $RESPONSE | grep -o '"id":[0-9]*' | cut -d':' -f2)
    echo "Created todo #$i: ID=$TODO_ID"
    
    # Sleep to avoid rate limiting - 3 seconds every 20 requests
    if [ $(( (i - 20) % 20 )) -eq 0 ] && [ $i -ne 21 ]; then
        echo "Rate limit pause (60s)..."
        sleep 60
    fi
    sleep 0.5
done

echo "Done!"
