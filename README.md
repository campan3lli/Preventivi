# Preventivi / Limone Blu Studio

Questa applicazione è composta da tre parti:

1. Frontend React, compilato in static files.
2. Backend FastAPI in Python.
3. MongoDB esterno, consigliato su Atlas.

## Deploy consigliato su CloudPanel

La soluzione più semplice è questa:

1. CloudPanel gestisce dominio, SSL e Nginx.
2. Il frontend React viene buildato e servito come sito statico.
3. Il backend FastAPI gira come servizio locale su `127.0.0.1`.
4. Nginx inoltra `/api` al backend.
5. MongoDB resta fuori dalla VPS.

## Variabili ambiente

### Backend

Crea `backend/.env` con questi valori:

```env
MONGO_URL=mongodb+srv://USER:PASSWORD@CLUSTER.mongodb.net/?retryWrites=true&w=majority
DB_NAME=preventivi
RESEND_API_KEY=your_resend_key
SENDER_EMAIL=info@limoneblu.it
CORS_ORIGINS=https://cp.limoneblu.it,https://limoneblu.it
```

Note:

- `CORS_ORIGINS` deve contenere il dominio reale del sito.
- Non usare `*` in produzione se `allow_credentials=True`.

### Frontend

Prima della build imposta:

```env
REACT_APP_BACKEND_URL=https://cp.limoneblu.it
```

## Backend FastAPI

### 1. Dipendenze

Sul server:

```bash
cd /path/to/preventivi/backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install "uvicorn[standard]" gunicorn
```

### 2. Avvio con systemd

Usa un servizio come questo:

```ini
[Unit]
Description=Preventivi FastAPI
After=network.target

[Service]
WorkingDirectory=/path/to/preventivi/backend
Environment="PATH=/path/to/preventivi/backend/venv/bin"
ExecStart=/path/to/preventivi/backend/venv/bin/gunicorn -k uvicorn.workers.UvicornWorker -w 2 -b 127.0.0.1:8001 server:app
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Comandi utili:

```bash
sudo systemctl daemon-reload
sudo systemctl enable preventivi-api
sudo systemctl start preventivi-api
sudo systemctl status preventivi-api --no-pager -l
```

## Frontend React

### Build

```bash
cd /path/to/preventivi/frontend
export REACT_APP_BACKEND_URL="https://cp.limoneblu.it"
npm install
npm run build
```

La cartella da servire come document root è `frontend/build`.

### Routing SPA

Nel vhost CloudPanel usa il fallback su `index.html`:

```nginx
location / {
	try_files $uri /index.html;
}
```

## Nginx reverse proxy per l'API

Nel sito CloudPanel aggiungi:

```nginx
location /api/ {
	proxy_pass http://127.0.0.1:8001/api/;
	proxy_http_version 1.1;
	proxy_set_header Host $host;
	proxy_set_header X-Real-IP $remote_addr;
	proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
	proxy_set_header X-Forwarded-Proto $scheme;
}
```

## MongoDB Atlas

1. Crea un cluster Atlas.
2. Crea un utente database.
3. Aggiungi l'IP pubblico della VPS nella whitelist.
4. Copia la connection string in `MONGO_URL`.

## Controlli finali

1. `https://cp.limoneblu.it:8443` deve aprire CloudPanel.
2. `https://cp.limoneblu.it` deve servire il frontend.
3. `https://cp.limoneblu.it/api/` deve rispondere dal backend.
4. Dal backend verifica che Mongo sia raggiungibile.

## Ordine consigliato di deploy

1. Configura MongoDB Atlas.
2. Crea il sito in CloudPanel.
3. Avvia il backend FastAPI come servizio.
4. Builda il frontend.
5. Configura il reverse proxy `/api`.
6. Attiva SSL.
7. Verifica login, creazione preventivi e PDF.
