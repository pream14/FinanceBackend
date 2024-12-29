from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime, timedelta  # Use this for datetime functionality
from sqlalchemy import func

from decimal import Decimal




from werkzeug.security import generate_password_hash, check_password_hash  # Import from werkzeug
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will allow all domains to access your Flask app
app.config['JWT_SECRET_KEY'] = "starz"
app.config['JWT_ACCESS_TOKEN_EXPIRES'] =timedelta(days=365)



# Initialize the Flask application

# Configure the MySQL database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:starz@localhost/finance'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# Initialize the SQLAlchemy object
db = SQLAlchemy(app)
jwt = JWTManager(app)

# Define the Users table model
class User(db.Model):
    __tablename__ = 'Users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())  # Add this field


    def __init__(self,user_id, username, password, role):
        self.user_id=user_id
        self.username = username
        self.password = password
        self.role = role


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user_id = data.get('user_id')  # Accept user_id instead of username
    password = data.get('password')

    if not user_id or not password:
        return jsonify({'error': 'User ID and password are required'}), 400

    # Fetch user from DB based on user_id
    user = User.query.filter_by(user_id=user_id).first()

    if user and check_password_hash(user.password, password):
        # Create JWT token that expires in 1 hour
        access_token = create_access_token(
            identity=user.user_id
        )
        return jsonify({'access_token': access_token,'username': user.username, 'role': user.role}), 200
    else:
        return jsonify({'error': 'Invalid user ID or password'}), 401
