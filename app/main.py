import random
import secrets
from datetime import datetime, timedelta
from typing import List

from fastapi import FastAPI, Depends, HTTPException, status, Request, Form
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from .database import get_db, engine
from . import models, schemas, auth

# Создаем таблицы в базе данных
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="StarSpin")

# Подключаем статические файлы и шаблоны
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Сегменты колеса (стандартная европейская рулетка)
WHEEL_SEGMENTS = [
    {"value": "0", "number": 0, "color": "green", "multiplier": 36, "is_even": False},
    {"value": "32", "number": 32, "color": "red", "multiplier": 36, "is_even": True},
    {"value": "15", "number": 15, "color": "black", "multiplier": 36, "is_even": False},
    {"value": "19", "number": 19, "color": "red", "multiplier": 36, "is_even": False},
    {"value": "4", "number": 4, "color": "black", "multiplier": 36, "is_even": True},
    {"value": "21", "number": 21, "color": "red", "multiplier": 36, "is_even": False},
    {"value": "2", "number": 2, "color": "black", "multiplier": 36, "is_even": True},
    {"value": "25", "number": 25, "color": "red", "multiplier": 36, "is_even": False},
    {"value": "17", "number": 17, "color": "black", "multiplier": 36, "is_even": False},
    {"value": "34", "number": 34, "color": "red", "multiplier": 36, "is_even": True},
    {"value": "6", "number": 6, "color": "black", "multiplier": 36, "is_even": True},
    {"value": "27", "number": 27, "color": "red", "multiplier": 36, "is_even": False},
    {"value": "13", "number": 13, "color": "black", "multiplier": 36, "is_even": False},
    {"value": "36", "number": 36, "color": "red", "multiplier": 36, "is_even": True},
    {"value": "11", "number": 11, "color": "black", "multiplier": 36, "is_even": False},
    {"value": "30", "number": 30, "color": "red", "multiplier": 36, "is_even": True},
    {"value": "8", "number": 8, "color": "black", "multiplier": 36, "is_even": True},
    {"value": "23", "number": 23, "color": "red", "multiplier": 36, "is_even": False},
    {"value": "10", "number": 10, "color": "black", "multiplier": 36, "is_even": True},
    {"value": "5", "number": 5, "color": "red", "multiplier": 36, "is_even": False},
    {"value": "24", "number": 24, "color": "black", "multiplier": 36, "is_even": True},
    {"value": "16", "number": 16, "color": "red", "multiplier": 36, "is_even": True},
    {"value": "33", "number": 33, "color": "black", "multiplier": 36, "is_even": False},
    {"value": "1", "number": 1, "color": "red", "multiplier": 36, "is_even": False},
    {"value": "20", "number": 20, "color": "black", "multiplier": 36, "is_even": True},
    {"value": "14", "number": 14, "color": "red", "multiplier": 36, "is_even": True},
    {"value": "31", "number": 31, "color": "black", "multiplier": 36, "is_even": False},
    {"value": "9", "number": 9, "color": "red", "multiplier": 36, "is_even": False},
    {"value": "22", "number": 22, "color": "black", "multiplier": 36, "is_even": True},
    {"value": "18", "number": 18, "color": "red", "multiplier": 36, "is_even": True},
    {"value": "29", "number": 29, "color": "black", "multiplier": 36, "is_even": False},
    {"value": "7", "number": 7, "color": "red", "multiplier": 36, "is_even": False},
    {"value": "28", "number": 28, "color": "black", "multiplier": 36, "is_even": True},
    {"value": "12", "number": 12, "color": "red", "multiplier": 36, "is_even": True},
    {"value": "35", "number": 35, "color": "black", "multiplier": 36, "is_even": False},
    {"value": "3", "number": 3, "color": "red", "multiplier": 36, "is_even": False},
    {"value": "26", "number": 26, "color": "black", "multiplier": 36, "is_even": True},
]

