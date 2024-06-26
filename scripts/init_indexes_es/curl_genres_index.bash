curl -X PUT http://127.0.0.1:9200/genres -H 'Content-Type: application/json' -d '
{
  "mappings": {
    "dynamic": "strict",
    "properties": {
      "id": {
        "type": "keyword"
      },
      "name": {
        "type": "text"
      }
    }
  }
}
'
