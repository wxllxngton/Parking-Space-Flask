# Import Statements
from flask import Flask, redirect, request, render_template, url_for, flash, session
from flask_bootstrap import Bootstrap
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask import abort
from datetime import datetime
import time

import stripe

stripe_keys = {
  'secret_key': 'sk_test_51LcRknFAwMnZH9bVd5mgvKYK0nC1IpMG7bb9gUmC1b4H1v3Jh4MmY5hdFzGMDXnbJHJoHDKSc13nQkVy5sqz2J7d00v7yhA42P',
  'publishable_key': 'pk_test_51LcRknFAwMnZH9bVbmOBBJrvuD4QBkCZj03lfFRpBQ5cl09yC3rNGEZkga75QSYr713wjUURFvI8Si3Sn0hnXPR800Rc48cGma'
}

stripe.api_key = stripe_keys['secret_key']

#--------------------------- CONNECT TO DATABASE ------------------------------#
from usersManager import *
from locationManager import *
from parkingSpotManager import *
from receiptManager import *
from feedbackManager import *
#------------------------------------------------------------------------------#

c_o_c_i = None

################## FUNCTIONS ##################
def twelve_to_twentyfour(string):

      if string[-2:] == "AM" and string[:2] == "12":
         return "00" + string[2:-2]

      elif string[-2:] == "AM":
         return string[:-2]

      elif string[-2:] == "PM" and string[:2] == "12":
         return string[:-2]

      else:
          return str(int(string[:2]) + 12) + string[2:8]

# Config Flask
app = Flask(__name__)
'''Flask login
Make-shift secret key - login_manager only works in its presence'''
app.config['SECRET_KEY'] = 'any-secret-key-you-choose'

# Config ckEditor for blogs
ckeditor = CKEditor(app)


# Config Bootstrap
Bootstrap(app)


# Config LoginManager
login_manager = LoginManager()
# Confuguration
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.get(User.id == user_id)


# Decorator grants admin user privilages
def admin_only(function):
    @wraps(function)
    def decorated_function(*args, **kwargs):
        #If id is not 1 then return abort with 403 error
        if current_user.email != 'admin@gmail.com':
            return abort(403)
        #Otherwise continue with the route function
        return function(*args, **kwargs)
    return decorated_function

@app.route('/', methods=['GET', 'POST'])
def home():
    message = None
    permission = None
    permission_manage_reservations = None

    if request.args.get('message'):
        message = request.args.get('message')

    try:
        # if Receipt.get(Receipt.user == current_user.email, Receipt.status == 'Unpaid', Receipt.time_in >= int(datetime.timestamp(datetime.now()))) or request.args.get('check_in_time'):
        if Receipt.get(Receipt.user == current_user.email, Receipt.status == 'Unpaid', Receipt.time_in <= int(datetime.timestamp(datetime.now())) + 60):
            permission = True
    except:
        permission = False

    try:
        if Receipt.select().where(Receipt.user == current_user.email, Receipt.status == 'Unpaid'):
            permission_manage_reservations = True
    except:
        permission_manage_reservations = False

    print(f"CIT=============={request.args.get('check_in_time')}")
    global c_o_c_i
    c_o_c_i = request.args.get('check_in_time')
    if request.method == 'POST':
        Feedback.insert(fname=request.form['name'], comment=request.form['comment']).execute()
        return render_template('index.html', logged_in=current_user.is_authenticated, message='Comment has been successfully sent 👍', permission_checkout=permission, check_in_time=request.args.get('check_in_time'), permission_manage_reservations=permission_manage_reservations)
    return render_template('index.html', logged_in=current_user.is_authenticated, permission_checkout=permission, check_in_time=request.args.get('check_in_time'), permission_manage_reservations=permission_manage_reservations, message=message)

