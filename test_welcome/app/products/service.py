from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .models import Product
from .schemas import ProductCreate, ProductUpdate

class ProductService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list(self):
        result = await self.db.execute(select(Product))
        return result.scalars().all()

    async def create(self, item: ProductCreate):
        obj = Product(**item.dict())
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def read(self, id: int):
        result = await self.db.execute(select(Product).where(Product.id == id))
        return result.scalars().first()

    async def update(self, id: int, item: ProductUpdate):
        obj = await self.read(id)
        if not obj:
            return None
        
        for key, value in item.dict(exclude_unset=True).items():
            setattr(obj, key, value)
        
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def delete(self, id: int):
        obj = await self.read(id)
        if not obj:
            return None
        
        await self.db.delete(obj)
        await self.db.commit()
        return obj