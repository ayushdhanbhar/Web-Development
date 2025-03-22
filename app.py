from flask import Flask, jsonify, render_template, redirect, url_for, flash, request, session
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from pymongo import MongoClient
import smtplib
from email.message import EmailMessage

app = Flask(__name__)
app.config['SECRET_KEY'] = '12333'  # Replace with your actual secret key
app.config['MONGO_URI'] = "mongodb+srv://vedant:vedant@cluster0.1fi6w.mongodb.net/db"  # MongoDB connection URI

client = MongoClient("mongodb+srv://vedant:vedant@cluster0.1fi6w.mongodb.net/db")
db = client['db']  # Replace with your database name
users_collection = db['users']  # Replace with your collection name

mongo = PyMongo(app)

# Routes

# Send Email Function
def send_email(user_email, user_name):
    
    sender_email = 'satkarmafoundation101@gmail.com'  # Replace with your email
    sender_password = 'mltj nriw ltsn sxvg'    # Replace with your email password
    subject = 'Welcome to Satkarma NGO'
    
    # Create the email content
    message_content = f"""
    Hello {user_name},
    
    Thank you for signing up for Satkarma Team !
    
    We are thrilled to have you as part of our community. By joining us, you are making a positive impact in the world. Together, we can work towards making a difference in the lives of many. We appreciate your support and look forward to your active participation.
    
    If you have any questions or need more information, feel free to reach out.
    
    Best regards,
    The Satkarma Team
    """
    
    msg = EmailMessage()
    msg.set_content(message_content)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = user_email
    
    # Sending the email
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:  # Gmail SMTP server
            server.login(sender_email, sender_password)
            server.send_message(msg)
        print(f"Email sent to {user_email}")
    except Exception as e:
        print(f"Failed to send email to {user_email}: {str(e)}")

# Sign in
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = mongo.db.users.find_one({'email': email})
        
        if user and check_password_hash(user['password'], password):
            # Login user by storing user id in session
            session['user_id'] = str(user['_id'])
            flash('Logged in successfully!')
            return redirect(url_for('homepage'))
        else:
            error_message = 'Invalid email or password.'
            return render_template('sign.html', error_message=error_message)

    return render_template('sign.html')

# Homepage - Displays NGO search
@app.route('/', methods=['GET', 'POST'])
def homepage():
    ngos = mongo.db.ngos.find()  # Fetch all NGOs
    return render_template('homepage.html', ngos=ngos)



# Register Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fullname = request.form['fullname']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        # Check if the email or username already exists in the database
        existing_user_email = users_collection.find_one({'email': email})
        existing_user_username = users_collection.find_one({'username': username})

        if existing_user_email:
            flash('Email already registered. Please use a different email or log in.')
            return redirect(url_for('register'))

        if existing_user_username:
            flash('Username already taken. Please choose a different username.')
            return redirect(url_for('register'))

        # Insert the new user in the database
        users_collection.insert_one({
            'fullname': fullname,
            'email': email,
            'username': username,
            'password': hashed_password
        })
        
        # Send welcome email after successful registration
        send_email(email, username)

        flash('Registered successfully! Please log in.')
        return redirect(url_for('login'))

    return render_template('register.html')

# Donation page
@app.route('/donate')
def donate():
    if 'user_id' not in session:
        flash('You need to log in to donate.')
        return redirect(url_for('login'))
    return render_template('donate.html')

# Logout
@app.route('/logout')
def logout():
    # Clear the user session
    session.pop('user_id', None)
    flash('Logged out successfully.')

    # Redirect to the homepage after logout
    return redirect(url_for('homepage'))

# Contact page
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        mobile = request.form['mobile']
        message = request.form['message']

        contact_data = {
            'name': name,
            'email': email,
            'mobile': mobile,
            'message': message
        }

        mongo.db.contacts.insert_one(contact_data)

        flash('Thank you for contacting us! We will get back to you soon.')
        return redirect(url_for('thank_you'))

    return render_template('contact.html')

# Thank you page after form submission
@app.route('/thank_you')
def thank_you():
    return render_template('thank_you.html')

# About page
@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/NGOS')
def ngos():
    # Fetch NGOs from the database
    ngos = list(mongo.db.ngos.find())
    return render_template('NGOS.html', ngos=ngos)


# Individual NGO details page
@app.route('/ngo/<ngo_id>')
def ngo_details(ngo_id):
    ngo = mongo.db.ngos.find_one({'_id': ObjectId(ngo_id)})
    if ngo:
        return render_template('ngo_details.html', ngo=ngo)
    else:
        flash('NGO not found.')
        return redirect(url_for('ngos'))

@app.route('/transaction')
def transaction():
    if 'user_id' not in session:
        flash('Please login to make a donation.')
        return redirect(url_for('login'))

    user = mongo.db.users.find_one({'_id': ObjectId(session['user_id'])})
    ngos = list(mongo.db.ngos.find())
    
    return render_template('transaction.html', ngos=ngos, user=user)

from flask_mail import Mail, Message

# Flask-Mail Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'satkarmafoundation101@gmail.com'  # Your Gmail ID
app.config['MAIL_PASSWORD'] = 'kloh mapp tuwv oqys'  # Your Gmail app password
app.config['MAIL_DEFAULT_SENDER'] = 'satkarmafoundation101@gmail.com'

mail = Mail(app)

@app.route('/process_payment', methods=['POST'])
def process_payment():
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'User not authenticated'})

    data = request.json
    ngo_id = data.get('ngo_id')
    amount = data.get('amount')

    if not ngo_id or not amount:
        return jsonify({'status': 'error', 'message': 'Invalid data'})

    user_id = session['user_id']

    # Fetch user details from MongoDB
    user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'})

    email = user['email']
    user_name = user['fullname']

    # Store payment data in MongoDB
    payment_data = {
        'user_id': ObjectId(user_id),
        'ngo_id': ObjectId(ngo_id),
        'amount': amount,
        'status': 'success'  # Fake payment status
    }

    db.payments.insert_one(payment_data)

    # Send Thank You Email to the User
    subject = "Thank You for Your Donation - SatKarma"
    message_body = f"""
    Dear {user_name},

    Thank you for your generous donation of ₹{amount} to support the NGO. Your support means a lot to us.

    We truly appreciate your contribution to help those in need.

    Regards,
    SatKarma Team
    """

    msg = Message(subject, recipients=[email], body=message_body)
    mail.send(msg)

    return jsonify({'status': 'success'})

# @app.route('/yup')
# def yup():
#     return render_template('yup.html')

if __name__ == '__main__':
    app.run(debug=True)
