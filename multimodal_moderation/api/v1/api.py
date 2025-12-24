from fastapi import APIRouter

from .endpoints import moderate_audio_file, moderate_image_file, moderate_video_file, moderate_text, health, analytics

api_router = APIRouter()

api_router.include_router(moderate_audio_file.router, tags=["moderate_audio_file"])
api_router.include_router(moderate_image_file.router, tags=["moderate_image_file"])
api_router.include_router(moderate_video_file.router, tags=["moderate_video_file"])
api_router.include_router(moderate_text.router, tags=["moderate_text"])
api_router.include_router(analytics.router, tags=["analytics"])
api_router.include_router(health.router, tags=["health"])