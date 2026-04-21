
# KIRO_MASTER_PROMPT.md

You are generating the initial implementation of the AgroFlightOps system.

Read the following documents first:

- SpecProjetoKiro.md
- DATABASE_RULES.md

Follow all database rules strictly.

## Goals

Generate the MVP of AgroFlightOps including:

- database models
- migrations
- API endpoints
- services layer
- repositories
- basic authentication
- document upload/download integration with S3

## Backend

Language: Python
Framework: FastAPI

Architecture:

app/
 ├── api
 ├── services
 ├── repositories
 ├── models
 └── schemas

## Database

Engine: MySQL 8.0

Use:

BIGINT UNSIGNED AUTO_INCREMENT as primary key.

Foreign keys must use BIGINT UNSIGNED.

Use Flyway migrations.

## API Examples

GET /usuarios
POST /usuarios

GET /drones
POST /drones

GET /missoes
POST /missoes

## Security

Authentication: JWT
Password hashing: bcrypt

## Output

Generate:

- database models
- migration scripts
- API routers
- service layer
- repository layer
