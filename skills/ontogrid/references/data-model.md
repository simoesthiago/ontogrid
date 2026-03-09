# Data model summary

Public core entities:

- `source`
- `dataset`
- `dataset_version`
- `refresh_job`
- `entity`
- `entity_alias`
- `relation`
- `metric_series`
- `observation`
- `insight_snapshot`

Enterprise extension later:

- `tenant`
- `user`
- `private_connection`
- `asset`
- `measurement`
- `alert`
- `case`

Storage split:

- PostgreSQL/TimescaleDB for metadata, versions and time-series
- Neo4j for the public Energy Graph
