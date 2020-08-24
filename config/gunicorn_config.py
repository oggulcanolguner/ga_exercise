import multiprocessing

workers = multiprocessing.cpu_count()
bind = "0.0.0.0:8000"
keepalive = 60
worker_class = "gthread"
threads = 3
timeout = 120

chdir = "/app"
