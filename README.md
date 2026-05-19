# Nebula Genshin Demo

## Backend services

The application stack is split into these runtime roles:

- `web`: FastAPI producer API. It connects to an external RabbitMQ and publishes messages.
- `worker`: Queue consumer. It connects to external RabbitMQ and external Nebula Graph.
- `init-db`: One-shot initializer for business graph schemas.
- `cron`: Scheduler for crawler jobs.

Start the stack:

```bash
sudo docker compose down -v && sudo docker compose up -d --build
```