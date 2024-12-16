import os
import asyncio
from aiohttp import web

CACHE_DIR_1 = os.environ.get('CACHE_DIR_1', './videos1')
REPLICA_PORT_1 = int(os.environ.get('REPLICA_PORT_1', 9002))
os.makedirs(CACHE_DIR_1, exist_ok=True)


async def stream_video(request):
    filename = request.match_info['filename']
    path = os.path.join(CACHE_DIR_1, filename)
    if os.path.isfile(path):
        return web.FileResponse(path)
    else:
        return web.json_response({"error": "Video not found"}, status=404)


async def cache_video(request):
    filename = request.match_info['filename']
    path = os.path.join(CACHE_DIR_1, filename)

    # Write incoming data to file
    try:
        with open(path, 'wb') as f:
            while True:
                chunk = await request.content.readany()
                if not chunk:
                    break
                f.write(chunk)
        return web.json_response({"message": f"Video {filename} cached successfully"})
    except Exception as e:
        return web.json_response({"error": f"Failed to cache video: {str(e)}"}, status=500)


async def is_cached(request):
    filename = request.match_info['filename']
    path = os.path.join(CACHE_DIR_1, filename)
    return web.json_response({"cached": os.path.isfile(path)})


async def init_app():
    app = web.Application()
    app.add_routes([
        web.get('/video/{filename}', stream_video),
        web.post('/cache_video/{filename}', cache_video),
        web.get('/is_cached/{filename}', is_cached),
    ])
    return app


def main():
    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(init_app())
    web.run_app(app, host='0.0.0.0', port=REPLICA_PORT_1)


if __name__ == '__main__':
    main()
