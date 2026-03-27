from fastapi import FastAPI
from db.database import engine, Base
from routes import products

app = FastAPI()

app.include_router(products.router, prefix="/products", tags=["Products"])

Base.metadata.create_all(bind=engine)




        

