from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify
from functools import wraps
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import your existing backend services
from user.db import init_db
from user.repositories.sqllite_user_repo import SQLiteUserRepository
from user.services.RegistrationService import RegistrationService
from user.services.AuthenticationSer import AuthenticationService

# Import account services
from account.account_service import AccountService
from account.exceptions import AccountNotFoundError, InsufficientFundsError, InactiveAccountError

# Import database connection helper
from database.db_helper import get_db_connection, close_db_connection

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = 'your_secret_key_here'  # Change this to a random secret key

# Initialize database and services
print("Initializing database...")
init_db()

# Use the same database path that your Flask app expects
db_path = 'C:\\Users\\Taizya Yambayamba\\Desktop\\Programming works\\Penny\\database\\penny.db'
repo = SQLiteUserRepository(db_path)
reg_service = RegistrationService(repo)
auth_service = AuthenticationService(repo)
account_service = AccountService()
print("Services initialized successfully!")

# Add teardown app context to close database connections
@app.teardown_appcontext
def teardown_db(exception):
    close_db_connection()

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Use get() method with default to avoid KeyError
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        # Check if fields are empty
        if not username or not password:
            flash('Please fill in all fields.')
            return render_template('login.html')
        
        print(f"Login attempt: username={username}")  # Debug log
        
        try:
            # Check if the authentication service has the required method
            if not hasattr(auth_service, 'login_with_username'):
                flash('Authentication system error. Please contact support.')
                print("ERROR: auth_service.login_with_username method not found!")
                return render_template('login.html')
            
            # Use the new login_with_username method
            user_id = auth_service.login_with_username(username, password)
            
            if user_id:
                session['user_id'] = user_id
                session['username'] = username
                
                # Try to get the user's full name if available
                try:
                    user = repo.get_user_by_id(user_id)
                    session['full_name'] = user.get('full_name', username)
                except Exception as e:
                    print(f"Error getting user details: {e}")
                    session['full_name'] = username
                    
                flash(f'Welcome back, {session["full_name"]}!')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid username or password.')
                
        except ValueError as e:
            error_msg = str(e)
            print(f"Login ValueError: {error_msg}")
            
            # Provide user-friendly error messages
            if "not found" in error_msg.lower():
                flash('Account not found. Please check your username or sign up.')
            elif "invalid password" in error_msg.lower():
                flash('Invalid password. Please try again.')
            else:
                flash(f'Login failed: {error_msg}')
                
        except AttributeError as e:
            flash('Authentication system error. Please contact support.')
            print(f"Method error: {e}")
        except Exception as e:
            flash('An error occurred during login. Please try again.')
            print(f"Unexpected login error: {e}")
            print(f"Error type: {type(e)}")
    
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Get form data
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password']
        confirm_password = request.form.get('confirm_password', '')
        role = 'customer'  # Default to customer since your form doesn't have role selection
        
        print(f"Signup attempt: username={username}, email={email}")  # Debug log
        
        # Basic validation
        if confirm_password and password != confirm_password:
            flash('Passwords do not match.')
            return render_template('signup.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long.')
            return render_template('signup.html')
        
        if len(username) < 3:
            flash('Username must be at least 3 characters long.')
            return render_template('signup.html')
        
        # Email validation
        if '@' not in email or '.' not in email:
            flash('Please enter a valid email address.')
            return render_template('signup.html')
        
        try:
            # Use your existing registration service
            print(f"Calling registration service...")  # Debug log
            message = reg_service.register(username, email, password, role)
            print(f"Registration successful: {message}")  # Debug log
            flash('Account created successfully! Please log in.')
            return redirect(url_for('login'))
            
        except ValueError as e:
            error_msg = str(e)
            print(f"Registration ValueError: {error_msg}")  # Debug log
            flash(f'Registration failed: {error_msg}')
            return render_template('signup.html')
        except Exception as e:
            print(f"Registration Exception: {str(e)}")  # Debug log
            print(f"Exception type: {type(e)}")  # Debug log
            flash('Error creating account. Please try again.')
            return render_template('signup.html')
    
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session.get('user_id')
    
    try:
        # Get user's accounts and total balance
        user_accounts = account_service.get_accounts_by_user(user_id)
        total_balance = sum(account['balance'] for account in user_accounts)
    except Exception as e:
        print(f"Error fetching accounts for dashboard: {e}")
        user_accounts = []
        total_balance = 0
    
    return render_template('dashboard.html', 
                         current_user={'username': session.get('full_name', session.get('username', 'User'))},
                         accounts=user_accounts,
                         total_balance=total_balance)


