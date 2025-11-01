import uvicorn
from fastapi import FastAPI
from fastapi.params import Depends
from sqlalchemy.orm import Session
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from Router.main_router import main_router

from DataBase import setup_database, get_session
from DBModel.model import ModelService

from sqlalchemy import select, func


app = FastAPI()
app.mount('/static', StaticFiles(directory='static', html=True), name='static')
app.include_router(main_router)
templates = Jinja2Templates(directory='templates')


INITIAL_SERVICES= [
    {"name": "Профессиональная гигиена",
     "description": "Комплексная чистка зубов, удаление зубного камня и налета для профилактики кариеса и заболеваний десен.",
     "price": 4500.00},
    {"name": "Лечение кариеса",
     "description": "Современное и безболезненное лечение с использованием высококачественных пломбировочных материалов.",
     "price": 6000.00},
    {"name": "Имплантация",
     "description": "Восстановление утраченных зубов с помощью современных имплантатов. Надежно и долговечно.",
     "price": 45000.00},
    {"name": "Ортодонтия (Брекеты)",
     "description": "Исправление прикуса и выравнивание зубов у детей и взрослых с использованием современных брекет-систем.",
     "price": 120000.00},
    {"name": "Эстетическая реставрация", "description": "Улучшение внешнего вида улыбки, виниры и отбеливание.",
     "price": 9500.00},
    {"name": "Хирургия", "description": "Удаление зубов любой сложности, в том числе зубов мудрости.",
     "price": 7000.00},
]


@app.post('/setup_database')
async def setup_db():
    await setup_database()


@app.post('/set_data_db')
async def insert_initial_services(session: Session = Depends(get_session)):
    """
    Проверяет, существуют ли услуги в БД, и если нет, вставляет начальный набор данных.
    """
    try:
        # Проверяем количество записей в таблице Service
        count_result = await session.execute(select(func.count(ModelService.service_id)))
        count = count_result.scalar_one()

        if count == 0:
            print("База данных услуг пуста. Заполнение начальными данными...")

            # Создаем объекты Service из словарей данных
            new_services = [ModelService(**data) for data in INITIAL_SERVICES]

            session.add_all(new_services)
            await session.commit()
            print(f"Успешно добавлено {len(new_services)} начальных услуг.")
        else:
            print(f"В таблице услуг уже есть {count} записей. Пропуск заполнения начальными данными.")

    except Exception as e:
        await session.rollback()
        print(f"Произошла ошибка при заполнении начальными услугами: {e}")



if __name__ == '__main__':
    uvicorn.run(app, port=5000)