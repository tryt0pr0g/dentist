from pydantic import BaseModel
from datetime import datetime, date, time


class AuthUser(BaseModel):
    login: str
    password: str


class RegUser(AuthUser):
    fio: str
    birthday: datetime


class AppointmentData(BaseModel):
    selected_date: date
    selected_time: time
    service_id: int


class AuthRequest(BaseModel):
    login: str
    password: str

# Pydantic-модель для успешного ответа (возвращаем только ID пользователя и логин)
class AuthResponse(BaseModel):
    user_id: int
    login: str