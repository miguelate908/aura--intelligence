from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CompanyCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)


class CustomerCreate(BaseModel):
    company_id: int = Field(gt=0)
    name: str = Field(min_length=1, max_length=150)
    email: Optional[str] = Field(default=None, max_length=150, pattern=r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
    phone: Optional[str] = Field(default=None, max_length=50)


class ProductCreate(BaseModel):
    company_id: int = Field(gt=0)
    sku: str = Field(min_length=1, max_length=100)
    name: str = Field(min_length=1, max_length=150)
    price: float = Field(default=0, ge=0)


class WarehouseCreate(BaseModel):
    company_id: int = Field(gt=0)
    name: str = Field(min_length=1, max_length=150)
    location: Optional[str] = Field(default=None, max_length=200)


class CustomerUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    email: Optional[str] = Field(default=None, max_length=150, pattern=r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
    phone: Optional[str] = Field(default=None, max_length=50)


class ProductUpdate(BaseModel):
    sku: str = Field(min_length=1, max_length=100)
    name: str = Field(min_length=1, max_length=150)
    price: float = Field(default=0, ge=0)


class WarehouseUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    location: Optional[str] = Field(default=None, max_length=200)


class InventoryCreate(BaseModel):
    product_id: int
    warehouse_id: int
    quantity: int = 0
    minimum_quantity: int = 0


class OrderCreate(BaseModel):
    company_id: int
    customer_id: int
    status: str = "pending"
    total: float = 0
class UserCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    company_name: str = Field(min_length=1, max_length=150)
    name: str = Field(min_length=1, max_length=150)
    email: str = Field(pattern=r"^[^\s@]+@[^\s@]+\.[^\s@]+$", max_length=150)
    password: str = Field(min_length=12, max_length=72)

    @field_validator("password")
    @classmethod
    def password_fits_bcrypt_byte_limit(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("La contraseña no puede superar 72 bytes en UTF-8")
        return value


class LoginRequest(BaseModel):
    email: str = Field(pattern=r"^[^\s@]+@[^\s@]+\.[^\s@]+$", max_length=150)
    password: str = Field(min_length=1, max_length=72)

    @field_validator("password")
    @classmethod
    def password_fits_bcrypt_byte_limit(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("La contraseña no puede superar 72 bytes en UTF-8")
        return value
