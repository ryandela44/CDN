import os
import asyncio
import aiohttp
from aiohttp import web

ORIGIN_PORT = int(os.environ.get('ORIGIN_PORT', 9001))
REPLICA_PORT_1 = int(os.environ.get('REPLICA_PORT_1', 9002))
REPLICA_PORT_2 = int(os.environ.get('REPLICA_PORT_2', 9003))
REPLICA_SERVERS = [f"http://localhost:{REPLICA_PORT_1}", f"http://localhost:{REPLICA_PORT_2}"]

CONTROLLER_PORT = int(os.environ.get('CONTROLLER_PORT', 9004))

current_index = 0


def round_robin_select():
    global current_index
    replica = REPLICA_SERVERS[current_index]
    current_index = (current_index + 1) % len(REPLICA_SERVERS)
    return replica


async def load_balance(request):
    filename = request.match_info.get('filename')
    if not filename:
        return web.json_response({"error": "Filename is missing"}, status=400)
    replica = round_robin_select()
    # Map the chosen replica to a path on Nginx
    if replica == f"http://localhost:{REPLICA_PORT_1}":
        # Use the /replica1/ path
        redirect_url = f"https://localhost:9008/replica1/video/{filename}"
    else:
        # Use the /replica2/ path
        redirect_url = f"https://localhost:9008/replica2/video/{filename}"

    raise web.HTTPFound(redirect_url)


async def cache_videos():
    async with aiohttp.ClientSession() as session:
        # Get video list from origin
        origin_url = f"http://localhost:{ORIGIN_PORT}/list_videos"
        async with session.get(origin_url) as resp:
            if resp.status == 200:
                video_list = await resp.json()
            else:
                print("Failed to fetch video list from origin")
                return

        # Push each video to replicas if not cached
        for video in video_list:
            for replica in REPLICA_SERVERS:
                is_cached_url = f"{replica}/is_cached/{video}"
                try:
                    async with session.get(is_cached_url) as check_resp:
                        if check_resp.status == 200:
                            cache_status = await check_resp.json()
                            if cache_status.get("cached", False):
                                print(f"Video {video} is already cached on {replica}")
                                continue
                except Exception as e:
                    print(f"Error checking cache status: {e}")
                    continue

                # Push video
                push_video_url = f"http://localhost:{ORIGIN_PORT}/push_video"
                payload = {"filename": video, "replica": replica}
                print(f"Pushing {video} from origin to {replica}...")
                try:
                    async with session.post(push_video_url, json=payload) as push_resp:
                        if push_resp.status == 200:
                            print(f"Video {video} successfully pushed to {replica}")
                        else:
                            print(f"Failed to push {video} to {replica}: {push_resp.status}")
                except Exception as e:
                    print(f"Error pushing {video} to {replica}: {e}")


async def init_app():
    # Pre-cache videos before serving requests
    await cache_videos()

    app = web.Application()
    app.add_routes([
        web.get('/video/{filename}', load_balance),
    ])
    return app


def main():
    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(init_app())
    web.run_app(app, host='0.0.0.0', port=CONTROLLER_PORT)


if __name__ == '__main__':
    main()
