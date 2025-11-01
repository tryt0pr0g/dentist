from fastapi import APIRouter, Request, Depends, Query
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates
from DataBase import AsyncSession, get_session
from DBModel.model import ModelService, ModelClient
from sqlalchemy import select


page_router = APIRouter()
templates = Jinja2Templates(directory='templates')


@page_router.get(path='/', response_class=HTMLResponse)
async def main_page(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})


@page_router.get("/auth")
async def auth(request: Request):
    return templates.TemplateResponse("auth.html", {"request": request})


@page_router.get("/reg")
async def reg(request: Request):
    return templates.TemplateResponse("reg.html", {"request": request})


@page_router.get("/profile")
async def profile(request: Request, db: AsyncSession = Depends(get_session)):
    # user = await db.execute(select(ModelClient).where(ModelClient.user_id == ...))
    return templates.TemplateResponse("profile.html", {"request": request})


@page_router.get("/catalog")
async def catalog(request: Request, db: AsyncSession = Depends(get_session)):
    """
    Получение списка услуг из БД.
    """

    # 1. Формируем запрос на выборку всех услуг, сортируем по ID
    query = select(ModelService).order_by(ModelService.service_id)

    # 2. Выполняем запрос асинхронно
    result = await db.execute(query)

    # 3. Получаем список объектов (Service)
    services_list = result.scalars().all()

    # Передаем список объектов услуг в шаблон
    return templates.TemplateResponse("catalog.html", {"request": request, "services": services_list})


@page_router.get("/appointment", response_class=HTMLResponse)
async def get_appointment_page(
        request: Request,
        session: AsyncSession = Depends(get_session),
        # ⚠️ Меняем service_id на service_name
        service_name: str = Query(None, alias="service_name")
):
    service_id = None

    # Имя услуги, которое будет отображаться в шаблоне
    display_name = "Не выбрана"

    # Если service_name передан, ищем его в БД
    if service_name:
        try:
            # Ищем ID и полное имя услуги по названию
            stmt = select(ModelService.service_id, ModelService.name).filter(ModelService.name == service_name)
            result = await session.execute(stmt)
            service_data = result.first()  # Получаем кортеж (service_id, name)

            if service_data:
                service_id, display_name = service_data
            else:
                # Если услуга с таким названием не найдена
                service_name = None

        except Exception as e:
            # Ошибка БД
            print(f"Database error on service lookup: {e}")
            service_name = None

    context = {
        "request": request,
        # Передаем service_id в шаблон (скрытое поле)
        "service_id": service_id,
        # Передаем название услуги для отображения пользователю
        "service_name": display_name,
        "title": "Запись на прием"
    }
    return templates.TemplateResponse("appointment.html", context)
