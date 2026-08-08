import asyncio
import logging
from aiohttp import web

logger = logging.getLogger(__name__)

async def handle_health(request):
    return web.Response(text="OK", status=200)

async def start_health_server(port: int = 8080):
    app = web.Application()
    app.router.add_get("/health", handle_health)
    app.router.add_get("/", handle_health)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info(f"Health check server started on port {port}")
