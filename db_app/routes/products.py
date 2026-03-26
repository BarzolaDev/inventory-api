from fastapi import APIRouter, Depends, HTTPException, status
from models.models import Product, StockMovement
from sqlalchemy.orm import Session
from schemas.schemas import ProductCreate, ProductPatch, MovementResponse
from db.database import get_db

router = APIRouter()

@router.post("/products")
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    db_product = Product(name=product.name, stock=product.stock)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.get("/products")
def get_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    return products

@router.patch("/products/{product_id}")
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

@router.get("/products/{product_id}/movements", response_model=list[MovementResponse])
def get_movements(product_id: int ,db: Session = Depends(get_db)):
    db_stock_movements = db.query(StockMovement).filter(
                            StockMovement.product_id == product_id
                            ).all()

    return db_stock_movements