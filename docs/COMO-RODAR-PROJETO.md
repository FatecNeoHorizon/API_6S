## :whale: Como Rodar com Docker <a id="como-rodar-com-docker"></a>

### Pré-requisitos

- Docker instalado
- Docker Compose (`docker compose`) habilitado

### 1. Criar arquivo de ambiente

Na raiz do projeto, crie um arquivo `.env` com as variáveis usadas no `docker-compose.yml`.

Exemplo mínimo:

```env
POSTGRES_DB=zeus
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
MONGO_INITDB_ROOT_USERNAME=admin
MONGO_INITDB_ROOT_PASSWORD=admin
```

### 2. Subir os serviços

Na raiz do projeto (`API_6S`):

```bash
docker compose up --build -d
```

Serviços iniciados:

- `frontend` em `http://localhost:5173`
- `backend` em `http://localhost:8000`
- `postgres` em `localhost:5432`
- `mongo` em `localhost:27017`

### 3. Ver logs (opcional)

```bash
docker compose logs -f
```

Ou de um serviço especifico:

```bash
docker compose logs -f backend
```

### 4. Parar o ambiente

```bash
docker compose down
```

Para remover tambem os volumes de banco:

```bash
docker compose down -v
```

### 5. Reiniciar apenas um serviço (opcional)

```bash
docker compose up -d --build backend
```

```bash
docker compose restart frontend
```