curl -X PUT http://127.0.0.1:9200/persons -H 'Content-Type: application/json' -d '
{
  "mappings": {
    "dynamic": "strict",
    "properties": {
      "id": {
        "type": "keyword"
      },
      "full_name": {
        "type": "text"
      },
      "films": {
        "type": "nested",
        "dynamic": "strict",
        "properties": {
          "id": {
            "type": "keyword"
          },
          "roles": {
            "type": "text"
          }
        }
      }
    }
  }
}'