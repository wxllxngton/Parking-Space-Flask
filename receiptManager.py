from peewee import *
from parkingSpotManager import *
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

#--------------------------- CONNECT TO DATABASE ------------------------------#
database_receipt = SqliteDatabase('databases/receipt.db')

''' Model definitions -- the standard "pattern" is to define a base model class that specifies which database to use.  then, any subclasses will automaticallyuse the correct storage'''
class BaseModel(Model):
    class Meta:
        database = database_receipt
        table_name = 'receipt'

# The user model specifies its fields (or columns) declaratively, like django
class Receipt(UserMixin, BaseModel):
    id = PrimaryKeyField(unique=True, null=False)
    user = CharField()
    time_in = IntegerField()
    time_out = IntegerField()
    price = IntegerField()
    status = CharField()
    product_name = CharField()
    spot_id = ForeignKeyField(ParkingSpot, to_field="id")

Receipt.create_table()

# import stripe
# stripe.api_key = "sk_test_51LcRknFAwMnZH9bVd5mgvKYK0nC1IpMG7bb9gUmC1b4H1v3Jh4MmY5hdFzGMDXnbJHJoHDKSc13nQkVy5sqz2J7d00v7yhA42P"


# id = [receipt.product_name for receipt in Receipt.select().where(Receipt.user == 'admin@gmail.com', Receipt.time_out == 1670394000)][0]

# print(stripe.Product.search(query=f"name:'{id}'",))

