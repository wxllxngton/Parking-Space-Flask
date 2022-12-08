from peewee import *
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user


#--------------------------- CONNECT TO DATABASE ------------------------------#
database_feedback = SqliteDatabase('databases/feedback.db')

''' Model definitions -- the standard "pattern" is to define a base model class that specifies which database to use.  then, any subclasses will automaticallyuse the correct storage'''
class BaseModel(Model):
    class Meta:
        database = database_feedback
        table_name = 'feedback'
# The user model specifies its fields (or columns) declaratively, like django
class Feedback(UserMixin, BaseModel):
    id = PrimaryKeyField(unique=True, null=False)
    fname = CharField()
    comment = CharField()

Feedback.create_table()


