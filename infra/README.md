# MBOAHUB Database

## Start the database

Make sure Docker Desktop is installed and running, then run:

```bash
docker compose up -d postgres
```

## Connection details

- Host: localhost
- Port: 5432
- Database: mboahub
- Username: mboahub
- Password: mboahub123

Connection string:

```text
postgresql://mboahub:mboahub123@localhost:5432/mboahub
```

## Connect with psql

```bash
docker compose exec postgres psql -U mboahub -d mboahub
```

## Stop the database

```bash
docker compose down
```

## Reset everything

```bash
docker compose down -v
```