#----------------------------- MANAGE ACCOUNT ---------------------------------------#

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        # Setting parameters
        form_email = request.form['email']
        form_password = request.form['password']
        #Find user by email entered.
        try:
            user = User.select().where(User.email == form_email).get()
        except User.DoesNotExist:
            error = 'Invalid credentials!'
            return render_template("login.html", error=error, logged_in=current_user.is_authenticated)
        # Comapring data
        if check_password_hash(user.password,form_password):
            login_user(user)
            flash('You were successfully logged in')
            try:
                # Check whether user has any unpaid payments
                if Receipt.get(Receipt.user == current_user.email, Receipt.status == 'Unpaid', Receipt.time_in <= int(datetime.timestamp(datetime.now())) + 600):
                    check_in_time = Receipt.get(Receipt.user == current_user.email, Receipt.status == 'Unpaid', Receipt.time_in <= int(datetime.timestamp(datetime.now()))).time_in
                    # print("=================================")
                    # print(Receipt.get(Receipt.user == current_user.email, Receipt.status == 'Unpaid', Receipt.time_in >= int(datetime.timestamp(datetime.now()))).time_in)
                    print(f"CO===Login={check_in_time}")
                    global c_o_c_i
                    c_o_c_i = check_in_time
                    return redirect(url_for('check_out', check_in_time=check_in_time))
            except Exception as err:
                return redirect(url_for('check_in'))
        else:
            error = 'Invalid credentials!'
            return render_template("login.html", error=error, logged_in=current_user.is_authenticated)
    return render_template('login.html', logged_in=current_user.is_authenticated)


@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        # Validating the inputs
        if not request.form['password'] or not request.form['fname'] or not request.form['lname'] or not request.form['email']:
            return render_template("sign-up.html", logged_in=current_user.is_authenticated, error='Please fill all fields!')

        # Setting password
        password_hashed = generate_password_hash(password=request.form['password'], method="pbkdf2:sha256", salt_length=8)
        #Confirming existence of email
        try:
            # Inserting data
            User.insert(email=request.form['email'], password=password_hashed, fname=request.form['fname'], lname=request.form['lname']).execute()
            return render_template('login.html', logged_in=current_user.is_authenticated, error='Account created successfully 👍')
        except IntegrityError:
            error = 'You already have an account'
            return render_template("login.html", error=error)
    return render_template('sign-up.html', logged_in=current_user.is_authenticated)

#------------------------------------------------------------------------------#

#----------------------------- MANAGE RESERVATIONS ---------------------------------------#
@app.route('/manage-reservations')
def manage_reservations():
    message = None
    # reservations = Receipt.select().join(ParkingSpot).where(Receipt.user == current_user.email, Receipt.status == 'Unpaid', Receipt.time_in >= int(datetime.timestamp(datetime.now())))
    if request.args.get('message'):
        message = request.args.get('message')

    reservations = []
    for reservation in Receipt.select().where(Receipt.user == current_user.email, Receipt.status == 'Unpaid', Receipt.time_in >= int(datetime.timestamp(datetime.now()))):
        business_id = ParkingSpot.select().where(ParkingSpot.id == reservation.spot_id).get().business_id
        new_reservation = {
            "time_in" : datetime.fromtimestamp(reservation.time_in),
            "spot_id": reservation.spot_id,
            "location_name" : Location.select().where(Location.id == business_id).get().name
        }
        reservations.append(new_reservation)

    print(reservations)
    if reservations:
        return render_template('manage-reservations.html', logged_in=current_user.is_authenticated, reservations=reservations, check_in_time=request.args.get('check_in_time'), message=message)
    else:
        if request.args.get('check_in_time'):
            message = 'No other reservations made. Check out/Check in first!'
        return redirect(url_for('home', check_in_time=request.args.get('check_in_time'), message=message))

@app.route('/manage-reservations_cancel')
def manage_reservations_cancel():
    spot_id = int(request.args.get('spot_id'))
    check_in_time = int(request.args.get('check_in_time'))
    try:
        # Deletes the receipt
        q = Receipt.delete().where(Receipt.user == current_user.email, Receipt.status == 'Unpaid', Receipt.spot_id == spot_id)
        q.execute()

        # Updates the status of the spot to OPEN
        q = ParkingSpot.update(type='Open').where(ParkingSpot.id == spot_id)
        q.execute()
        return redirect(url_for('manage_reservations', check_in_time=check_in_time, message="Reservation has been successfully cancelled 👍"))
    except Receipt.DoesNotExist:
        return redirect(url_for('check_out', check_in_time=check_in_time, message="Receipt seems not to exist"))
