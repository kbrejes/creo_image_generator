# Deploy to Contabo Server

## Step 1: Create DNS Record

In your domain DNS settings, add:
```
Type: A
Name: creo
Value: [your Contabo server IP]
TTL: 300
```

Wait a few minutes for DNS to propagate.

---

## Step 2: Copy Files to Server

From your local machine:
```bash
# Create directory on server
ssh user@yourserver "mkdir -p /opt/creo"

# Copy project files
rsync -avz --exclude '__pycache__' --exclude '.git' --exclude 'outputs/*' \
  /Users/kirill/Documents/Dev\ Dev\ Dev/ACTIVE/creo_image_generator/ \
  user@yourserver:/opt/creo/
```

---

## Step 3: Create .env on Server

SSH into server:
```bash
ssh user@yourserver
cd /opt/creo
```

Edit `.env`:
```bash
nano .env
```

Contents:
```
HOST=0.0.0.0
PORT=8000
DEBUG=false
STORAGE_TYPE=local
STORAGE_LOCAL_PATH=/app/outputs
BASE_URL=https://creo.yourads.io

# API Keys
REPLICATE_API_TOKEN=your_replicate_token_here
OPENAI_API_KEY=your_openai_key_here  # Optional, for DALL-E
```

---

## Step 4: Check Docker Network

Your other services (Dify, n8n) probably share a network. Find it:
```bash
docker network ls
```

Look for something like `caddy_network` or `proxy_network`.

Update `docker-compose.yml` if needed:
```yaml
networks:
  caddy_network:  # Change to match your actual network name
    external: true
```

---

## Step 5: Add to Caddy/Nginx

If using **Caddy** (Caddyfile):
```
creo.yourads.io {
    reverse_proxy creo-api:8000
}
```

If using **nginx**:
```nginx
server {
    listen 443 ssl http2;
    server_name creo.yourads.io;

    ssl_certificate /path/to/cert;
    ssl_certificate_key /path/to/key;

    location / {
        proxy_pass http://creo-api:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Reload your proxy:
```bash
# For Caddy
docker exec -it caddy caddy reload --config /etc/caddy/Caddyfile

# For nginx
docker exec -it nginx nginx -s reload
```

---

## Step 6: Start the Container

```bash
cd /opt/creo
docker compose up -d --build
```

Check logs:
```bash
docker logs creo-api -f
```

---

## Step 7: Test

```bash
curl https://creo.yourads.io/
```

Should return:
```json
{"name":"Ad Creative Agent API","version":"1.0.0","status":"running"...}
```

---

## Step 8: Update Dify Workflow

In your Dify HTTP nodes, use:
- **Generate Image**: `https://creo.yourads.io/tools/generate-image`
- **Compose Ad**: `https://creo.yourads.io/pipeline/compose`

---

## Troubleshooting

### Container won't start
```bash
docker logs creo-api
```

### Network issues
```bash
# Make sure container is on the right network
docker network inspect caddy_network
```

### 502 Bad Gateway
- Check container is running: `docker ps`
- Check container name matches proxy config
- Check port 8000 is exposed

### API returns localhost URLs
- Check `BASE_URL` in `.env` is set to `https://creo.yourads.io`
- Rebuild: `docker compose up -d --build`
