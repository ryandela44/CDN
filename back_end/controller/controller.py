import requests
from flask import Flask, redirect, request, jsonify
import asyncio
from hypercorn.asyncio import serve
from hypercorn.config import Config
import aiohttp

ORIGIN_SERVER = "http://localhost:9001"
REPLICA_SERVERS = [
    "http://localhost:9002",
    "http://localhost:9003"
]

app = Flask(__name__)


def round_robin():
    return REPLICA_SERVERS[0]


@app.route('/video/<filename>')
def load_balance(filename):
    replica = round_robin()
    return redirect(f'{replica}/video/{filename}')


@app.route('/push_video', methods=['POST'])
async def push_video_to_replica():
    data = request.json
    filename = data.get('filename')
    replica = round_robin()

    origin_url = f"{ORIGIN_SERVER}/push_video"

    async with aiohttp.ClientSession() as session:
        async with session.post(origin_url, json={"filename": filename, "replica": replica}) as response:
            if response.status == 200:
                return jsonify({"message": f"Video pushed to replica"}), 200
            else:
                return jsonify({"error": "Failed to push video"}), response.status

#@app.route('/push_video', methods=['POST'])
#def push_video_to_replica():
#    data = request.json
#    filename = data.get('filename')
#    replica = round_robin()
#
#    origin_url = f"{ORIGIN_SERVER}/push_video"
#    response = requests.post(origin_url, json={"filename": filename, "replica": replica})
#    if response.status_code == 200:
#        return jsonify({"message": f"Video pushed to replica"}), 200
#    else:
#        return jsonify({"error": "Failed to push video"}), response.status_code


if __name__ == "__main__":
    # app.run(host='0.0.0.0', port=9004)
    config = Config()
    config.bind = ["0.0.0.0:9001"]
    config.alpn_protocols = ["h3"]  # Enable HTTP/3
    asyncio.run(serve(app, config))
