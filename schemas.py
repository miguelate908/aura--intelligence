from typing import Optional



from pydantic import BaseModel





class CompanyCreate(BaseModel):

    name: str





class CustomerCreate(BaseModel):

    company_id: int

    name: str

    email: Optional[str] = None

    phone: Optional[str] = None





class ProductCreate(BaseModel):

    company_id: int

    sku: str

    name: str

    price: float = 0





class WarehouseCreate(BaseModel):

    company_id: int

    name: str

    location: Optional[str] = None


class EventCreate(BaseModel):
    company_id: int
    event_type: str
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    description: Optional[str] = None