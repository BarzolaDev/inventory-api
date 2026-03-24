from fastapi import FastAPI, Depends, HTTPException, status
from db.database import engine, Base, SessionLocal
from models.models import Product, StockMovement
from sqlalchemy.orm import Session
from schemas.schemas import ProductCreate, ProductPatch

app = FastAPI()

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db 
    finally:
        db.close()

@app.post("/products")
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    db_product = Product(name=product.name, stock=product.stock)
    #quiero guardar esto
    db.add(db_product)
    # lo guardo
    db.commit()
    # trae datos nuevos como el id
    db.refresh(db_product)
    # se lo doy al cliente
    return db_product

@app.get("/products")
def get_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    return products

@app.patch("/products/{product_id}")
def update_stock(product_id: int, stock_n: ProductPatch, db: Session = Depends(get_db)):
    
    product = db.query(Product).filter(Product.id == product_id).first() 

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = f'El producto con id {product_id} no existe')

    new_stock = stock_n.stock + product.stock

    if new_stock < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Stock insuficiente para realizar la operación'
        )
    
    #aca tendra que ir el stock movement 
    movement = StockMovement(
        product_id = product.id,
        quantity = stock_n.stock,
    )
    db.add(movement)

    product.stock = new_stock

    db.commit()
    db.refresh(product)

    return product