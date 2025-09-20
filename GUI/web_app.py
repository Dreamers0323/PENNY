from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify
from functools import wraps
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from datetime import datetime
import time

# Import your existing backend services
from user.db import init_db
from user.repositories.sqllite_user_repo import SQLiteUserRepository
from user.services.RegistrationService import RegistrationService
from user.services.AuthenticationSer import AuthenticationService

# Import account services
from account.account_service import AccountService
from account.exceptions import AccountNotFoundError, InsufficientFundsError, InactiveAccountError

# Add these imports at the top
from purchases.purchase_service import PurchaseService
from purchases.budget_planner import BudgetPlanner
from purchases.savings import SavingsGoals

#import from loan service
from loan.loan_service import LoanService
from loan.models import LoanStatus

# import penny chatbot
from chatbot.penny_chatbot import PennyChatbot

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

def debug_route(route_name):
    """Decorator to debug slow routes"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            print(f"🔍 [{datetime.now()}] Starting {route_name}")
            
            try:
                result = func(*args, **kwargs)
                end_time = time.time()
                print(f"✅ [{datetime.now()}] {route_name} completed in {end_time - start_time:.2f}s")
                return result
            except Exception as e:
                end_time = time.time()
                print(f"❌ [{datetime.now()}] {route_name} failed after {end_time - start_time:.2f}s: {e}")
                raise
                
        wrapper.__name__ = func.__name__
        return wrapper
    return decorator

@app.route('/accounts')
@login_required
def accounts():
    user_id = session.get('user_id')
    print(f"🔍 Starting accounts page for user {user_id}")
    
    try:
        print("🔍 Step 1: Calling get_accounts_by_user...")
        start_time = time.time()
        user_accounts = account_service.get_accounts_by_user(user_id)
        print(f"✅ Step 1 completed in {time.time() - start_time:.2f}s - Found {len(user_accounts)} accounts")
        
        print("🔍 Step 2: Calculating total balance...")
        start_time = time.time()
        total_balance = sum(account['balance'] for account in user_accounts)
        print(f"✅ Step 2 completed in {time.time() - start_time:.2f}s - Total: {total_balance}")
        
        print("🔍 Step 3: Getting transaction history...")
        start_time = time.time()
        recent_transactions = []
        for account in user_accounts:
            print(f"🔍 Getting transactions for account {account['account_id']}")
            transactions = account_service.get_transaction_history(account['account_id'])
            print(f"✅ Found {len(transactions)} transactions for account {account['account_id']}")
            for transaction in transactions:
                recent_transactions.append({
                    'account_id': account['account_id'],
                    'account_type': account['account_type'],
                    'transaction_type': transaction[0],
                    'amount': transaction[1],
                    'timestamp': transaction[2]
                })
        print(f"✅ Step 3 completed in {time.time() - start_time:.2f}s - Total transactions: {len(recent_transactions)}")
        
        print("🔍 Step 4: Sorting transactions...")
        start_time = time.time()
        recent_transactions.sort(key=lambda x: x['timestamp'], reverse=True)
        recent_transactions = recent_transactions[:5]
        print(f"✅ Step 4 completed in {time.time() - start_time:.2f}s")
        
    except Exception as e:
        print(f"❌ Error in accounts route: {e}")
        import traceback
        traceback.print_exc()
        user_accounts = []
        total_balance = 0
        recent_transactions = []
        flash('Error loading accounts. Please try again.')
    
    print("🔍 Rendering template...")
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
    
    print(f"🔍 Starting account creation: user={user_id}, type={account_type}")
    
    if not account_type or account_type not in ['Savings', 'Checking']:
        print("❌ Invalid account type")
        flash('Please select a valid account type.')
        return redirect(url_for('accounts'))
    
    try:
        print("🔍 Calling account_service.create_account...")
        start_time = time.time()
        account = account_service.create_account(user_id, account_type)
        print(f"✅ Account created in {time.time() - start_time:.2f}s: {account}")
        flash(f'{account_type} account created successfully!')
    except Exception as e:
        print(f"❌ Error creating account: {e}")
        import traceback
        traceback.print_exc()
        flash(f'Error creating account: {str(e)}')
    
    print("🔍 Redirecting to accounts page...")
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
    user_id = session.get('user_id')
    loan_service = LoanService()
    
    try:
        # Get user's loans
        user_loans = loan_service.get_loans_by_user(user_id)
        print(f"Found {len(user_loans)} loans for user {user_id}")
        
        # Calculate totals
        total_borrowed = sum(loan.principal for loan in user_loans if loan.status != LoanStatus.REJECTED.value)
        total_owed = sum(loan.balance_remaining for loan in user_loans if loan.status == LoanStatus.APPROVED.value)
        total_repaid = sum(loan.total_repayment for loan in user_loans)
        
    except Exception as e:
        print(f"Error fetching loans: {e}")
        user_loans = []
        total_borrowed = 0
        total_owed = 0
        total_repaid = 0
        flash('Error loading loans. Please try again.')
    
    return render_template('loans.html', 
                         current_user={'username': session.get('full_name', session.get('username', 'User'))},
                         loans=user_loans,
                         total_borrowed=total_borrowed,
                         total_owed=total_owed,
                         total_repaid=total_repaid,
                         LoanStatus=LoanStatus)

@app.route('/loans/apply', methods=['POST'])
@login_required
def apply_for_loan():
    user_id = session.get('user_id')
    
    try:
        principal = float(request.form.get('principal', 0))
        interest_rate = float(request.form.get('interest_rate', 0))
        term_months = int(request.form.get('term_months', 0))
        loan_type = request.form.get('loan_type', '')
        reason = request.form.get('reason', '')
        
        print(f"Loan application received: user_id={user_id}, principal={principal}, "
              f"interest_rate={interest_rate}, term_months={term_months}, "
              f"loan_type={loan_type}, reason={reason}")
        
        if principal <= 0 or interest_rate <= 0 or term_months <= 0:
            flash('Please enter valid loan details.')
            return redirect(url_for('loans'))
        
        if not loan_type:
            flash('Please select a loan type.')
            return redirect(url_for('loans'))
        
        loan_service = LoanService()
        loan = loan_service.apply_for_loan(user_id, principal, interest_rate, term_months, loan_type, reason)
        
        print(f"Loan application successful: loan_id={loan.id}")
        flash(f'Loan application submitted successfully! Your monthly payment will be ZMW {loan.monthly_payment:.2f}')
        
    except Exception as e:
        print(f"Error applying for loan: {str(e)}")
        import traceback
        traceback.print_exc()
        flash(f'Error applying for loan: {str(e)}')
    
    return redirect(url_for('loans'))

@app.route('/loans/repay', methods=['POST'])
@login_required
def make_repayment():
    user_id = session.get('user_id')
    
    try:
        loan_id = int(request.form.get('loan_id', 0))
        amount = float(request.form.get('amount', 0))
        
        if amount <= 0:
            flash('Please enter a valid repayment amount.')
            return redirect(url_for('loans'))
        
        loan_service = LoanService()
        
        # Verify the loan belongs to the user and is approved
        loan = loan_service.find_loan(loan_id)
        if not loan or loan.user_id != user_id:
            flash('Invalid loan or unauthorized action.')
            return redirect(url_for('loans'))
        
        if loan.status != 'approved':
            flash('You can only make repayments on approved loans.')
            return redirect(url_for('loans'))
        
        if amount > loan.balance_remaining:
            flash(f'Repayment amount cannot exceed the remaining balance of ZMW {loan.balance_remaining:.2f}')
            return redirect(url_for('loans'))
        
        # Make the repayment
        success = loan_service.make_repayment(loan_id, amount)
        
        if success:
            flash(f'Repayment of ZMW {amount:.2f} processed successfully!')
            
            # Check if loan is fully paid
            updated_loan = loan_service.find_loan(loan_id)
            if updated_loan and updated_loan.balance_remaining <= 0:
                flash('Congratulations! You have fully paid off this loan. 🎉')
                
        else:
            flash('Error processing repayment. Please try again.')
            
    except ValueError:
        flash('Please enter valid numeric values.')
    except Exception as e:
        flash(f'Error making repayment: {str(e)}')
    
    return redirect(url_for('loans'))

@app.route('/loans/calculator', methods=['POST'])
@login_required
def calculate_loan():
    try:
        # Get data from JSON or form data
        if request.is_json:
            data = request.get_json()
            principal = float(data.get('calc_principal', 0))
            interest_rate = float(data.get('calc_interest_rate', 0))
            term_months = int(data.get('calc_term_months', 0))
        else:
            principal = float(request.form.get('calc_principal', 0))
            interest_rate = float(request.form.get('calc_interest_rate', 0))
            term_months = int(request.form.get('calc_term_months', 0))
        
        # Validate inputs
        if principal <= 0 or interest_rate <= 0 or term_months <= 0:
            return jsonify({'error': 'Please enter valid values'}), 400
        
        # Calculate monthly payment
        monthly_rate = interest_rate / 100 / 12
        if monthly_rate == 0:
            monthly_payment = principal / term_months
        else:
            monthly_payment = principal * monthly_rate * (1 + monthly_rate) ** term_months / ((1 + monthly_rate) ** term_months - 1)
        
        total_payment = monthly_payment * term_months
        total_interest = total_payment - principal
        
        return jsonify({
            'monthly_payment': round(monthly_payment, 2),
            'total_payment': round(total_payment, 2),
            'total_interest': round(total_interest, 2)
        })
        
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid input values'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
        
@app.route('/plans')
@login_required
def plans():
    user_id = session.get('user_id')
    print(f"🔍 Starting plans page for user {user_id}")
    
    try:
        print("🔍 Getting current date...")
        current_month = datetime.now().strftime("%B")
        current_year = datetime.now().year
        print(f"✅ Current date: {current_month} {current_year}")
        
        print("🔍 Initializing BudgetPlanner...")
        start_time = time.time()
        budget_planner = BudgetPlanner()
        print(f"✅ BudgetPlanner initialized in {time.time() - start_time:.2f}s")
        
        print("🔍 Initializing SavingsGoals...")
        start_time = time.time()
        savings = SavingsGoals(user_id)
        print(f"✅ SavingsGoals initialized in {time.time() - start_time:.2f}s")
        
        print("🔍 Getting budgets...")
        start_time = time.time()
        budgets = budget_planner.get_budgets(user_id, current_month, current_year)
        print(f"✅ Budgets retrieved in {time.time() - start_time:.2f}s: {len(budgets)} items")
        
        print("🔍 Getting budget summary...")
        start_time = time.time()
        budget_summary = budget_planner.get_budget_summary(user_id, current_month, current_year)
        print(f"✅ Budget summary retrieved in {time.time() - start_time:.2f}s")
        
        print("🔍 Getting savings goals...")
        start_time = time.time()
        savings_goals = savings.get_goals()
        print(f"✅ Savings goals retrieved in {time.time() - start_time:.2f}s: {len(savings_goals)} goals")
        
    except Exception as e:
        print(f"❌ Error in plans route: {e}")
        import traceback
        traceback.print_exc()
        budgets = []
        budget_summary = None
        savings_goals = []
        flash('Error loading plans. Please try again.')
    
    print("🔍 Rendering plans template...")
    return render_template('plans.html', 
                         current_user={'username': session.get('full_name', session.get('username', 'User'))},
                         budgets=budgets,
                         budget_summary=budget_summary,
                         savings_goals=savings_goals,
                         current_month=current_month,
                         current_year=current_year)

@app.route('/plans/set_budget', methods=['POST'])
@login_required
def set_budget():
    user_id = session.get('user_id')
    budget_type = request.form.get('budget_type')
    amount = float(request.form.get('amount', 0))
    category = request.form.get('category', '')
    month = request.form.get('month', datetime.now().strftime("%B"))
    year = int(request.form.get('year', datetime.now().year))
    
    try:
        purchase_service = PurchaseService(user_id)
        
        if budget_type == 'overall':
            purchase_service.set_overall_budget(amount, month, year)
            flash(f'Overall budget of ZMW {amount:.2f} set for {month} {year}')
        else:
            purchase_service.set_budget_category(category, amount, month, year)
            flash(f'Budget for {category} set to ZMW {amount:.2f} for {month} {year}')
            
    except Exception as e:
        flash(f'Error setting budget: {str(e)}')
    
    return redirect(url_for('plans'))

@app.route('/plans/delete_budget', methods=['POST'])
@login_required
def delete_budget():
    user_id = session.get('user_id')
    category = request.form.get('category')
    month = request.form.get('month', datetime.now().strftime("%B"))
    year = int(request.form.get('year', datetime.now().year))
    
    try:
        purchase_service = PurchaseService(user_id)
        purchase_service.delete_budget_category(category, month, year)
        flash(f'Budget category "{category}" deleted for {month} {year}')
    except Exception as e:
        flash(f'Error deleting budget: {str(e)}')
    
    return redirect(url_for('plans'))

@app.route('/plans/add_savings_goal', methods=['POST'])
@login_required
def add_savings_goal():
    user_id = session.get('user_id')
    goal_name = request.form.get('goal_name')
    target_amount = float(request.form.get('target_amount', 0))
    
    try:
        purchase_service = PurchaseService(user_id)
        purchase_service.add_savings_goal(goal_name, target_amount)
        flash(f'Savings goal "{goal_name}" added with target of ZMW {target_amount:.2f}')
    except Exception as e:
        flash(f'Error adding savings goal: {str(e)}')
    
    return redirect(url_for('plans'))

@app.route('/plans/update_savings', methods=['POST'])
@login_required
def update_savings():
    user_id = session.get('user_id')
    goal_name = request.form.get('goal_name')
    amount = float(request.form.get('amount', 0))
    
    try:
        purchase_service = PurchaseService(user_id)
        purchase_service.update_savings_progress(goal_name, amount)
        flash(f'Updated savings for "{goal_name}" by ZMW {amount:.2f}')
    except Exception as e:
        flash(f'Error updating savings: {str(e)}')
    
    return redirect(url_for('plans'))

@app.route('/plans/delete_savings_goal', methods=['POST'])
@login_required
def delete_savings_goal():
    user_id = session.get('user_id')
    goal_name = request.form.get('goal_name')
    
    try:
        purchase_service = PurchaseService(user_id)
        purchase_service.delete_savings_goal(goal_name)
        flash(f'Savings goal "{goal_name}" deleted')
    except Exception as e:
        flash(f'Error deleting savings goal: {str(e)}')
    
    return redirect(url_for('plans'))

@app.route('/penny')
@login_required
def penny():
    user_id = session.get('user_id')
    
    # Get initial data for the chat interface
    try:
        account_service = AccountService()
        user_accounts = account_service.get_accounts_by_user(user_id)
        total_balance = sum(account['balance'] for account in user_accounts) if user_accounts else 0
        
        purchase_service = PurchaseService(user_id)
        savings_goals = purchase_service.get_savings_goals()
        
    except Exception as e:
        print(f"Error fetching data for Penny: {e}")
        user_accounts = []
        total_balance = 0
        savings_goals = []
    
    return render_template('penny.html', 
                         current_user={'username': session.get('full_name', session.get('username', 'User'))},
                         accounts=user_accounts,
                         total_balance=total_balance,
                         savings_goals=savings_goals)


@app.route('/penny/chat', methods=['POST'])
@login_required
def penny_chat():
    user_id = session.get('user_id')
    user_message = request.json.get('message', '').strip()

    if not user_message:
        return jsonify({'error': 'Empty message'}), 400

    try:
        penny_bot = PennyChatbot(user_id)
        response = penny_bot.process_message(user_message)

        return jsonify({'response': response, 'success': True})

    except Exception as e:
        print(f"Error in Penny chat: {e}")
        return jsonify({
            'response': "I'm sorry, I encountered an error. Please try again.",
            'error': str(e)
        }), 500

# Add this route to your web_app.py for testing
@app.route('/penny/test', methods=['POST'])
@login_required
def penny_test():
    try:
        user_id = session.get('user_id')
        data = request.get_json()
        
        print(f"Test route called - User ID: {user_id}")
        print(f"Request data: {data}")
        
        return jsonify({
            'success': True,
            'response': f'Test successful! User ID: {user_id}, Message: {data.get("message", "No message")}',
            'debug_info': {
                'user_id': user_id,
                'session_data': dict(session),
                'request_data': data
            }
        })
        
    except Exception as e:
        print(f"Error in test route: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'response': 'Test failed'
        }), 500
    
if __name__ == '__main__':
    print("Starting Flask application...")
    app.run(debug=True)