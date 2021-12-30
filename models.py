from sqlalchemy import (create_engine, Column, Integer, String, ForeignKey)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql.selectable import FromClause
from sqlalchemy.sql.sqltypes import Date 

engine = create_engine("sqlite:///inventory.db", echo=False)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

class Brand(Base):

    __tablename__ = "Brands"

    brand_id = Column(Integer, primary_key=True)
    brand_name = Column(String)
    product = relationship("Product", back_populates="brand")

    def __repr__(self):
        return f'\nBrand ID: {self.brand_id}\rBrand Name: {self.brand_name}'

class Product(Base):

    __tablename__ = "Products"

    product_id = Column(Integer, primary_key=True)
    product_name = Column(String)
    product_quantity = Column(Integer)
    product_price = Column(Integer)
    date_updated = Column(Date)
    brand_id = Column(Integer, ForeignKey("Brands.brand_id"))
    brand = relationship("Brand", back_populates="product")

    def __repr__(self):
        return f"""
        \nProduct ID: {self.product_id}\r
        Product Name: {self.product_name}\r
        Quantity: {self.product_quantity}\r
        Price: {self.product_price}\r
        Date Last Updated: {self.date_updated}"""

if __name__ == '__main__':
    Base.metadata.create_all(engine)
