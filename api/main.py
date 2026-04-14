from fastapi import FastAPI
from api.routes import product, user

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



        

