# ContaBot local stack

## Primeiro uso

Crie o arquivo local `infra\.env`. Esse arquivo nao deve ser commitado.

```powershell
New-Item infra\.env
```

Variaveis obrigatorias:

```env
API_PORT=8000
POSTGRES_DB=contabot
POSTGRES_USER=contabot
POSTGRES_PASSWORD=
POSTGRES_PORT=5432
EVOLUTION_POSTGRES_DB=evolution
REDIS_PORT=6379
MINIO_ROOT_USER=contabot
MINIO_ROOT_PASSWORD=
MINIO_BUCKET=contabot
MINIO_API_PORT=9000
MINIO_CONSOLE_PORT=9001
EVOLUTION_API_PORT=8080
EVOLUTION_SERVER_URL=http://localhost:8080
EVOLUTION_API_KEY=
```

Depois suba a stack:

```powershell
docker compose --env-file infra\.env -f infra\docker-compose.yml up -d --build
```

## Servicos

- API: http://localhost:8000
- Evolution API: http://localhost:8080
- MinIO Console: http://localhost:9001
- Postgres: localhost:5432
- Redis: localhost:6379

## Comandos uteis

```powershell
docker compose --env-file infra\.env -f infra\docker-compose.yml ps
docker compose --env-file infra\.env -f infra\docker-compose.yml logs -f api
docker compose --env-file infra\.env -f infra\docker-compose.yml down
```

Para apagar os dados locais tambem:

```powershell
docker compose --env-file infra\.env -f infra\docker-compose.yml down -v
```
