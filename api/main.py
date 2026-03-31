from fastapi import FastAPI
from routes import users
from db.database import engine, Base
from routes import products, users

app = FastAPI()

app.include_router(products.router, prefix="/products", tags=["Products"])
app.include_router(users.router, prefix="/users", tags=["Users"])

Base.metadata.create_all(bind=engine)




        

