from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId

app = Flask(__name__)
app.config['SECRET_KEY'] = '12333'  # Replace with your actual secret key
app.config['MONGO_URI'] = 'mongodb://localhost:27017/db'  # MongoDB connection URI

mongo = PyMongo(app)

# Routes

# Routes

# Sign in
@app.route('/', methods=['GET', 'POST'])
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
@app.route('/homepage')
def homepage():
    # Check if the user is logged in
    if 'user_id' not in session:
        flash('You need to log in to access the homepage.')
        return redirect(url_for('login'))

    ngos = mongo.db.ngos.find()  # Fetch all NGOs
    return render_template('homepage.html', ngos=ngos)


# Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fullname = request.form['fullname']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        # Check if the email or username already exists in the database
        existing_user_email = mongo.db.users.find_one({'email': email})
        existing_user_username = mongo.db.users.find_one({'username': username})

        if existing_user_email:
            flash('Email already registered. Please use a different email or log in.')
            return redirect(url_for('register'))

        if existing_user_username:
            flash('Username already taken. Please choose a different username.')
            return redirect(url_for('register'))

        # Insert the new user in the database
        mongo.db.users.insert_one({'fullname': fullname, 'email': email, 'username': username, 'password': hashed_password})
        flash('Registered successfully! Please login.')
        return redirect(url_for('login'))

    return render_template('register.html')


# Donation page
@app.route('/donate')
def donate():
    # Check if the user is logged in
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
    return redirect(url_for('login'))

# Contact page

# Route to display the contact form and handle form submission
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Retrieve form data
        name = request.form['name']
        email = request.form['email']
        mobile = request.form['mobile']
        message = request.form['message']

        # Insert data into MongoDB 'contacts' collection
        contact_data = {
            'name': name,
            'email': email,
            'mobile': mobile,
            'message': message
        }

        # Insert data into MongoDB using Flask-PyMongo
        mongo.db.contacts.insert_one(contact_data)

        # Flash a success message and redirect to a thank-you page
        flash('Thank you for contacting us! We will get back to you soon.')
        return redirect(url_for('thank_you'))

    # Render the contact form if it's a GET request
    return render_template('contact.html')

# Thank you page after form submission
@app.route('/thank_you')
def thank_you():
    return render_template('thank_you.html')

# About page
@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)
