from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import product, user

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


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



        