# Типы ставок
BET_TYPES = {
    "number": {"multiplier": 36, "description": "Ставка на конкретное число"},
    "red": {"multiplier": 2, "description": "Ставка на красное"},
    "black": {"multiplier": 2, "description": "Ставка на черное"},
    "even": {"multiplier": 2, "description": "Ставка на четное"},
    "odd": {"multiplier": 2, "description": "Ставка на нечетное"},
}

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("index.html", {"request": request, "segments": WHEEL_SEGMENTS})

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
async def register_user(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    # Проверка, существует ли пользователь
    db_user = db.query(models.User).filter(models.User.username == username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Имя пользователя уже используется")
    
    # Создание нового пользователя
    hashed_password = auth.get_password_hash(password)
    new_user = models.User(username=username, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Перенаправление на страницу логина
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/login")
async def login(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = auth.authenticate_user(db, username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль"
        )
    
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    response = RedirectResponse(url="/game", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return response

@app.get("/game", response_class=HTMLResponse)
async def game_page(request: Request, db: Session = Depends(get_db)):
    try:
        current_user = await auth.get_current_user(request=request, db=db)
        return templates.TemplateResponse(
            "game.html", 
            {
                "request": request, 
                "user": current_user,
                "segments": WHEEL_SEGMENTS
            }
        )
    except HTTPException:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/spin")
async def spin_wheel(
    request: Request,
    bet: schemas.BetCreate,
    db: Session = Depends(get_db)
):
    try:
        current_user = await auth.get_current_user(request=request, db=db)
        
        # Проверка, есть ли у пользователя достаточно звезд
        if current_user.stars < bet.amount:
            raise HTTPException(status_code=400, detail="Недостаточно звезд для ставки")
        
        # Выбор случайного сегмента
        result_segment = random.choice(WHEEL_SEGMENTS)
        
        # Обработка выигрыша в зависимости от типа ставки
        win_amount = 0
        won = False
        
        # Разбиваем ставку на тип и значение (если это число)
        bet_parts = bet.segment.split(':')
        bet_type = bet_parts[0]
        
        if bet_type == "number" and len(bet_parts) > 1:
            # Ставка на конкретное число
            bet_number = bet_parts[1]
            if result_segment["value"] == bet_number:
                win_amount = bet.amount * BET_TYPES["number"]["multiplier"]
                won = True
        elif bet_type == "red":
            # Ставка на красное
            if result_segment["color"] == "red":
                win_amount = bet.amount * BET_TYPES["red"]["multiplier"]
                won = True
        elif bet_type == "black":
            # Ставка на черное
            if result_segment["color"] == "black":
                win_amount = bet.amount * BET_TYPES["black"]["multiplier"]
                won = True
        elif bet_type == "even":
            # Ставка на четное
            if result_segment["is_even"] and result_segment["number"] != 0:
                win_amount = bet.amount * BET_TYPES["even"]["multiplier"]
                won = True
        elif bet_type == "odd":
            # Ставка на нечетное
            if not result_segment["is_even"] and result_segment["number"] != 0:
                win_amount = bet.amount * BET_TYPES["odd"]["multiplier"]
                won = True
        
        # Обновление звезд пользователя
        current_user.stars = current_user.stars - bet.amount + win_amount
        
        # Сохранение ставки
        new_bet = models.Bet(
            user_id=current_user.id,
            amount=bet.amount,
            segment=bet.segment,
            result=result_segment["value"],
            win_amount=win_amount
        )
        db.add(new_bet)
        db.commit()
        db.refresh(new_bet)
        db.refresh(current_user)
        
        return {
            "result": result_segment,
            "won": won,
            "win_amount": win_amount,
            "stars": current_user.stars
        }
    except HTTPException:
        raise HTTPException(status_code=401, detail="Не авторизован")

@app.get("/history", response_class=HTMLResponse)
async def history_page(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        current_user = await auth.get_current_user(request=request, db=db)
        # Получение истории ставок пользователя
        bets = db.query(models.Bet).filter(models.Bet.user_id == current_user.id).order_by(models.Bet.created_at.desc()).all()
        
        return templates.TemplateResponse(
            "history.html", 
            {
                "request": request, 
                "user": current_user,
                "bets": bets
            }
        )
    except HTTPException:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(key="access_token")
    return response 