@app.route('/accounts')
@login_required
def accounts():
    user_id = session.get('user_id')
    
    try:
        # Get user's accounts
        user_accounts = account_service.get_accounts_by_user(user_id)
        
        # Calculate total balance
        total_balance = sum(account['balance'] for account in user_accounts)
        
        # Get recent transactions (from all accounts)
        recent_transactions = []
        for account in user_accounts:
            transactions = account_service.get_transaction_history(account['account_id'])
            for transaction in transactions:
                recent_transactions.append({
                    'account_id': account['account_id'],
                    'account_type': account['account_type'],
                    'transaction_type': transaction[0],
                    'amount': transaction[1],
                    'timestamp': transaction[2]
                })
        
        # Sort transactions by timestamp (newest first) and take top 5
        recent_transactions.sort(key=lambda x: x['timestamp'], reverse=True)
        recent_transactions = recent_transactions[:5]
        
    except Exception as e:
        print(f"Error fetching accounts: {e}")
        user_accounts = []
        total_balance = 0
        recent_transactions = []
    
    return render_template('accounts.html', 
                         current_user={'username': session.get('full_name', session.get('username', 'User'))},
                         accounts=user_accounts,
                         total_balance=total_balance,
                         recent_transactions=recent_transactions)

@app.route('/accounts/create', methods=['POST'])
@login_required
def create_account():
    user_id = session.get('user_id')
    account_type = request.form.get('account_type')
    
    if not account_type or account_type not in ['Savings', 'Checking']:
        flash('Please select a valid account type.')
        return redirect(url_for('accounts'))
    
    try:
        account = account_service.create_account(user_id, account_type)
        flash(f'{account_type} account created successfully!')
    except Exception as e:
        flash(f'Error creating account: {str(e)}')
    
    return redirect(url_for('accounts'))

@app.route('/accounts/deposit', methods=['POST'])
@login_required
def deposit():
    user_id = session.get('user_id')
    account_id = request.form.get('account_id')
    amount = float(request.form.get('amount', 0))
    
    if amount <= 0:
        flash('Please enter a valid amount.')
        return redirect(url_for('accounts'))
    
    try:
        new_balance = account_service.deposit(user_id, account_id, amount)
        flash(f'Deposited ZMW {amount:.2f} successfully. New balance: ZMW {new_balance:.2f}')
    except (AccountNotFoundError, InactiveAccountError, PermissionError) as e:
        flash(str(e))
    except Exception as e:
        flash(f'Error processing deposit: {str(e)}')
    
    return redirect(url_for('accounts'))

@app.route('/accounts/withdraw', methods=['POST'])
@login_required
def withdraw():
    user_id = session.get('user_id')
    account_id = request.form.get('account_id')
    amount = float(request.form.get('amount', 0))
    
    if amount <= 0:
        flash('Please enter a valid amount.')
        return redirect(url_for('accounts'))
    
    try:
        new_balance = account_service.withdraw(user_id, account_id, amount)
        flash(f'Withdrew ZMW {amount:.2f} successfully. New balance: ZMW {new_balance:.2f}')
    except (AccountNotFoundError, InactiveAccountError, InsufficientFundsError, PermissionError) as e:
        flash(str(e))
    except Exception as e:
        flash(f'Error processing withdrawal: {str(e)}')
    
    return redirect(url_for('accounts'))

@app.route('/accounts/transfer', methods=['POST'])
@login_required
def transfer():
    user_id = session.get('user_id')
    from_account_id = request.form.get('from_account_id')
    to_account_id = request.form.get('to_account_id')
    amount = float(request.form.get('amount', 0))
    
    if amount <= 0:
        flash('Please enter a valid amount.')
        return redirect(url_for('accounts'))
    
    if from_account_id == to_account_id:
        flash('Cannot transfer to the same account.')
        return redirect(url_for('accounts'))
    
    try:
        from_balance, to_balance = account_service.transfer_funds(user_id, from_account_id, to_account_id, amount)
        flash(f'Transferred ZMW {amount:.2f} successfully. New balances: From: ZMW {from_balance:.2f}, To: ZMW {to_balance:.2f}')
    except (AccountNotFoundError, InactiveAccountError, InsufficientFundsError, PermissionError) as e:
        flash(str(e))
    except Exception as e:
        flash(f'Error processing transfer: {str(e)}')
    
    return redirect(url_for('accounts'))

@app.route('/accounts/transactions/<account_id>')
@login_required
def get_transactions(account_id):
    user_id = session.get('user_id')
    
    try:
        # Verify the account belongs to the user
        account = account_service._get_account(account_id)
        if account['user_id'] != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        transactions = account_service.get_transaction_history(account_id)
        return jsonify(transactions)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@app.route('/loans')
@login_required
def loans():
    return render_template('loans.html', 
                         current_user={'username': session.get('full_name', session.get('username', 'User'))})

@app.route('/plans')
@login_required
def plans():
    return render_template('plans.html', 
                         current_user={'username': session.get('full_name', session.get('username', 'User'))})

@app.route('/penny')
@login_required
def penny():
    return render_template('penny.html', 
                         current_user={'username': session.get('full_name', session.get('username', 'User'))})

if __name__ == '__main__':
    print("Starting Flask application...")
    app.run(debug=True)