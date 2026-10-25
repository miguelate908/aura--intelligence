from sqlalchemy.orm import Session

from models import Company, Product, Customer, Warehouse


def query_products_by_company(
    db: Session,
    company_id: int
):
    return (
        db.query(Product)
        .filter(Product.company_id == company_id)
        .all()
    )


def query_customers_by_company(
    db: Session,
    company_id: int
):
    return (
        db.query(Customer)
        .filter(Customer.company_id == company_id)
        .all()
    )


def query_warehouses_by_company(
    db: Session,
    company_id: int
):
    return (
        db.query(Warehouse)
        .filter(Warehouse.company_id == company_id)
        .all()
    )


def query_company_summary(
    db: Session,
    company_id: int
):
    company = (
        db.query(Company)
        .filter(Company.id == company_id)
        .first()
    )

    if company is None:
        return None

    products = query_products_by_company(
        db,
        company_id
    )

    customers = query_customers_by_company(
        db,
        company_id
    )

    warehouses = query_warehouses_by_company(
        db,
        company_id
    )

    return {
        "company": {
            "id": company.id,
            "name": company.name
        },
        "products": [
            {
                "id": product.id,
                "sku": product.sku,
                "name": product.name,
                "price": product.price
            }
            for product in products
        ],
        "customers": [
            {
                "id": customer.id,
                "name": customer.name,
                "email": customer.email,
                "phone": customer.phone
            }
            for customer in customers
        ],
        "warehouses": [
            {
                "id": warehouse.id,
                "name": warehouse.name,
                "location": warehouse.location
            }
            for warehouse in warehouses
        ]
    }