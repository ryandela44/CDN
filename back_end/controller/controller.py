import os
import random
import ssl

from aiohttp import ClientTimeout
from flask_cors import CORS
import aiohttp
from flask import Flask, redirect, request, jsonify
import asyncio
from hypercorn.asyncio import serve
from hypercorn import Config

ORIGIN_SERVER = "https://localhost:9001"
REPLICA_SERVERS = [
    "https://localhost:9002",
    "https://localhost:9003"
]

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024 * 1024  # 5 GB
CORS(app)


def random_select():
    return random.choice(REPLICA_SERVERS)


@app.route('/video/<filename>')
def load_balance(filename):
    replica = random_select()
    return redirect(f'{replica}/video/{filename}')


@app.route('/push_video', methods=['POST'])
async def push_video_to_replica():
    data = request.json
    filename = data.get('filename')
    replica = REPLICA_SERVERS[0]

    origin_url = f"{ORIGIN_SERVER}/push_video"

    async with aiohttp.ClientSession(timeout=ClientTimeout(total=600)) as session:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        async with session.post(origin_url, json={"filename": filename, "replica": replica},
                                ssl=ssl_context) as response:
            if response.status == 200:
                return jsonify({"message": f"Video pushed to replica"}), 200
            else:
                return jsonify({"error": "Failed to push video"}), response.status


async def cache_videos():
    """Cache all videos from origin to all replicas using the push_video endpoint."""
    async with aiohttp.ClientSession(timeout=ClientTimeout(total=600)) as session:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        # Fetch the list of videos from the origin server
        async with session.get(f"{ORIGIN_SERVER}/list_videos", ssl=ssl_context) as response:
            if response.status == 200:
                video_list = await response.json()  # Assuming this returns a list of filenames
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


VIDEO_METADATA = {
    "video1.mp4": {"title": "Video 1", "author": "Author 1", "stats": "100 views",
                   "thumbnail": f"{ORIGIN_SERVER}/thumbnails/video1.jpg"},
    "video2.mp4": {"title": "Video 2", "author": "Author 2", "stats": "200 views",
                   "thumbnail": f"{ORIGIN_SERVER}/thumbnails/video2.jpg"},
    "video3.mp4": {"title": "Video 3", "author": "Author 3", "stats": "300 views",
                   "thumbnail": f"{ORIGIN_SERVER}/thumbnails/video3.jpg"},
    "video4.mp4": {"title": "Video 4", "author": "Author 4", "stats": "400 views",
                   "thumbnail": f"{ORIGIN_SERVER}/thumbnails/video4.jpg"},
    "video5.mp4": {"title": "Video 5", "author": "Author 5", "stats": "500 views",
                   "thumbnail": f"{ORIGIN_SERVER}/thumbnails/video5.jpg"},
}


@app.route('/list_videos_metadata', methods=['GET'])
def list_videos_metadata():
    """
    Provide metadata for all available videos.
    """
    video_folder = os.path.join('/', 'Users', 'macbookpro', 'PycharmProjects', 'CDN', 'back_end', 'videos')
    try:
        # Get the list of video files from the video folder
        video_files = os.listdir(video_folder)

        # Build metadata for each video, if available
        metadata = []
        for video in video_files:
            if video in VIDEO_METADATA:
                metadata.append(VIDEO_METADATA[video])
            else:
                # Fallback metadata if not defined
                metadata.append({
                    "title": video,
                    "author": "Unknown",
                    "stats": "0 views",
                    "thumbnail": f"{ORIGIN_SERVER}/thumbnails/{video}"
                })

        return jsonify(metadata), 200
    except Exception as e:
        return jsonify({"error": f"Failed to list video metadata: {str(e)}"}), 500


if __name__ == "__main__":
    # Cache videos on controller launch
    config = Config()
    config.bind = ["0.0.0.0:9004"]
    config.alpn_protocols = ["h3", "h2", "http/1.1"]  # Include both HTTP/3 and HTTP/2
    config.certfile = "/Users/macbookpro/cert.pem"
    config.keyfile = "/Users/macbookpro/privkey.pem"
    config.ssl_handshake_timeout = 5
    asyncio.run(cache_videos())

    # Start the controller server
    asyncio.run(serve(app, config))
