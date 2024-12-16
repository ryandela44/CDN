import os
import asyncio
import aiohttp
from aiohttp_asgi import ASGIResource
from aiohttp import web
from hypercorn.asyncio import serve
from hypercorn.config import Config

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

    file_size = os.path.getsize(path)
    headers = {
        'Content-Type': 'application/octet-stream',
        'Content-Length': str(file_size)
    }

    async with aiohttp.ClientSession() as session:
        with open(path, 'rb') as f:
            # Using ssl=False here for simplicity if self-signed certs are used elsewhere
            async with session.post(f"{replica}/cache_video/{filename}", data=f, headers=headers, ssl=False) as resp:
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

    # Convert aiohttp app to ASGI handler
    asgi_app = aiohttp_asgi.ASGIResource.__init__(app)

    config = Config()
    config.bind = [f"0.0.0.0:{ORIGIN_PORT}"]
    config.alpn_protocols = ["h3", "h2"]  # Enable HTTP/3 and HTTP/2
    config.certfile = "./cert.pem"
    config.keyfile = "./privkey.pem"
    config.ssl_handshake_timeout = 5

    loop.run_until_complete(serve(asgi_app, config))

if __name__ == '__main__':
    main()
