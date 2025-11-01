from DataBase import ModelORM
from sqlalchemy import String, Date, Float, ForeignKey, Time
from sqlalchemy.orm import Mapped, mapped_column
from datetime import date
from typing import Optional

from datetime import time


class ModelClient(ModelORM):
    __tablename__ = 'users'

    user_id: Mapped[int] = mapped_column(primary_key=True, unique=True, autoincrement=True)
    fio: Mapped[str] = mapped_column(String(250))
    birthday: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    login: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))

    def __repr__(self):
        return f"<ModelClient(id={self.user_id}, login='{self.login}')>"


class ModelService(ModelORM):
    __tablename__ = 'services'

    service_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(String(1000))
    price: Mapped[float] = mapped_column(Float, nullable=False)


class Appointment(ModelORM):
    __tablename__ = 'appointments'

    appointment_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # Предполагаем, что ForeignKey() настроен правильно
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    service_id: Mapped[int] = mapped_column(ForeignKey("services.service_id"))
    date: Mapped[date] = mapped_column(Date)
    # Используем Time для корректного хранения времени
    time: Mapped[time] = mapped_column(Time, nullable=False)