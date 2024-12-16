import random
import ssl

from aiohttp import ClientTimeout
from flask_cors import CORS
import aiohttp
from flask import Flask, redirect, jsonify
import asyncio
from hypercorn.asyncio import serve
from hypercorn import Config

ORIGIN_SERVER = "https://localhost:9001"
REPLICA_SERVERS = [
    "https://localhost:9002",
    "https://localhost:9003"
]

app = Flask(__name__)
CORS(app)


def random_select():
    return random.choice(REPLICA_SERVERS)


@app.route('/video/<filename>')
def load_balance(filename):
    print(filename)
    if not filename:
        return jsonify({"error": "Filename is missing"}), 400

    replica = random_select()
    return redirect(f'{replica}/video/{filename}')


async def cache_videos():
    """Cache all videos from origin to all replicas using the push_video endpoint."""
    async with aiohttp.ClientSession(timeout=ClientTimeout(total=600)) as session:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        # Fetch the list of videos from the origin server
        async with session.get(f"{ORIGIN_SERVER}/list_videos", ssl=ssl_context) as response:
            if response.status == 200:
                video_list = await response.json()
            else:
                print("Failed to fetch video list from origin")
                return

        # Push each video to all replicas
        for video in video_list:
            for replica in REPLICA_SERVERS:
                # Check if the video is already cached
                is_cached_url = f"{replica}/is_cached/{video}"
                try:
                    async with session.get(is_cached_url, ssl=ssl_context) as check_response:
                        if check_response.status == 200:
                            cache_status = await check_response.json()
                            if cache_status.get("cached", False):
                                print(f"Video {video} is already cached on {replica}")
                                continue
                except Exception as e:
                    print(f"Error checking cache status for {video} on {replica}: {e}")
                    continue

                # If not cached, push the video
                push_video_url = f"{ORIGIN_SERVER}/push_video"
                payload = {
                    "filename": video,
                    "replica": replica
                }

                print(f"Pushing {video} from origin to {replica}...")
                try:
                    async with session.post(push_video_url, json=payload, ssl=ssl_context) as push_response:
                        print(f"Protocol version: {push_response.version}")
                        if push_response.status == 200:
                            print(f"Video {video} successfully pushed to {replica}")
                        else:
                            print(f"Failed to push {video} to {replica}: {push_response.status}")
                except Exception as e:
                    print(f"Error pushing {video} to {replica}: {e}")


if __name__ == "__main__":
    # Cache videos on controller launch
    config = Config()
    config.bind = ["0.0.0.0:9004"]
    config.alpn_protocols = ["h3", "h2"]  # Include both HTTP/3 and HTTP/2
    config.certfile = "/Users/macbookpro/cert.pem"
    config.keyfile = "/Users/macbookpro/privkey.pem"
    config.ssl_handshake_timeout = 5
    asyncio.run(cache_videos())

    # Start the controller server
    asyncio.run(serve(app, config))
