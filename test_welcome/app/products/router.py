from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from .schemas import ProductCreate, ProductUpdate, ProductResponse
from .service import ProductService

# Import get_db from the project's database configuration
try:
    from app.db.session import get_db
except ImportError:
    # Fallback for different project structures
    try:
        from database import get_db
    except ImportError:
        from ...database_examples.database_sql_example import get_db

router = APIRouter(prefix="/products", tags=["Product"])

@router.get("/", response_model=List[ProductResponse])
async def list_products(db: AsyncSession = Depends(get_db)):
    service = ProductService(db)
    return await service.list()

@router.get("/{id}", response_model=ProductResponse)
async def read_product(id: int, db: AsyncSession = Depends(get_db)):
    service = ProductService(db)
    item = await service.read(id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.post("/", response_model=ProductResponse)
async def create_product(
    item: ProductCreate,
    db: AsyncSession = Depends(get_db)
):
    service = ProductService(db)
    return await service.create(item)

@router.patch("/{id}", response_model=ProductResponse)
async def update_product(id: int, item: ProductUpdate, db: AsyncSession = Depends(get_db)):
    service = ProductService(db)
    updated = await service.update(id, item)
    if not updated:
        raise HTTPException(status_code=404, detail="Item not found")
    return updated

@router.delete("/{id}", response_model=ProductResponse)
async def delete_product(id: int, db: AsyncSession = Depends(get_db)):
    service = ProductService(db)
    deleted = await service.delete(id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Item not found")
    return deleted