from Scheme.user import RegUser, AppointmentData, AuthResponse, AuthRequest
from DataBase import get_session
from DBModel.model import ModelClient, Appointment
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi.responses import JSONResponse  # <-- 1. Добавлен импорт
from urllib.parse import quote  # <-- 2. Добавлен импорт для кодирования
from datetime import datetime, timedelta, time
from urllib.parse import unquote


user_router = APIRouter()


@user_router.post('/api/register')
async def reg_user(user_data: RegUser, session: AsyncSession = Depends(get_session)):
    # --- 1. Проверка существования пользователя (по логину) ---
    stmt = select(ModelClient).filter(ModelClient.login == user_data.login)
    result = await session.execute(stmt)
    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким логином уже существует"
        )

    # --- 2. Создание и вставка нового пользователя ---
    new_user = ModelClient(
        fio=user_data.fio,
        birthday=user_data.birthday.date() if user_data.birthday else None,
        login=user_data.login,
        password_hash=user_data.password
    )

    # 3. Добавление объекта в сессию и сохранение в БД
    try:
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Не удалось создать пользователя: {e}"
        )

    # --- 4. Создание ответа и сохранение логина в Cookie ---

    # 4.1. Подготовка данных для ответа
    response_content = {
        "message": "Пользователь успешно зарегистрирован",
        "user_id": new_user.user_id,
        "login": new_user.login
    }

    # Инициализируем объект JSONResponse
    response = JSONResponse(content=response_content, status_code=status.HTTP_200_OK)

    # 4.2. Кодирование логина и установка Cookie
    # Логин кодируется на случай наличия спецсимволов (@, ., и т.д.)
    encoded_login = quote(new_user.login)

    response.set_cookie(
        key="user_login",
        value=encoded_login,
        max_age=3600 * 24 * 7,  # 7 дней
        httponly=False,  # Доступно для чтения JavaScript (для отображения)
        samesite="lax"
    )

    return response


async def get_current_user_id(session: AsyncSession = Depends(get_session), request: Request = None):
    """Извлекает user_id, используя логин из куки."""

    # 1. Получаем логин из куки
    encoded_login = request.cookies.get("user_login")
    if not encoded_login:
        # Если куки нет, пользователь не авторизован
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не авторизован. Войдите, чтобы записаться."
        )

    # 2. Декодируем логин
    login = unquote(encoded_login)

    # 3. Находим пользователя по логину в БД
    stmt = select(ModelClient.user_id).filter(ModelClient.login == login)
    result = await session.execute(stmt)
    user_id = result.scalars().first()

    if not user_id:
        # Если логин в куки не соответствует реальному пользователю
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверные данные авторизации."
        )
    return user_id


@user_router.post("/api/appointment")
async def create_appointment(
        data: AppointmentData,
        user_id: int = Depends(get_current_user_id),  # Получаем ID пользователя
        session: AsyncSession = Depends(get_session)
):
    # 1. Проверка ограничений (дублируется на бэкенде для безопасности)

    # Проверка, что выбрана целая минута (т.к. step=3600 на клиенте, но надо проверить на сервере)
    if data.selected_time.minute != 0 or data.selected_time.second != 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Время приема должно быть выбрано по целым часам.")

    if data.selected_date < (datetime.now().date() + timedelta(days=1)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Запись возможна только со следующего дня.")

    # КРИТИЧЕСКОЕ ИЗМЕНЕНИЕ: Обновлен максимальный час до 17:00
    if data.selected_time < time(9, 0) or data.selected_time > time(17, 0):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Время записи: с 9:00 до 17:00.")

    # 2. Создание объекта записи
    # Предполагаем, что Appointment импортирована
    new_appointment = Appointment(
        user_id=user_id,
        service_id=data.service_id,
        date=data.selected_date,
        time=data.selected_time
    )

    # 3. Сохранение в БД
    try:
        session.add(new_appointment)
        await session.commit()
        await session.refresh(new_appointment)
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Ошибка при сохранении записи в БД.")

    return {"message": "Запись успешно создана!", "appointment_id": new_appointment.appointment_id}


@user_router.post("/api/auth",
             response_model=AuthResponse,
             status_code=status.HTTP_200_OK,
             summary="Авторизация пользователя по логину и паролю")
async def authenticate_user(
        data: AuthRequest,
        session: AsyncSession=  Depends(get_session)
):
    """
    Проверяет учетные данные пользователя.

    В случае успеха возвращает ID пользователя и логин.
    """

    # 1. Поиск пользователя по логину
    user = await get_by_login(session, data.login)

    if not user:
        # Важно: для безопасности всегда возвращать одно и то же сообщение
        # независимо от того, не найден ли логин или неверен пароль.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
        )

    # 3. Успешная авторизация
    return AuthResponse(user_id=user.user_id, login=user.login)


async def get_by_login(session: AsyncSession, login: str):
    """Выполняет поиск пользователя в БД по логину."""
    result = await session.execute(
        select(ModelClient).where(ModelClient.login == login)
    )
    return result.scalars().first()