#-----------------------------------------------------------------------------------------#



#----------------------------- CHECK IN ---------------------------------------#

@app.route('/check-in', methods=['GET','POST'])
def check_in():
    if request.method == 'POST':
        return redirect(url_for('search_by_location', location=request.form['location'].upper()))
    return render_template('check-in.html', locations=Location.select(), logged_in=current_user.is_authenticated)


@app.route('/check-in/<location>', methods=['GET','POST'])
def search_by_location(location):
    locations = None
    if location == 'ALL':
        locations = Location.select()
    else:
        locations = Location.select().where(Location.name == location)
    if request.method == 'POST':
        return redirect(url_for('search_by_location', location=request.form['location'].upper()))
    return render_template('check-in.html', locations=locations, logged_in=current_user.is_authenticated)


#------------------------------------------------------------------------------#

#----------------------------- DASHBOARD ---------------------------------------#


@app.route('/dashboard')
@admin_only
def dashboard():
    return render_template('dashboard.html', receipts=Receipt.select(), users=User.select(), locations=Location.select(), feeds=Feedback.select(), check_in_time=request.args.get('check_in_time'))


@app.route('/reports')
@admin_only
def reports():
    locations_names = {location.id:location.name for location in Location.select()}
    spots = []
    for spot in ParkingSpot.select():
        new_spot = {
            "id": spot.id,
            "type": spot.type,
            "location": locations_names[int(str(spot.business_id))]
        }
        spots.append(new_spot)
    return render_template('reports.html', p_spots=spots, check_in_time=request.args.get('check_in_time'))

#------------------------------------------------------------------------------#

#----------------------------- CHECK OUT ---------------------------------------#

@app.route('/calendar/<int:location_id>', methods=['GET','POST'])
def calendar(location_id):
    error = None
    if request.method == 'POST':
        date, time = request.form.get('datetime').split(' ')[0], twelve_to_twentyfour(request.form.get('datetime').split(' ')[1]+request.form.get('datetime').split(' ')[2])
        print("24-hour Format time ::",twelve_to_twentyfour(time))
        month, day, year = int(date.split('/')[0]), int(date.split('/')[1]), int(date.split('/')[2])
        hour, minute, second = int(time.split(':')[0]), int(time.split(':')[1]), int(time.split(':')[2])

        scheduled_date = datetime(year, month, day, hour, minute, second)
        if scheduled_date < datetime.now():
            print("Nay")
            error = 'Select an appopriate time'
            return render_template('calendar.html', logged_in=current_user.is_authenticated, error=error)
        else:
            print("Yay")
            return redirect(url_for('reserve', location_id=location_id, check_in_time=[year, month, day, hour, minute, second]))
    return render_template('calendar.html', logged_in=current_user.is_authenticated)


@app.route('/reserve/<int:location_id>', methods=['GET','POST'])
def reserve(location_id):
    error = None
    year, month, day, hour, minute, second = request.args.getlist('check_in_time')
    check_in_time = None

    if request.method == 'GET':
        spots_in_location = ParkingSpot.select().where(ParkingSpot.business_id == location_id)

        # Stores the OPEN PARKING SPOTS IDS
        open_spots_ids = [spot.id for spot in spots_in_location if spot.type == 'Open']

        try:
            # Reserves the first parking spot said to be OPEN
            q = ParkingSpot.update(type='Reserved').where(ParkingSpot.id == open_spots_ids[0])
            q.execute()

            # Inserting timestamp of when user booked spot
            check_in_time = int(datetime.timestamp((datetime(int(year), int(month), int(day), int(hour), int(minute), int(second)))))
            # check_in_time = int(datetime.timestamp(datetime.now()))

            Receipt.insert(user=current_user.email, spot_id=open_spots_ids[0], time_in=check_in_time, status='Unpaid').execute()

        except IndexError:
            error = 'There are no spots left in selected area'
            locations = Location.select()
            return render_template('check-in.html', locations=locations, logged_in=current_user.is_authenticated, error=error)

    if (check_in_time - int(datetime.timestamp(datetime.now()))) <= 60:
        print(f"Check-in============={check_in_time}")
        global c_o_c_i
        c_o_c_i = check_in_time
        return redirect(url_for('check_out', check_in_time=check_in_time))
    else:
        return redirect(url_for('home', check_in_time=check_in_time, message='Reservation successful.'))
    # return redirect(url_for('home', check_in_time=check_in_time, message='Reservation successful.'))



