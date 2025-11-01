from fastapi import APIRouter
from Router.page_router import page_router
from Router.user_api import user_router

main_router = APIRouter()
main_router.include_router(page_router)
main_router.include_router(user_router)