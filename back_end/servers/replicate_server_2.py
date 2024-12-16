from flask import Flask, send_file, jsonify, request
import os
import asyncio
from hypercorn.asyncio import serve
from hypercorn.config import Config

app = Flask(__name__)


@app.route('/video/<filename>')
def stream_video(filename):
    path = os.path.join('/', 'Users', 'macbookpro', 'PycharmProjects', 'CDN', 'back_end', 'videos2', filename)

    if os.path.exists(path):
        return send_file(path, as_attachment=False)
    else:
        return jsonify({"error": "Video not found"}), 404


@app.route('/cache_video/<filename>', methods=['POST'])
def cache_video(filename):
    path = os.path.join('/', 'Users', 'macbookpro', 'PycharmProjects', 'CDN', 'back_end', 'videos2', filename)
    with open(path, 'wb') as f:
        f.write(request.files['file'].read())
    return jsonify({"message": "Video cached successfully"}), 200


@app.route('/is_cached/<filename>', methods=['GET'])
def is_cached(filename):
    # Check if the video exists in the cache directory
    path = os.path.join('/', 'Users', 'macbookpro', 'PycharmProjects', 'CDN', 'back_end', 'videos2', filename)
    if os.path.exists(path):
        return jsonify({"cached": True}), 200
    else:
        return jsonify({"cached": False}), 200


if __name__ == "__main__":
    # app.run(host='0.0.0.0', port=9003)
    config = Config()
    config.bind = ["0.0.0.0:9003"]
    config.alpn_protocols = ["h3", "h2"]  # Include both HTTP/3 and HTTP/2
    config.certfile = "/Users/macbookpro/cert.pem"
    config.keyfile = "/Users/macbookpro/privkey.pem"
    config.ssl_handshake_timeout = 5

    asyncio.run(serve(app, config))
