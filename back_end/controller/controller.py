import ssl

from flask import Flask, redirect, request, jsonify
import asyncio
from hypercorn.asyncio import serve
from back_end.scripts import controller_script
import aiohttp

ORIGIN_SERVER = "https://localhost:9001"
REPLICA_SERVERS = [
    "https://localhost:9002",
    "https://localhost:9003"
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
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        async with session.post(origin_url, json={"filename": filename, "replica": replica}, ssl=ssl_context) as response:
            if response.status == 200:
                return jsonify({"message": f"Video pushed to replica"}), 200
            else:
                return jsonify({"error": "Failed to push video"}), response.status


if __name__ == "__main__":
    # app.run(host='0.0.0.0', port=9004)

    asyncio.run(serve(app, controller_script.config))
