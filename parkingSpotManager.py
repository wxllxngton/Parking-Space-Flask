from peewee import *
from locationManager import *
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

#--------------------------- CONNECT TO DATABASE ------------------------------#
database_parkingSpot = SqliteDatabase('databases/parkingSpot.db')

''' Model definitions -- the standard "pattern" is to define a base model class that specifies which database to use.  then, any subclasses will automaticallyuse the correct storage'''
class BaseModel(Model):
    class Meta:
        database = database_parkingSpot
        table_name = 'parkingspot'

# The user model specifies its fields (or columns) declaratively, like django
class ParkingSpot(UserMixin, BaseModel):
    id = PrimaryKeyField(unique=True, null=False)
    type = CharField()
    business_id = ForeignKeyField(Location, to_field="id")

ParkingSpot.create_table()


