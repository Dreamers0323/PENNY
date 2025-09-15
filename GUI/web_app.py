from flask import Flask, render_template, redirect, url_for, request, flash, session
from functools import wraps
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import your existing backend services
from user.db import init_db
from user.repositories.sqllite_user_repo import SQLiteUserRepository
from user.services.RegistrationService import RegistrationService
from user.services.AuthenticationSer import AuthenticationService

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = 'your_secret_key_here'  # Change this to a random secret key

# Initialize your database and services
print("Initializing database...")
init_db()
# Use the same database path that your Flask app expects
db_path = 'C:\\Users\\Taizya Yambayamba\\Desktop\\Programming works\\Penny\\database\\penny.db'
repo = SQLiteUserRepository(db_path)
reg_service = RegistrationService(repo)
auth_service = AuthenticationService(repo)
print("Services initialized successfully!")

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
        username = request.form['username']
        password = request.form['password']
        
        try:
            # Use the new login_with_username method
            user_id = auth_service.login_with_username(username, password)
            session['user_id'] = user_id
            session['username'] = username
            session['full_name'] = username
            flash(f'Welcome back, {username}!')
            return redirect(url_for('dashboard'))
            
        except ValueError as e:
            flash(f'Login failed: {str(e)}')
            print(f"Login ValueError: {e}")
        except AttributeError as e:
            flash('Login method not available.')
            print(f"Method error: {e}")
        except Exception as e:
            flash('An error occurred during login. Please try again.')
            print(f"Login error: {e}")
    
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
    return render_template('dashboard.html', 
                         current_user={'username': session.get('full_name', session.get('username', 'User'))})

@app.route('/accounts')
@login_required
def accounts():
    return render_template('accounts.html', 
                         current_user={'username': session.get('full_name', session.get('username', 'User'))})

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