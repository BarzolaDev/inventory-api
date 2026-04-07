from fastapi import FastAPI
from api.db.database import engine, Base
from api.routes import products, users
from api import models

app = FastAPI()


app.include_router(
    products.router,
    prefix="/products",
    tags=["Products"]
)
app.include_router(
    users.router,
    prefix="/users",
    tags=["Users"]
)

Base.metadata.create_all(bind=engine)



        

