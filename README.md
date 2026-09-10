


# Create "events" topic:
curl -X PUT "http://localhost:8085/v1/projects/my-local-project/topics/events"

# Create subscription named "events-sub" in the "events" topic 
curl -X PUT "http://localhost:8085/v1/projects/my-local-project/subscriptions/events-sub" \
     -H "Content-Type: application/json" \
     -d '{"topic": "projects/my-local-project/topics/events"}'

# List (Pull) the events arriving in the topic

curl -X POST "http://localhost:8085/v1/projects/my-local-project/subscriptions/events-sub:pull" \
     -H "Content-Type: application/json" \
     -d '{"maxMessages": 10, "returnImmediately": true}'



The emulator will respond with a JSON array of receivedMessages. Because Pub/Sub data payload strings are always Base64 encoded, they will look like scrambled text.


echo "SGVsbG8=" | base64 --decode
# Output: Hello


# Test emulator localy

echo -n '{"event":"movie_favourites","user_id":"123","movie_id":"456"}' | base64

Suppose this gives:

eyJldmVudCI6Im1vdmllX2Zhdm91cml0ZXMiLCJ1c2VyX2lkIjoiMTIzIiwibW92aWVfaWQiOiI0NTYifQ==

curl -X POST \
  "http://localhost:8085/v1/projects/my-local-project/topics/events:publish" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "data": "eyJldmVudCI6Im1vdmllX2Zhdm91cml0ZXMiLCJ1c2VyX2lkIjoiMTIzIiwibW92aWVfaWQiOiI0NTYifQ=="
      }
    ]
  }'


# Connect to local DB
psql -U myuser -W MovieMatch1234 -d MovieMatch

# Show tables
SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname = 'public';