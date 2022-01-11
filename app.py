from sqlalchemy.engine import create_engine
from models import (Base, session, Brand, Product, engine)
from sqlalchemy import (func, desc)
import datetime
import csv
import time

def menu():
    options = ['V', 'N', 'A', 'B']
    while True: 
        choice = input('''\nPlease choose from the following options:
        \rPress V to view product details
        \rPress N to add a new product
        \rPress A to view an analysis of items 
        \rPress B to backup the database\n''').upper()
        if choice in options:
            return choice 
        else:
            print("***ERROR*** \nThat is an invalid option!")
            continue


def clean_price(price_str):
    if price_str[0] == '$':
        price_float = float(price_str[1: ])
        return int(price_float * 100)
    else:
        try:
            price_float = float(price_str)
            return int(price_float * 100)
        except ValueError:
            input('''
            \n***ERROR***
            please input a valid price (E.g. 3.99)
            ------------------------
            ''')
            return

def clean_date(date_str):
    split_date = date_str.split('/')
    try:
        month = int(split_date[0])
        day = int(split_date[1])
        year = int(split_date[2])
        new_date = datetime.date(year, month, day)
    except ValueError:
        input('''
            \n*** DATE ERROR ***
            \rThe date format should be in the following format: mm\dd\yyyy (ex: 12/25/2021)
            \rPress enter to try again''')
        return
    else:
        return new_date


def clean_quant(quant_str):
    try:
        quant_int = int(quant_str)
    except ValueError:
        input('''
        \n*** ERROR **
        \rQuantity should be entered as a number
        \rPress ENTER to try again
        \r------------------------------------
        ''')
    else: 
        return quant_int
        


def add_csvbrands():
    with open('brands.csv') as csvfile: 
        data = csv.reader(csvfile)
        header = next(data)
        if header != None:
            for row in data:
                name = ' '.join(row) 
                new_brand = Brand(brand_name=name)
                if new_brand.brand_name not in [v[0] for v in session.query(Brand.brand_name).all()]:
                    session.add(new_brand)
                else:
                    continue
        session.commit()


def choose_brand():
    brands = session.query(Brand.brand_id, Brand.brand_name)
    id_list = [value for value, in session.query(Brand.brand_id).all()] 
    print("\nPlease choose from the following brands:")
    for brand_tuple in brands:
        id = brand_tuple[0]
        name = brand_tuple[1]
        print(f'{id}) {name}')
    while True: 
        brand_prompt = input("Please select the number for the corresponding brand, or press 0 if the brand is not listed\n")
        try:    
            brand_int = int(brand_prompt)
            if brand_int in id_list:
                return brand_int
            elif brand_int == 0:
                new_brand()
                return
            else: 
                print("That is not a valid number from the list")
                continue
        except ValueError:
            print("That is not a number! Please choose a number from the brand list")
            continue
            

def new_brand():
    brand_name = input("what is the brand name? ")
    new_brand = Brand(brand_name=brand_name)
    session.add(new_brand)
    session.commit()
    print(f"Thank you! {brand_name} has been added to the Brands database")
    return new_brand.brand_id



def add_inventory():
    with open('inventory.csv') as csvfile:
        data = csv.reader(csvfile)
        header = next(data)

        if header != None:   
            for row in data:
                product_name = row[0]
                quantity = clean_quant(row[2])
                price = clean_price(row[1])
                date_updated = clean_date(row[3])
                current_brand = session.query(Brand).filter(Brand.brand_name==row[4]).first()
                brand_id = current_brand.brand_id
                new_product = Product(product_name=product_name, product_quantity=quantity, 
                                    product_price=price, date_updated=date_updated, brand_id=brand_id)
                if (new_product.product_name, new_product.date_updated) not in session.query(Product.product_name, Product.date_updated).all():
                    session.add(new_product)
                else: 
                    continue
        session.commit()

