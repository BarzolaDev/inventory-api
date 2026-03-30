from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from schemas.schemas import ProductCreate, MovementResponse, MovementCreate,Product
from db.database import get_db
from services import products_services

router = APIRouter()

@router.post("/")
def new_product(product: ProductCreate, db: Session = Depends(get_db)):
    new_pruduct = products_services.new_product(db=db, product_data=product)
    return new_pruduct

@router.get("/")
def get_products(db: Session = Depends(get_db)):
    products = products_services.get_products(db=db)
    return products

@router.post("/products/{product_id}/stock", response_model=Product)
def update_product_stock(
    product_id: int, 
    movement: MovementCreate, 
    db: Session = Depends(get_db)
):
    # Llamamos a tu service blindado
    return products_services.update_stock(product_id=product_id, movement_data=movement, db=db)
    

@router.get("/{product_id}/movements", response_model=list[MovementResponse])
def get_movements(product_id: int ,db: Session = Depends(get_db)):
    movements = products_services.get_movements(product_id=product_id, db=db)
    return movements