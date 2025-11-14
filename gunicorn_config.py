"""
Configuração do Gunicorn para melhor estabilidade no Render
"""
import multiprocessing
import os

# Número de workers (ajustar conforme necessário)
workers = int(os.environ.get('GUNICORN_WORKERS', 2))

# Timeout aumentado para operações longas (exportação de planilhas)
timeout = int(os.environ.get('GUNICORN_TIMEOUT', 120))  # 2 minutos

# Keep-alive
keepalive = 5

# Logging
accesslog = '-'
errorlog = '-'
loglevel = os.environ.get('GUNICORN_LOG_LEVEL', 'info')

# Worker class
worker_class = 'sync'

# Worker connections
worker_connections = 1000

# Max requests (reiniciar worker após N requisições para evitar memory leaks)
max_requests = 1000
max_requests_jitter = 50

# Preload app (melhor para memória)
preload_app = True

# Graceful timeout
graceful_timeout = 30