def app():
    num_products = session.query(func.count(Product.product_id)).first()[0]
    app_running = True
    while app_running: 
        choice = menu()
        if choice == 'V':
            while True:
                try:
                    id_choice = int(input(f'Please enter a product ID number (between 1 and {num_products}): '))
                except ValueError:
                    input(f"""
                        ***ERROR***
                        \rPlease enter a valid number between 1 and {num_products}
                        \rPress ENTER to try again...""")
                else:
                    if id_choice in range(1,int(num_products + 1)):
                        prod_choice = session.query(Product).filter(Product.product_id==id_choice).first()
                        print(f'''
                        \n***{prod_choice.product_name}***
                        \rPrice: ${prod_choice.product_price / 100}
                        \rBrand: {prod_choice.brand.brand_name}
                        \rQuantity: {prod_choice.product_quantity}
                        \rDate Updated: {prod_choice.date_updated}
                        ''')
                        time.sleep(1.5)
                        input('\nPress ENTER to continue...')
                        break
                    else:
                        input(f"""
                        ***ERROR***
                        \rThat number is not in the system
                        \rPlease enter a valid number between 1 and {num_products}
                        \rPress ENTER to try again...""")
                        

        elif choice == 'N':
            prod_name = input('What is the name of the product? ')
            while True:
                try:
                    prod_quant = int(input('How many products are available? '))
                except ValueError:
                    input("""
                    ***ERROR***
                    \rPlease enter a numerical number of products available
                    \rPress ENTER to try again...""")
                    continue  
                else:
                    break
            while True:
                try:
                    prod_price = int(float(input('How much does the product cost? $')) * 100)
                except ValueError:
                    input("""
                    ***ERROR***
                    \rPlease enter a valid price (e.g. 3.99) 
                    \rPress ENTER to try again...""")
                    continue
                else:
                    break
            current_date = datetime.date.today()
            brand_id = choose_brand()
            new_product = Product(product_name=prod_name, product_quantity=prod_quant, 
                                    product_price=prod_price, date_updated=current_date, brand_id=brand_id)
            print(f"""
                    \nThe following is being added to the database:
                    \rProduct Name: {prod_name}
                    \rProduct Quantity: {prod_quant}
                    \rProduct Price: ${prod_price/100}
                    \rBrand: {session.query(Brand.brand_name).filter(Brand.brand_id==brand_id).first()[0]}""")
            time.sleep(1.5)
            session.add(new_product)
            session.commit()
                
        elif choice == 'A':
            priciest = session.query(Product.product_name, func.max(Product.product_price)).first()
            cheapest = session.query(Product.product_name, func.min(Product.product_price)).first()
            common_tuple = session.query(Product.brand_id, func.count(Product.brand_id)).group_by(Product.brand_id).order_by(desc(func.count(Product.brand_id))).first()
            common_brand = session.query(Brand.brand_name).filter(Brand.brand_id==common_tuple[0]).first()
            input(f'''
            ***ANALYSIS***
            \rMost expensive product: {priciest[0]}
            \rThe price is: ${priciest[1]/100}
            \r\nLeast expensive product is: {cheapest[0]}
            \rThe price is: ${cheapest[1]/100}
            \r\nThe most common brand is: {common_brand[0]}
            \rThe number of products {common_brand[0]} has is: {common_tuple[1]}
            \nPress ENTER to return to the main menu'''
            )

        elif choice == 'B':
            outfile = open('inventory_backup.csv', 'w', newline='')
            outcsv = csv.writer(outfile)
            outcsv.writerow(['product name', 'product price', 'product quantity', 'date updated'])
            products = session.query(Product).all()
            for prod in products: 
                outcsv.writerow([prod.product_name, prod.product_quantity, prod.product_price, prod.date_updated, prod.brand.brand_name])
            outfile.close()


if __name__ == '__main__':
    Base.metadata.create_all(engine)
    add_csvbrands()
    add_inventory()
    app()