@app.route('/cancel-reservation', methods=['GET', 'POST'])
def cancel_reservation():
    check_in_time = int(request.args.get('check_in_time'))
    try:
        spot_id = Receipt.select().where(Receipt.user == current_user.email, Receipt.time_in == check_in_time).get().spot_id

        # Deletes the receipt
        q = Receipt.delete().where(Receipt.user == current_user.email, Receipt.time_in == check_in_time)
        q.execute()

        # Updates the status of the spot to OPEN
        q = ParkingSpot.update(type='Open').where(ParkingSpot.id == spot_id)
        q.execute()
        return redirect(url_for('home', message='Cancel successful.'))
    except Receipt.DoesNotExist:
        return redirect(url_for('check_out', check_in_time=check_in_time))

@app.route('/check-out', methods=['GET', 'POST'])
def check_out():
    error = None
    cancel_booking = None

    print(f"ARGS========={request.args.get('check_in_time')}")
    if request.args.get('check_in_time') is None:
        print(f"Type========={type(c_o_c_i)}")
        print(f"Data========={c_o_c_i}")
        check_in_time = int(c_o_c_i)
    else:
        check_in_time = int(request.args.get('check_in_time'))

    if datetime.timestamp(datetime.now()) + 2 > check_in_time:
        cancel_booking = True


    reserved_spot_id = Receipt.select().where(Receipt.user == current_user.email, Receipt.time_in == check_in_time).get().spot_id
    reserved_spot_name = Location.select().where(Location.id == ParkingSpot.select().where(ParkingSpot.id == reserved_spot_id).get().business_id).get().name
    if request.method == 'POST':
        # Setting parameters
        email = request.form['email']
        check_in_time = int(c_o_c_i)
        try:
            # Reserves the first parking spot said to be OPEN
            check_out_time = int(datetime.timestamp(datetime.now()))
            q = Receipt.update(time_out=check_out_time, status='Paid').where(Receipt.user == email, Receipt.time_in == check_in_time)
            q.execute()

            # Updates the status of the spot to OPEN
            spot_id = [spot.spot_id for spot in Receipt.select().where(Receipt.user == email, Receipt.time_in == check_in_time)][0]
            q = ParkingSpot.update(type='Open').where(ParkingSpot.id == spot_id)
            q.execute()

            # Does calculation of the price
            price = (check_out_time - check_in_time) * 20

            # Updates the PRICE on the DB
            q = Receipt.update(price=price).where(Receipt.time_in == check_in_time, Receipt.user == email)
            q.execute()

            id = f"{email}{check_out_time}"
            # Updates PRODUCT NAME IN RECEIPT DB
            q = Receipt.update(product_name=id).where(Receipt.user == email, Receipt.time_out == check_out_time)
            q.execute()

            print(price)
            try:
                stripe.Product.create(name=id, default_price_data={
                'currency': 'kes',
                'unit_amount_decimal': price * 100})

                # Cannot read data immediately after writing
                time.sleep(20)

                product_id = stripe.Product.search(query="name:'{}'".format(id))['data'][0]['id']

                price_id = stripe.Product.retrieve(product_id)['default_price']
                # price_id = stripe.Product.list(limit=3)['data'][0]['default_price']

                return redirect(url_for('payment', price_id=price_id))
            except Exception as e:
                return redirect(url_for('check_out', check_in_time=check_in_time))

        except Receipt.DoesNotExist:
            error = 'Receipt does not exist'
            return render_template("check-out.html", error=error,  logged_in=current_user.is_authenticated, spot_id=reserved_spot_id, spot_name=reserved_spot_name, check_in_time=check_in_time, formatted_check_in_time=datetime.fromtimestamp(check_in_time))
    print(f"Trueee====={cancel_booking}")
    return render_template('check-out.html', logged_in=current_user.is_authenticated, spot_id=reserved_spot_id, spot_name=reserved_spot_name, cancel_booking_permission=cancel_booking, check_in_time=check_in_time, formatted_check_in_time=datetime.fromtimestamp(check_in_time))

