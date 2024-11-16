import requests
from aiohttp import ClientSession, FormData, ClientError
from flask import Flask, send_file, abort, jsonify, request
import asyncio
from hypercorn.asyncio import serve
from hypercorn.config import Config
import os
import aiohttp

app = Flask(__name__)


@app.route('/video/<filename>')
def stream_video(filename):
    path = os.path.join('./videos', filename)
    if os.path.exists(path):
        return send_file(path, as_attachment=False)
    else:
        abort(404, description="Video not found")


@app.route('/push_video', methods=['POST'])
async def push_video():
    data = request.json
    filename = data['filename']
    replica = data['replica']

    path = os.path.join('/', 'Users', 'macbookpro', 'PycharmProjects', 'CDN', 'back_end', 'videos', filename)
    if os.path.exists(path):
        url = f"{replica}/cache_video/{filename}"

        async with ClientSession() as session:
            with open(path, 'rb') as f:
                form = FormData()
                form.add_field('file', f, filename=filename, content_type='video/mp4')

                try:
                    async with session.post(url, data=form) as response:
                        if response.status == 200:
                            return jsonify({"message": f"Video pushed to {replica}"}), 200
                        else:
                            return jsonify({"error": "Failed to push video"}), response.status
                except ClientError as e:
                    return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": f"Video {filename} not found on origin server"}), 404

#@app.route('/push_video', methods=['POST'])
#def push_video():
 #   data = request.json
 #   filename = data['filename']
 #   replica = data['replica']

#    path = os.path.join('/', 'Users', 'macbookpro', 'PycharmProjects', 'CDN', 'back_end', 'videos', filename)
#    if os.path.exists(path):
#        url = f"{replica}/cache_video/{filename}"
#        with open(path, 'rb') as f:
#            try:
#                response = requests.post(url, files={'file': (filename, f, 'video/mp4')})
#                if response.status_code == 200:
#                    return jsonify({"message": f"Video pushed to {replica}"}), 200
#                else:
#                    return jsonify({"error": "Failed to push video"}), 500
#            except requests.exceptions.RequestException as e:
#                return jsonify({"error": str(e)}), 500
#    else:
#        return jsonify({"error": f"Video {filename} not found on origin server"}), 404


if __name__ == "__main__":
    # app.run(host='0.0.0.0', port=9001)
    config = Config()
    config.bind = ["0.0.0.0:9001"]
    config.alpn_protocols = ["h3"]  # Enable HTTP/3
    asyncio.run(serve(app, config))
