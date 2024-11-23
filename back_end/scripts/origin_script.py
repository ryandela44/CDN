from hypercorn.config import Config

config = Config()
config.bind = ["0.0.0.0:9001"]
config.alpn_protocols = ["h3", "h2", "http/1.1"]  # Include both HTTP/3 and HTTP/2
config.certfile = "/Users/macbookpro/cert.pem"
config.keyfile = "/Users/macbookpro/privkey.pem"
config.ssl_handshake_timeout = 5