# Route to create a new Owner
@app.route('/create_owner', methods=['POST'])
def create_owner():
    # Get data from the POST request
    username = request.json.get('username')
    password = request.json.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    # Hash the password using werkzeug's generate_password_hash
    hashed_password = generate_password_hash(password)

    # Create a new owner
    new_owner = User(username=username, password=hashed_password, role='Owner')

    # Add the new owner to the database
    try:
        db.session.add(new_owner)
        db.session.commit()
        return jsonify({"message": "Owner created successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# Route to get all users with role 'Owner'
@app.route('/get_owners', methods=['GET'])
def get_owners():
    owners = User.query.filter_by(role='Owner').all()
    owners_list = [{"user_id": owner.user_id, "username": owner.username, "role": owner.role} for owner in owners]
    return jsonify(owners_list), 200


# Define the Customers table model
class Customer(db.Model):
    __tablename__ = 'Customers'
    name = db.Column(db.String(100), nullable=False)
    contact_number = db.Column(db.String(15), primary_key=True, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    loan_amount = db.Column(db.Numeric(10, 2), nullable=False)
    repayment_type = db.Column(db.String(10), nullable=False)
    balance = db.Column(db.Numeric(10, 2), nullable=False, default=0)  # Balance column


    def __init__(self, name, contact_number, loan_amount, repayment_type, location):
        self.name = name
        self.contact_number = contact_number
        self.loan_amount = loan_amount
        self.repayment_type = repayment_type
        self.location = location

# Route to create a new Customer
@app.route('/create_customer', methods=['POST'])
def create_customer():
    # Get data from the POST request
    name = request.json.get('name')
    contact_number = request.json.get('contact_number')
    loan_amount = request.json.get('loan_amount')
    repayment_type = request.json.get('repayment_type')
    location = request.json.get('location')
    balance=request.json.get('loan_amount')

    if not name or not contact_number or not loan_amount or not repayment_type or not location:
        return jsonify({"error": "All fields are required"}), 400

    # Create a new customer
    new_customer = Customer(name=name, contact_number=contact_number, loan_amount=loan_amount,
                            repayment_type=repayment_type, location=location)

    # Add the new customer to the database
    try:
        db.session.add(new_customer)
        db.session.commit()
        return jsonify({"message": "Customer created successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# Route to create a new Worker
@app.route('/create_worker', methods=['POST'])
def create_worker():
    # Get data from the POST request
    user_id=request.json.get('user_id')
    username = request.json.get('username')
    password = request.json.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    # Hash the password using werkzeug's generate_password_hash
    hashed_password = generate_password_hash(password)

    # Create a new worker with 'Worker' role
    new_worker = User(user_id=user_id,username=username, password=hashed_password, role='Worker')

    # Add the new worker to the database
    try:
        db.session.add(new_worker)
        db.session.commit()
        return jsonify({"message": "Worker created successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# Route to get all customers
@app.route('/get_customers', methods=['GET'])
def get_customers():
    customers = Customer.query.all()
    customers_list = [{"name": customer.name,
                        "contact_number": customer.contact_number, "loan_amount": str(customer.loan_amount),
                        "repayment_type": customer.repayment_type, "location": customer.location} for customer in customers]
    return jsonify(customers_list), 200

# Route to get all workers
@app.route('/get_workers', methods=['GET'])
def get_workers():
    workers = User.query.filter_by(role='Worker').all()
    workers_list = [{"user_id": worker.user_id, "username": worker.username, "role": worker.role,"date":worker.created_at} for worker in workers]
    return jsonify(workers_list), 200

@app.route('/get_customers_by_location', methods=['GET'])
def get_customers_by_location():
    # Get the location from the query parameters
    location = request.json.get('location')

    if not location:
        return jsonify({"error": "Location parameter is required"}), 400

    # Query the database to get customers for the specified location
    customers = Customer.query.filter_by(location=location).all()
    if not customers:
        return jsonify({"message": f"No customers found in location: {location}"}), 404

    # Format the response data
    customers_list = [
        {
            
            "name": customer.name,
            "contact_number": customer.contact_number,
            "loan_amount": str(customer.loan_amount),
            "repayment_type": customer.repayment_type,
            "location": customer.location
        }
        for customer in customers
    ]

    return jsonify(customers_list), 200



@app.route('/get_all_locations', methods=['GET'])
def get_all_locations():
    try:
        # Query to get distinct locations from the Customers table
        locations = db.session.query(Customer.location).distinct().all()
        
        # Flatten the result and format as a list
        locations_list = [location[0] for location in locations]
        
        return jsonify({"locations": locations_list}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


class Payment(db.Model):
    __tablename__ = 'Payments'
    payment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_id = db.Column(db.String(15), db.ForeignKey('Customers.contact_number'), nullable=False)
    worker_id = db.Column(db.Integer, nullable=False)
    payment_date = db.Column(db.Date, nullable=False, default=date.today)
    amount_paid = db.Column(db.Integer, nullable=False)
    payment_status = db.Column(db.Enum('Paid', 'Unpaid'), nullable=False)

from decimal import Decimal

@app.route('/update_payment', methods=['POST'])
@jwt_required()
def update_payment():
    try:
        # Extract worker ID from the token
        worker_id = get_jwt_identity()
        data = request.json

        if not isinstance(data, list):  # Ensure data is a list
            return jsonify({"error": "Invalid data format. Expected a list of payment records."}), 400

        for payment in data:
            if not isinstance(payment, dict):
                return jsonify({"error": "Each payment record must be a dictionary"}), 400

            customer_id = payment.get('customer_id')
            payment_date = payment.get('payment_date', str(date.today()))
            amount_paid = payment.get('amount_paid', 0)
            previous_amount = payment.get('previous_amount', 0)

            # Convert to Decimal for arithmetic operations
            try:
                amount_paid = Decimal(amount_paid)
                previous_amount = Decimal(previous_amount)
            except (ValueError, TypeError):
                return jsonify({"error": "amount_paid and previous_amount must be numeric values"}), 400

            payment_status = payment.get('payment_status', 'Unpaid' if amount_paid == 0 else 'Paid')
            payment_type = payment.get('payment_type', 'Payment')  # Default to 'Payment'

            if not customer_id:
                return jsonify({"error": "Missing required fields in one or more payment records"}), 400

            # Check if the customer exists
            customer = Customer.query.filter_by(contact_number=customer_id).first()
            if not customer:
                return jsonify({"error": f"Customer with ID {customer_id} not found"}), 404

            # Ensure customer.balance is a Decimal
            if not isinstance(customer.balance, Decimal):
                customer.balance = Decimal(customer.balance)

            # Update or create payment
            existing_payment = Payment.query.filter_by(customer_id=customer_id, payment_date=payment_date).first()
            if existing_payment:
                if payment_type == 'Addition':
                    customer.balance -= amount_paid
                    existing_payment.amount_paid += amount_paid
                elif payment_type == 'Payment':
                    if previous_amount is None:
                        return jsonify({"error": "Missing previous amount for correction"}), 400
                    if amount_paid > previous_amount:
                        customer.balance -= (amount_paid - previous_amount)
                        existing_payment.amount_paid = amount_paid  # Update amount
                    else:
                        customer.balance += (previous_amount - amount_paid)
                        existing_payment.amount_paid = amount_paid  # Update amount
                existing_payment.payment_status =payment_status 

            else:
                customer.balance -= amount_paid
                new_payment = Payment(
                    customer_id=customer_id,
                    worker_id=worker_id,  # Use worker ID from the token
                    payment_date=payment_date,
                    amount_paid=amount_paid,
                    payment_status=payment_status
                )
                db.session.add(new_payment)

        db.session.commit()
        return jsonify({"message": "Payment records successfully processed"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    
@app.route('/get_customers_payment_status', methods=['GET'])
def get_customers_payment_status():
    try:
        # Get the status filter and date from query parameters
        data = request.json
        payment_status = data.get('payment_status')  # "Paid" or "Unpaid"
        payment_date = data.get('payment_date', str(date.today()))  # Expected format: "YYYY-MM-DD"

        if not payment_status:
            return jsonify({"error": "Payment status parameter (Paid/Unpaid) is required"}), 400

        if not payment_date:
            return jsonify({"error": "Payment date parameter is required"}), 400

        # Ensure the payment status matches the expected case-insensitive values
        payment_status = payment_status.lower()

        if payment_status == "paid":
            # Query to find customers with payments marked as "Paid" on the given date
            customers = (
                db.session.query(Customer)
                .join(Payment)
                .filter(Payment.payment_status == "Paid", Payment.payment_date == payment_date)
                .all()
            )
        elif payment_status == "unpaid":
            # Query to find customers with payments marked as "Unpaid" on the given date
            customers = (
                db.session.query(Customer)
                .join(Payment)
                .filter(Payment.payment_status == "Unpaid", Payment.payment_date == payment_date)
                .all()
            )
        else:
            return jsonify({"error": "Invalid payment status. Use 'Paid' or 'Unpaid'."}), 400

        if not customers:
            return jsonify(
                {"message": f"No customers found for payment status: {payment_status.capitalize()} on {payment_date}"}
            ), 404

        # Format the response
        customers_list = [
            {
                "customer_id": customer.contact_number,
                "name": customer.name,
                "contact_number": customer.contact_number,
                "location": customer.location,
                "loan_amount": str(customer.loan_amount),
                "repayment_type": customer.repayment_type,
            }
            for customer in customers
        ]

        return jsonify(customers_list), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route('/get_previous_amount', methods=['GET'])
@jwt_required()  # Ensure the user is authenticated
def get_previous_amount():
    try:
        # Extract worker ID from the token (if needed)
        worker_id = get_jwt_identity()
        
        # Get customer ID and date from query parameters (can be passed via URL or request body)
        customer_id = request.args.get('customer_id')  # Assuming customer_id is passed as a query parameter
        payment_date = request.args.get('payment_date')  # Optionally pass a specific date

        if not customer_id or not payment_date:
            return jsonify({"error": "Customer ID and payment date are required"}), 400

        # Query to find the last payment for this customer before or on the given date
        previous_payment = Payment.query.filter(
            Payment.customer_id == customer_id,
            Payment.payment_date <= payment_date  # Ensure it's before or on the requested date
        ).order_by(Payment.payment_date.desc()).first()  # Get the most recent payment

        if not previous_payment:
            return jsonify({"message": "No previous payment found for this customer on the specified date"}), 404

        # Return the previous amount (amount paid on the last payment)
        return jsonify({"previous_amount": previous_payment.amount_paid}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_payment_by_date', methods=['GET', 'POST'])
def get_payment_by_date():
    # Log request arguments
    print("Request args:", request.args)

    # Retrieve query parameters
    customer_id = request.args.get('customer_id')
    payment_date = request.args.get('payment_date',date)

    # Log received parameters
    print(f"Received customer_id: {customer_id}, payment_date: {payment_date}")

    if not customer_id or not payment_date:
        return jsonify({'error': 'Missing customer_id or payment_date'}), 400

    try:
        # Attempt to parse the payment_date into a proper datetime object
        payment_date = datetime.strptime(payment_date, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format, use YYYY-MM-DD'}), 400

    try:
        # Query the database to find payments for the specified customer and date
        payments = Payment.query.filter_by(customer_id=customer_id, payment_date=payment_date).all()

        if not payments:
            # If no payments are found, return a record with amount_paid = 0
            payment_data = [{
                'customer_id': customer_id,
                'worker_id': None,
                'payment_date': payment_date.strftime('%Y-%m-%d'),
                'amount_paid': '0',  # No payment found, so we set amount to 0
                'payment_status': 'Unpaid'
            }]
            return jsonify({'payments': payment_data}), 200

        # Format the payment data into a list of dictionaries
        payment_data = [
            {
                'customer_id': payment.customer_id,
                'worker_id': payment.worker_id,
                'payment_date': payment.payment_date.strftime('%Y-%m-%d'),
                'amount_paid': str(payment.amount_paid),  # Ensure it's a string for consistency in JSON response
                'payment_status': payment.payment_status
            }
            for payment in payments
        ]

        # Return the payment data as a JSON response
        return jsonify({'payments': payment_data}), 200

    except Exception as e:
        # In case of any other error, log the exception and return an error message
        print(f"Error occurred: {str(e)}")
        return jsonify({'error': 'An error occurred while processing the request'}), 500
@app.route('/get_entries_by_worker', methods=['GET'])
@jwt_required()
def get_entries_by_worker():
    try:
        worker_id = request.args.get('worker_id')  # Extract worker ID from the query parameter
        payment_date = request.args.get('payment_date', datetime.now().strftime('%Y-%m-%d'))

        # Base query
        query = db.session.query(
            Payment.customer_id,
            Payment.payment_date,
            Payment.payment_status,
            Customer.name.label("customer_name"),
            func.sum(Payment.amount_paid).label('total_amount_paid')  # Calculate total amount paid
        ).join(Customer, Payment.customer_id == Customer.contact_number) \
         .filter(Payment.payment_date == payment_date, Payment.payment_status == 'Paid') \
         .group_by(Payment.customer_id, Customer.name, Payment.payment_date, Payment.payment_status)

        # Apply worker_id filter only if it's provided
        if worker_id:
            query = query.filter(Payment.worker_id == worker_id)

        # Execute the query
        payments = query.all()

        # Calculate total sum of all amount_paid
        total_sum = sum(payment.total_amount_paid for payment in payments)

        # Format the data for the response
        payment_data = [
            {
                "customer_id": payment.customer_id,
                "customer_name": payment.customer_name,
                "amount_paid": payment.total_amount_paid,
                "payment_date": payment.payment_date.strftime('%Y-%m-%d'),
                "payment_status": payment.payment_status,
            }
            for payment in payments
        ]
        
        # Add the total sum of all payments
        return jsonify({
            "payments": payment_data,
            "total_amount_paid": total_sum  # Add the total amount paid
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/get_customer_payment_history', methods=['GET'])
@jwt_required()
def get_customer_payment_history():
    try:
        # Extract worker_id from the JWT token
        worker_id = get_jwt_identity()
        
        # Retrieve customer_id or customer_name from request arguments (optional)
        customer_id = request.args.get('customer_id')  # Optional
        customer_name = request.args.get('customer_name')  # Optional
        
        # Ensure that either customer_id or customer_name is provided
        if not customer_id and not customer_name:
            return jsonify({"error": "Either customer_id or customer_name must be provided"}), 400
        
        # Build the query to retrieve payment data
        query = db.session.query(
            Payment.customer_id,
            Payment.amount_paid,
            Payment.payment_date,
            Payment.payment_status,
            Customer.name.label("customer_name"),
            Customer.balance ,
            Customer.loan_amount ,
            # Join with Customer table to get customer name
        ).join(Customer, Payment.customer_id == Customer.contact_number)  # Assuming customer_id matches contact_number

        # Apply filters based on the provided customer_id or customer_name
        if customer_id:
            query = query.filter(Payment.customer_id == customer_id)
        
        if customer_name:
            query = query.filter(Customer.name.ilike(f'%{customer_name}%'))  # Case-insensitive matching for name

        # Filter by worker_id to only retrieve the payments entered by the current worker
        query = query.filter(Payment.worker_id == worker_id)
        
        # Execute the query and fetch the results
        payments = query.all()

        # Format the response data
        payment_data = [
            {
                "customer_id": payment.customer_id,
                "customer_name": payment.customer_name,
                "amount_paid": payment.amount_paid,
                "payment_date": payment.payment_date.strftime('%Y-%m-%d'),  # Date format
                "payment_status": payment.payment_status,
                "balance":payment.balance,
                "loan_amount":payment.loan_amount
            }
            for payment in payments
        ]
        
        return jsonify({"payments": payment_data}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500




if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0",port=5000)

