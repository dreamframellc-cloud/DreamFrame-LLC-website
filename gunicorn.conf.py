import os

# Server socket - Render automatically sets PORT
bind = f"0.0.0.0:{os.environ.get('PORT', '10000')}"
backlog = 2048

# Worker processes - optimized for Cloud Run
workers = int(os.environ.get('GUNICORN_WORKERS', '1'))
worker_class = "sync"
worker_connections = 1000
timeout = int(os.environ.get('GUNICORN_TIMEOUT', '120'))
keepalive = 2

# Restart workers
max_requests = 1000
max_requests_jitter = 50
preload_app = True

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = 'dreamframe-gunicorn'

# Server mechanics - Render/Railway optimized
daemon = False
pidfile = None
user = None
group = None
tmp_upload_dir = None

# Cloud Run specific settings
forwarded_allow_ips = '*'
secure_scheme_headers = {'X-FORWARDED-PROTO': 'https'}

# SSL
keyfile = None
certfile = None