#------------------------------------------------------------------------------#

# @app.route('/payment/<int:price>')
# def payment(price):
#     return render_template('checkout-form.html', price=price)


#----------------------------------- STRIPE -----------------------------------#
YOUR_DOMAIN = 'http://127.0.0.1:5000'

@app.route('/payment/<price_id>', methods=['GET','POST'])
def payment(price_id):
    line_items = [{
        'price': price_id,
        'quantity': 1,
        }]
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=line_items,
            mode='payment',
            success_url=YOUR_DOMAIN + '/success',
            cancel_url=YOUR_DOMAIN + '/cancel',
        )
    except Exception as e:
        return str(e)
    return redirect(checkout_session.url, code=303)

#------------------------------------------------------------------------------#


#----------------------------- SUCCESS | CANCEL ==-----------------------------#
@app.route("/success", methods=['GET', 'POST'])
def success():
    return render_template('success.html')


@app.route("/cancel", methods=['GET', 'POST'])
def cancel():
    return render_template('cancel.html')

#------------------------------------------------------------------------------#


#------------------------------ MANAGE LOCATIONS ----------------------------------#
@app.route('/dashboard/add-location', methods=['GET','POST'])
def add_location():
    if request.method == 'POST':
        # Location.insert(name=request.args.get('location')).execute()
        Location.insert(name=request.form['location'].upper()).execute()

        location_id = Location.select().where(Location.name == request.form['location'].upper()).get()
        for i in range(int(request.form['spots'])):
            ParkingSpot.insert(type='Open', business_id=location_id).execute()

        return redirect(url_for('dashboard'))
    return redirect(url_for('dashboard'))


@app.route('/dashboard/delete-location/<int:id>')
def delete_location(id):
    if Location.get(Location.id == id):
        query = Location.get(Location.id == id)
        query.delete_instance()

        query = ParkingSpot.delete().where(ParkingSpot.business_id == id)
        query.execute()
    return redirect(url_for('dashboard'))
#------------------------------------------------------------------------------#

#------------------------------ MANAGE USERS ----------------------------------#
@app.route('/dashboard/delete-user/<int:id>')
def delete_user(id):
    if User.get(User.id == id):
        query = User.get(User.id == id)
        query.delete_instance()
    return redirect(url_for('dashboard'))
#------------------------------------------------------------------------------#



#-------------------------------- SIGN OUT ------------------------------------#
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

#------------------------------------------------------------------------------#

#-------------------------------- FEEDBACK ------------------------------------#

@app.route("/post_feedback", methods=['GET'])
def post_feedback():
    # Inserting data
    Feedback.insert(fname=current_user.fname, comment=request.args.get('comment')).execute()
    return redirect(url_for('check_in'))

#------------------------------------------------------------------------------#

#---------------------------- CHANGE PASSWORD ---------------------------------#

@app.route("/recover-password", methods=['GET','POST'])
def recover_password():
    error = None
    if request.method == 'POST':
        # Check for existence of the user
        try:
            if User.get(User.email == request.form['email']):
                return redirect(url_for('change_password', email=request.form['email']))
        except:
            error = 'User does not exist'
            return redirect(url_for('recover_password', error=error))
    return render_template('recover-password.html')


@app.route("/change-password/<email>", methods=['GET','POST'])
def change_password(email):
    if request.method == 'POST':
        if request.form['password_confirm'] == request.form['password']:
            # Salting password
            password_hashed = generate_password_hash(password=request.form['password'], method="pbkdf2:sha256", salt_length=8)

            # Updating password
            q = User.update(password=password_hashed).where(User.email == email)
            q.execute()
            return redirect(url_for('login'))
        else:
            return redirect(url_for('recover_password'))
    return render_template('change-password.html')

#------------------------------------------------------------------------------#




if __name__ == '__main__':
    app.run(debug=True)
