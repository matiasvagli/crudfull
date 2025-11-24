from pydantic import BaseModel, ConfigDict




class ProductBase(BaseModel):

    name: str

    price: float


class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int
    model_config = ConfigDict(from_attributes=True)