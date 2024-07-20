import os
import random
from typing import List

from fastapi import FastAPI, Depends, HTTPException, Query, UploadFile, File, BackgroundTasks
from fastapi_users import FastAPIUsers

from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import select, update, insert
from sqlalchemy.ext.asyncio import AsyncSession

from auth.Manager import get_user_manager
from auth.auth import auth_backend
from auth.database import User, get_async_session
from auth.schemas import UserRead, UserCreate

from db_models.models import users, user_models
from training.training_file import train_model_async

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PUT", "PATCH"],
    allow_headers=["*"],
)

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

current_user = fastapi_users.current_user()


@app.get("/protected-route")
def protected_route(user: User = Depends(current_user)):
    return f"Hello, {user.email}"

class UserBase(BaseModel):
    email: str

class UserUsername(BaseModel):
    username: str

@app.get("/get_username", response_model=UserUsername)
async def get_username(email: str = Query(...), session: AsyncSession = Depends(get_async_session)):
    async with session.begin():
        # Поиск пользователя по email
        result = await session.execute(select(users.c.username).where(users.c.email == email))
        user = result.fetchone()

        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        username = user._mapping["username"]
        return {"username": username}
class UserPremiumStatus(BaseModel):
    email: str
    is_premium: bool

@app.get("/check_premium", response_model=List[UserPremiumStatus])
async def check_premium(email: str, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(users).where(users.c.email == email))
    users_data = result.fetchall()

    users_list = []
    for user in users_data:
        user_dict = dict(user._mapping)
        user_dict["is_premium"] = user_dict["status_id"] == 2
        users_list.append({
            "email": user_dict["email"],
            "is_premium": user_dict["is_premium"]
        })

    return users_list


@app.post("/upgrade")
async def upgrade(email: str, session: AsyncSession = Depends(get_async_session)):
    async with session.begin():
        result = await session.execute(select(users).where(users.c.email == email))
        user = result.fetchone()

        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        user_dict = dict(user._mapping)

        if user_dict["status_id"] == 2:
            return {"message": "User already has premium status"}

        await session.execute(
            update(users)
            .where(users.c.email == email)
            .values(status_id=2)
        )

        return {"message": "User status updated to premium"}

async def generate_unique_token(session: AsyncSession):
    while True:
        token = f"{random.randint(1000, 9999)}"
        result = await session.execute(select(user_models).where(user_models.c.token == token))
        existing_token = result.fetchone()
        if existing_token is None:
            return token

@app.post("/create_model")
async def create_model(
        model_name: str,
        model_description: str,
        email: str,
        background_tasks: BackgroundTasks,
        file: UploadFile = File(...),
        session: AsyncSession = Depends(get_async_session)
):
    async with session.begin():
        # Поиск пользователя по email
        result = await session.execute(select(users).where(users.c.email == email))
        user = result.fetchone()

        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        user_id = user._mapping["id"]
        status_id = user._mapping["status_id"]

        # Проверка количества моделей, созданных пользователем, если он не премиум
        model_count_result = await session.execute(select(user_models).where(user_models.c.user_id == user_id))
        model_count = model_count_result.rowcount

        if status_id == 1 and model_count >= 1:
            raise HTTPException(status_code=400, detail="Non-premium users can create only one model")

        elif status_id == 2 and model_count >= 5:
            raise HTTPException(status_code=400, detail="Premium users can create only five model")

        # Генерация уникального токена
        token = await generate_unique_token(session)

        # Сохранение загруженного файла
        file_path = f"data/{file.filename}"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        # Запуск тренировки модели в фоне с обработкой исключений
        async def train_and_save():
            try:
                await train_model_async('data/' + file.filename, token, model_name, num_of_epochs=3)
                # Вставка новой модели в таблицу user_models
                new_model = {
                    "model_name": model_name,
                    "model_description": model_description,
                    "user_id": user_id,
                    "token": token
                }
                async with session.begin():
                    await session.execute(insert(user_models).values(new_model))
            except Exception as e:
                print(f"Training failed: {e}")
                raise HTTPException(status_code=500, detail="Training failed due to an error")

        background_tasks.add_task(train_and_save)

        return {"message": "Model creation and training started in background"}


@app.post("/finetune_model")
async def finetune_model(
        token: str,
        background_tasks: BackgroundTasks,
        file: UploadFile = File(...),
        session: AsyncSession = Depends(get_async_session)
):
    async with session.begin():
        # Поиск модели по токену
        result = await session.execute(select(user_models).where(user_models.c.token == token))
        model = result.fetchone()

        if model is None:
            raise HTTPException(status_code=404, detail="Model not found")

        trained_name = model._mapping["model_name"]

        # Сохранение загруженного файла
        file_path = f"data/{file.filename}"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        # Запуск тренировки модели в фоне с обработкой исключений
        async def train_and_save():
            try:
                await train_model_async('data/' + file.filename, token, trained_name, num_of_epochs=3)
            except Exception as e:
                print(f"Training failed: {e}")
                raise HTTPException(status_code=500, detail="Training failed due to an error")

        background_tasks.add_task(train_and_save)

        return {"message": "Model fine-tuning started in background"}


@app.get("/get_user_models")
async def get_user_models(email: str = Query(...), session: AsyncSession = Depends(get_async_session)):
    async with session.begin():
        # Поиск пользователя по email
        result = await session.execute(select(users).where(users.c.email == email))
        user = result.fetchone()

        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        user_id = user._mapping["id"]

        # Проверка наличия модели с токеном 0000
        default_model_result = await session.execute(
            select(user_models).where(user_models.c.token == '0000')
        )
        default_model = default_model_result.fetchone()

        if not default_model:
            # Добавление дефолтной модели, если она отсутствует
            default_model_data = {
                "token": '0000',
                "model_name": "Andrey",
                "model_description": (
                    "I am an ordinary student at Innopolis University. "
                    "I like to order food from Bazzar and discuss the Innotyaga sports club. "
                    "By the way, I am one of its creators :) See you at Innotyaga"
                ),
                "user_id": user_id
            }
            await session.execute(insert(user_models).values(default_model_data))

        # Поиск всех моделей, созданных пользователем, исключая модель с токеном 0000
        models_result = await session.execute(
            select(user_models).where(user_models.c.user_id == user_id).where(user_models.c.token != '0000')
        )
        models = models_result.fetchall()

        # Конвертация результата в список словарей
        models_list = [dict(model._mapping) for model in models]

        return models_list