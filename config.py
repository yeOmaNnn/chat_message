import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "12345678910QWERTY")
    SQLALCHEMY_DATABASE_URI = "sqlite:///chat.db"
