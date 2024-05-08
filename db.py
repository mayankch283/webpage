import json

class Hotel:
    def __init__(self, id, name):
        self.id = id
        self.name = name

class Order:
    def __init__(self, id, customer_name, hotel_id, room_type, check_in_date, check_out_date):
        self.id = id
        self.customer_name = customer_name
        self.hotel_id = hotel_id
        self.room_type = room_type
        self.check_in_date = check_in_date
        self.check_out_date = check_out_date

def load_hotels(filename):
    with open(filename) as f:
        hotels = json.load(f)
    return [Hotel(hotel['id'], hotel['name']) for hotel in hotels]

def load_orders(filename):
    with open(filename) as f:
        orders = json.load(f)
    return [Order(order['id'], order['customer_name'], order['hotel_id'], order['room_type'], order['check_in_date'], order['check_out_date']) for order in orders]