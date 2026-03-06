# Data model summary

Core entities:

- `tenant`
- `user`
- `asset`
- `measurement_point`
- `measurement`
- `health_score`
- `alert`
- `case`
- `ingestion_job`

Storage split:

- PostgreSQL/TimescaleDB for operational and time-series data
- Neo4j for topology and impact
