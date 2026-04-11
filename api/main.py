from fastapi import FastAPI
from api.db.database import engine, Base
from api.routes import product, user
from api import models

app = FastAPI()


app.include_router(
    product.router,
    prefix="/products",
    tags=["Products"]
)

app.include_router(
    user.router,
    prefix="/users",
    tags=["Users"]
)

Base.metadata.create_all(bind=engine)



        

