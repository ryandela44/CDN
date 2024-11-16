# hypercorn_config.py
bind = ["localhost:9004"]
certfile = "/path/to/your/cert.pem"  # Path to your SSL certificate
keyfile = "/path/to/your/key.pem"    # Path to your SSL key
alpn_protocols = ["h3", "http/1.1"]  # Enable HTTP/3 and HTTP/1.1 fallback
