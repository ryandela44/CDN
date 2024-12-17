import os
import asyncio
import aiohttp
from aiohttp import web

VIDEO_DIR = os.environ.get('VIDEO_DIR', './videos')
ORIGIN_PORT = int(os.environ.get('ORIGIN_PORT', 9001))


async def list_videos(request):
    videos = [f for f in os.listdir(VIDEO_DIR) if os.path.isfile(os.path.join(VIDEO_DIR, f))]
    return web.json_response(videos)


async def stream_video(request):
    filename = request.match_info['filename']
    path = os.path.join(VIDEO_DIR, filename)
    if os.path.isfile(path):
        return web.FileResponse(path)
    else:
        raise web.HTTPNotFound(text="Video not found")


async def push_video(request):
    data = await request.json()
    filename = data.get('filename')
    replica = data.get('replica')

    if not filename or not replica:
        return web.json_response({"error": "Filename or replica missing"}, status=400)

    path = os.path.join(VIDEO_DIR, filename)
    if not os.path.isfile(path):
        return web.json_response({"error": f"Video '{filename}' not found"}, status=404)

    # Send video to replica
    file_size = os.path.getsize(path)
    headers = {
        'Content-Type': 'application/octet-stream',
        'Content-Length': str(file_size)
    }

    async with aiohttp.ClientSession() as session:
        with open(path, 'rb') as f:
            async with session.post(f"{replica}/cache_video/{filename}", data=f, headers=headers) as resp:
                if resp.status == 200:
                    return web.json_response({"message": f"Video pushed to {replica}"})
                else:
                    body = await resp.text()
                    return web.json_response({"error": f"Failed to push video: {resp.status}, {body}"},
                                             status=resp.status)


async def init_app():
    app = web.Application()
    app.add_routes([
        web.get('/list_videos', list_videos),
        web.get('/video/{filename}', stream_video),
        web.post('/push_video', push_video)
    ])
    return app


def main():
    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(init_app())
    web.run_app(app, host='0.0.0.0', port=ORIGIN_PORT)


if __name__ == '__main__':
    main()
