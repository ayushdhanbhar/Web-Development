import datetime
from flask import Flask, jsonify, render_template, redirect, url_for, flash, request, session
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
import razorpay

app = Flask(__name__)
app.config['SECRET_KEY'] = '12333'  # Replace with your actual secret key
app.config['MONGO_URI'] = "mongodb+srv://vedant:vedant@cluster0.1fi6w.mongodb.net/db"  # MongoDB connection URI
razorpay_client = razorpay.Client(auth=("YOUR_KEY_ID", "YOUR_KEY_SECRET"))

mongo = PyMongo(app)

# Routes

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

# Add this to your existing code where you set up the database
def setup_sample_ngos():
    # Check if NGOs already exist
    if mongo.db.ngos.count_documents({}) == 0:
        sample_ngos = [
            {
                'name': 'Green Earth Foundation',
                'description': 'Working towards environmental conservation and sustainable practices.',
                'causes': ['Environment', 'Sustainability'],
                'location': 'Mumbai, India',
                'contact': 'contact@greenearthfoundation.org'
            },
            {
                'name': 'Happy Children Initiative',
                'description': 'Providing education and support to underprivileged children.',
                'causes': ['Education', 'Child Welfare'],
                'location': 'Delhi, India',
                'contact': 'info@happychildren.org'
            },
            {
                'name': 'Elder Care Society',
                'description': 'Supporting and caring for elderly individuals in need.',
                'causes': ['Elder Care', 'Healthcare'],
                'location': 'Pune, India',
                'contact': 'help@eldercaresociety.org'
            }
        ]
        mongo.db.ngos.insert_many(sample_ngos)




@app.route('/transaction')
def transaction():
    if 'user_id' not in session:
        flash('Please login to make a donation.')
        return redirect(url_for('login'))
    
    user = mongo.db.users.find_one({'_id': ObjectId(session['user_id'])})
    ngos = list(mongo.db.ngos.find())
    return render_template('transaction.html', ngos=ngos, user=user, razorpay_key_id="YOUR_KEY_ID")

# Create Razorpay order
@app.route('/create_order', methods=['POST'])
def create_order():
    if 'user_id' not in session:
        return jsonify({'error': 'User not logged in'}), 401

    data = request.json
    amount = data.get('amount', 0) * 100  # Amount in paise
    
    order_data = {
        'amount': amount,
        'currency': 'INR',
        'receipt': f'order_{ObjectId()}'
    }
    
    try:
        order = razorpay_client.order.create(data=order_data)
        
        # Store order details in database
        transaction_data = {
            'user_id': ObjectId(session['user_id']),
            'ngo_id': ObjectId(data['ngo_id']),
            'amount': amount / 100,  # Store in rupees
            'message': data.get('message', ''),
            'order_id': order['id'],
            'status': 'pending',
            'created_at': datetime.utcnow()
        }
        mongo.db.transactions.insert_one(transaction_data)
        
        return jsonify({'order_id': order['id']})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Verify payment
@app.route('/verify_payment', methods=['POST'])
def verify_payment():
    if 'user_id' not in session:
        return jsonify({'error': 'User not logged in'}), 401

    data = request.json
    
    try:
        # Verify signature
        params_dict = {
            'razorpay_payment_id': data['razorpay_payment_id'],
            'razorpay_order_id': data['razorpay_order_id'],
            'razorpay_signature': data['razorpay_signature']
        }
        razorpay_client.utility.verify_payment_signature(params_dict)
        
        # Update transaction status
        mongo.db.transactions.update_one(
            {'order_id': data['razorpay_order_id']},
            {'$set': {
                'status': 'completed',
                'payment_id': data['razorpay_payment_id'],
                'completed_at': datetime.utcnow()
            }}
        )
        
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500



# NGO details page
@app.route('/ngo1')
def ngo1():
    return render_template('ngo1.html')


if __name__ == '__main__':
    setup_sample_ngos()
    app.run(debug=True)
