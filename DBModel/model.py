from DataBase import ModelORM
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, DateTime, func, text, Numeric, Time, Date
from sqlalchemy.dialects.postgresql import INET
from typing import Annotated
from decimal import Decimal
from datetime import datetime, time, date


intPK = Annotated[int, mapped_column(primary_key=True, unique=True, autoincrement=True)]


class ModelClient(ModelORM):
    __tablename__ = 'clients'

    client_id: Mapped[intPK]
    fio: Mapped[str] = mapped_column(String(100))
    login: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    is_kid: Mapped[bool] = mapped_column(server_default=text('false'))
    ip_address: Mapped[str] = mapped_column(INET)

    appointments: Mapped["AppointmentModel"] = relationship(back_populates="client")


class ModelService(ModelORM):
    __tablename__ = 'services'

    service_id: Mapped[intPK]
    name: Mapped[str] = mapped_column(String(50))
    description: Mapped[str] = mapped_column(String(300))
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    duration: Mapped[time] = mapped_column(Time)

    service_appointments_links: Mapped["AppointmentServiceModel"] = relationship(back_populates="service")


class ProfessionModel(ModelORM):
    __tablename__ = 'professions'

    profession_id: Mapped[intPK]
    title: Mapped[str] = mapped_column(String(50))
    salary: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    premium: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    employees: Mapped["EmployeeModel"] = relationship(back_populates="profession")


class GenderModel(ModelORM):
    __tablename__ = 'genders'

    gender_id: Mapped[intPK]
    title: Mapped[str] = mapped_column(String(15))


class EmployeeModel(ModelORM):
    __tablename__ = 'employees'

    employee_id: Mapped[intPK]
    fio: Mapped[str] = mapped_column(String(100))
    birthday: Mapped[datetime] = mapped_column(DateTime)
    date_of_employment: Mapped[date] = mapped_column(Date, server_default=func.now())
    gender_id: Mapped[int] = mapped_column(ForeignKey('genders.gender_id'))
    profession_id: Mapped[int] = mapped_column(ForeignKey('professions.profession_id'))
    on_leave: Mapped[bool] = mapped_column(server_default=text('false'))
    office_id: Mapped[int] = mapped_column(ForeignKey('offices.office_id'))

    profession: Mapped["ProfessionModel"] = relationship(back_populates="employees")
    office: Mapped["OfficeModel"] = relationship(back_populates="employee")
    appointments: Mapped["AppointmentModel"] = relationship(back_populates="employee")
    gender: Mapped["GenderModel"] = relationship()


class AppointmentModel(ModelORM):
    __tablename__ = 'appointments'

    appointment_id: Mapped[intPK]
    client_id: Mapped[int] = mapped_column(ForeignKey('clients.client_id'))
    employee_id: Mapped[int] = mapped_column(ForeignKey('employees.employee_id'))
    note: Mapped[str] = mapped_column(String(300))
    appointment_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    is_cancelled: Mapped[bool] = mapped_column(server_default=text('false'))

    client: Mapped["ModelClient"] = relationship(back_populates="appointments")
    employee: Mapped["EmployeeModel"] = relationship(back_populates="appointments")
    appointment_services: Mapped["AppointmentServiceModel"] = relationship(back_populates="appointment")


class OfficeModel(ModelORM):
    __tablename__ = 'offices'

    office_id: Mapped[intPK]
    number: Mapped[int]

    employee: Mapped["EmployeeModel"] = relationship(back_populates="office")


class AppointmentServiceModel(ModelORM):
    __tablename__ = 'appointments_services'

    appointment_service_id: Mapped[intPK]
    appointment_id: Mapped[int] = mapped_column(ForeignKey('appointments.appointment_id'))
    service_id: Mapped[int] = mapped_column(ForeignKey('services.service_id'))

    service: Mapped["ModelService"] = relationship(back_populates="service_appointments_links")
    appointment: Mapped["AppointmentModel"] = relationship(back_populates="appointment_services")