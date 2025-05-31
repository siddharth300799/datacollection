from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import pyodbc
import os
from werkzeug.utils import secure_filename
from datetime import datetime
import json
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sslify import SSLify

app = Flask(__name__)
sslify = SSLify(app)
app.secret_key = 'your-secret-key-here'

# Database configuration
DB_CONFIG = {
    'server': 'app.msssurat.com',
    'database': 'metrodata',
    'username': 'sa',
    'password': 'diti2510',
    'driver': '{ODBC Driver 17 for SQL Server}'
}

# File upload configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_db_connection():
    """Get database connection"""
    try:
        conn_str = f"DRIVER={DB_CONFIG['driver']};SERVER={DB_CONFIG['server']};DATABASE={DB_CONFIG['database']};UID={DB_CONFIG['username']};PWD={DB_CONFIG['password']}"
        conn = pyodbc.connect(conn_str)
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def init_database():
    """Initialize database with sample data only if tables are empty"""
    conn = get_db_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    try:
        # Check if tables exist and have data
        cursor.execute("SELECT COUNT(*) FROM states")
        states_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM designations")
        designations_count = cursor.fetchone()[0]
        
        # Insert sample states data if tables are empty
        if states_count == 0:
            # Insert sample states
            states_data = [
                ('Andhra Pradesh', 'AP'),
                ('Arunachal Pradesh', 'AR'),
                ('Assam', 'AS'),
                ('Bihar', 'BR'),
                ('Chhattisgarh', 'CG'),
                ('Goa', 'GA'),
                ('Gujarat', 'GJ'),
                ('Haryana', 'HR'),
                ('Himachal Pradesh', 'HP'),
                ('Jharkhand', 'JH'),
                ('Karnataka', 'KA'),
                ('Kerala', 'KL'),
                ('Madhya Pradesh', 'MP'),
                ('Maharashtra', 'MH'),
                ('Manipur', 'MN'),
                ('Meghalaya', 'ML'),
                ('Mizoram', 'MZ'),
                ('Nagaland', 'NL'),
                ('Odisha', 'OR'),
                ('Punjab', 'PB'),
                ('Rajasthan', 'RJ'),
                ('Sikkim', 'SK'),
                ('Tamil Nadu', 'TN'),
                ('Telangana', 'TG'),
                ('Tripura', 'TR'),
                ('Uttar Pradesh', 'UP'),
                ('Uttarakhand', 'UK'),
                ('West Bengal', 'WB'),
                ('Delhi', 'DL'),
                ('Jammu and Kashmir', 'JK'),
                ('Ladakh', 'LA'),
                ('Lakshadweep', 'LD'),
                ('Puducherry', 'PY'),
                ('Andaman and Nicobar Islands', 'AN'),
                ('Chandigarh', 'CH'),
                ('Dadra and Nagar Haveli and Daman and Diu', 'DN')
            ]
            
            for state_name, state_code in states_data:
                cursor.execute("INSERT INTO states (state_name, state_code) VALUES (?, ?)", 
                             (state_name, state_code))
            
            # Insert sample districts for major states
            districts_data = [
                # Maharashtra
                ('Mumbai City', 14), ('Mumbai Suburban', 14), ('Pune', 14), ('Nagpur', 14), 
                ('Thane', 14), ('Nashik', 14), ('Aurangabad', 14), ('Solapur', 14),
                # Gujarat
                ('Ahmedabad', 7), ('Surat', 7), ('Vadodara', 7), ('Rajkot', 7), 
                ('Gandhinagar', 7), ('Jamnagar', 7), ('Junagadh', 7), ('Bharuch', 7),
                # Karnataka
                ('Bangalore Urban', 11), ('Bangalore Rural', 11), ('Mysore', 11), ('Tumkur', 11),
                ('Hassan', 11), ('Dakshina Kannada', 11), ('Belgaum', 11), ('Dharwad', 11),
                # Tamil Nadu
                ('Chennai', 23), ('Coimbatore', 23), ('Madurai', 23), ('Tiruchirappalli', 23),
                ('Salem', 23), ('Tirunelveli', 23), ('Erode', 23), ('Vellore', 23),
                # Delhi
                ('Central Delhi', 29), ('East Delhi', 29), ('New Delhi', 29), ('North Delhi', 29),
                ('South Delhi', 29), ('West Delhi', 29)
            ]
            
            for district_name, state_id in districts_data:
                cursor.execute("INSERT INTO districts (district_name, state_id) VALUES (?, ?)", 
                             (district_name, state_id))
        
        # Insert designations data if table is empty
        if designations_count == 0:
            designations_data = [
                ('AREA OFFICER', 'Security'),
                ('SECURITY SUPERVISOR', 'Security'),
                ('HEAD SECURITY GUARD', 'Security'),
                ('GENERAL MANAGER', 'Management'),
                ('LADY SEARCHER', 'Security'),
                ('PEON', 'General'),
                ('AIR GUNMAN', 'Security'),
                ('GUNMAN', 'Security'),
                ('ACCOUNTANT', 'Finance'),
                ('SENIOR SECURITY OFFICER', 'Security'),
                ('COMPUTER OPERATOR', 'IT'),
                ('OFFICE SUPERINTENDENT', 'Administration'),
                ('COMPUTER OPERTOR', 'IT'),
                ('FIREMAN', 'Safety'),
                ('CLERK', 'Administration'),
                ('ASSISTANT SECURITY OFFICER', 'Security'),
                ('BOUNCER', 'Security'),
                ('IT HEAD', 'IT'),
                ('SECURITY OFFICER', 'Security'),
                ('SECURITY GUARD', 'Security'),
                ('DRIVER', 'Transport'),
                ('EX.SERVICE MAN OFFICER', 'Security')
            ]
            
            for designation_name, department in designations_data:
                cursor.execute("INSERT INTO designations (designation_name, department) VALUES (?, ?)", 
                             (designation_name, department))
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"Database initialization error: {e}")
        return False
    finally:
        conn.close()





@app.before_request
def redirect_https_to_http():
    if request.url.startswith('https://'):
        url = request.url.replace('https://', 'http://', 1)
        return redirect(url, code=301)






# View Employee Details Route


# Add these admin credentials (you can change these)
ADMIN_CREDENTIALS = {
    'username': 'ADMIN',
    'password': 'ADMIN123'  # Change this to a secure password
}

# Session management
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            flash('Please login to access admin panel', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# Admin Login Route
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if (username == ADMIN_CREDENTIALS['username'] and 
            password == ADMIN_CREDENTIALS['password']):
            session['admin_logged_in'] = True
            session['admin_username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('admin/login.html')

# Admin Logout Route
@app.route('/admin/logout')
@login_required
def admin_logout():
    """Admin logout"""
    session.pop('admin_logged_in', None)
    session.pop('admin_username', None)
    flash('Logged out successfully', 'success')
    return redirect(url_for('admin_login'))

# Admin Dashboard Route
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    """Admin dashboard with employee list"""
    conn = get_db_connection()
    if not conn:
        flash('Database connection failed', 'error')
        return redirect(url_for('admin_login'))
    
    try:
        cursor = conn.cursor()
        
        # Get all employees with their details
        query = """
            SELECT 
                e.id,
                e.unit,
                e.first_name + ' ' + ISNULL(e.middle_name + ' ', '') + e.last_name AS full_name,
                e.mobile_no,
                e.doj,
                e.photo_path,
                d.designation_name,
                d.department,
                e.created_at
            FROM employees e
            LEFT JOIN designations d ON e.designation_id = d.id
            ORDER BY e.created_at DESC
        """
        
        cursor.execute(query)
        employees = []
        
        for row in cursor.fetchall():
            employees.append({
                'id': row[0],
                'unit': row[1],
                'full_name': row[2],
                'mobile_no': row[3],
                'doj': row[4],
                'photo_path': row[5],
                'designation': row[6],
                'department': row[7],
                'created_at': row[8]
            })
        
        # Get summary statistics
        cursor.execute("SELECT COUNT(*) FROM employees")
        total_employees = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT department) FROM designations")
        total_departments = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM employees WHERE doj >= DATEADD(month, -1, GETDATE())")
        recent_hires = cursor.fetchone()[0]
        
        conn.close()
        
        return render_template('admin/dashboard.html', 
                             employees=employees,
                             total_employees=total_employees,
                             total_departments=total_departments,
                             recent_hires=recent_hires)
    
    except Exception as e:
        conn.close()
        flash(f'Error loading dashboard: {str(e)}', 'error')
        return redirect(url_for('admin_login'))

# View Employee Details Route
# Replace the existing view_employee route with this fixed version

@app.route('/admin/employee/<int:employee_id>')
@login_required
def view_employee(employee_id):
    """View detailed employee information"""
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            flash('Database connection failed', 'error')
            return redirect(url_for('admin_dashboard'))
        
        cursor = conn.cursor()
        
        # Get employee details
        query = """
            SELECT 
                e.id, e.unit, e.first_name, e.middle_name, e.last_name, e.mobile_no, e.home_mobile_no,
                e.dob, e.doj, e.birth_place, e.gender, e.marital_status, e.spouse_name, 
                e.father_name, e.mother_name, e.education, e.institute_name, e.pf_no, e.esic_no, 
                e.uan_no, e.bank_ac_no, e.ifsc_code, e.bank_name, e.bank_branch_name, 
                e.name_in_passbook, e.pan_no, e.voter_id_no, e.blood_group, e.shoe_size, 
                e.waist, e.height, e.weight, e.chest, e.present_address, e.present_pincode,
                e.permanent_address, e.permanent_post, e.permanent_police_thana, e.permanent_tehsil,
                e.permanent_pincode, e.permanent_mobile_no, e.photo_path, e.signature_path,
                e.aadhar_front_path, e.aadhar_back_path, e.pan_photo_path, e.bank_passbook_path,
                e.certificate_path, e.created_at,
                d.designation_name, d.department,
                s1.state_name AS dob_state, s2.state_name AS present_state, s3.state_name AS permanent_state,
                dist1.district_name AS dob_district, dist2.district_name AS present_district, 
                dist3.district_name AS permanent_district
            FROM employees e
            LEFT JOIN designations d ON e.designation_id = d.id
            LEFT JOIN states s1 ON e.dob_state_id = s1.id
            LEFT JOIN states s2 ON e.present_state_id = s2.id
            LEFT JOIN states s3 ON e.permanent_state_id = s3.id
            LEFT JOIN districts dist1 ON e.dob_district_id = dist1.id
            LEFT JOIN districts dist2 ON e.present_district_id = dist2.id
            LEFT JOIN districts dist3 ON e.permanent_district_id = dist3.id
            WHERE e.id = ?
        """
        
        cursor.execute(query, (employee_id,))
        employee_row = cursor.fetchone()
        
        if not employee_row:
            flash('Employee not found', 'error')
            return redirect(url_for('admin_dashboard'))
        
        # Get family details
        cursor.execute("SELECT * FROM family_details WHERE employee_id = ?", (employee_id,))
        family_members = cursor.fetchall()
        
        # Convert employee row to dictionary BEFORE closing connection
        employee = {
            'id': employee_row[0],
            'unit': employee_row[1],
            'first_name': employee_row[2],
            'middle_name': employee_row[3],
            'last_name': employee_row[4],
            'mobile_no': employee_row[5],
            'home_mobile_no': employee_row[6],
            'dob': employee_row[7],
            'doj': employee_row[8],
            'birth_place': employee_row[9],
            'gender': employee_row[10],
            'marital_status': employee_row[11],
            'spouse_name': employee_row[12],
            'father_name': employee_row[13],
            'mother_name': employee_row[14],
            'education': employee_row[15],
            'institute_name': employee_row[16],
            'pf_no': employee_row[17],
            'esic_no': employee_row[18],
            'uan_no': employee_row[19],
            'bank_ac_no': employee_row[20],
            'ifsc_code': employee_row[21],
            'bank_name': employee_row[22],
            'bank_branch_name': employee_row[23],
            'name_in_passbook': employee_row[24],
            'pan_no': employee_row[25],
            'voter_id_no': employee_row[26],
            'blood_group': employee_row[27],
            'shoe_size': employee_row[28],
            'waist': employee_row[29],
            'height': employee_row[30],
            'weight': employee_row[31],
            'chest': employee_row[32],
            'present_address': employee_row[33],
            'present_pincode': employee_row[34],
            'permanent_address': employee_row[35],
            'permanent_post': employee_row[36],
            'permanent_police_thana': employee_row[37],
            'permanent_tehsil': employee_row[38],
            'permanent_pincode': employee_row[39],
            'permanent_mobile_no': employee_row[40],
            'photo_path': employee_row[41],
            'signature_path': employee_row[42],
            'aadhar_front_path': employee_row[43],
            'aadhar_back_path': employee_row[44],
            'pan_photo_path': employee_row[45],
            'bank_passbook_path': employee_row[46],
            'certificate_path': employee_row[47],
            'created_at': employee_row[48],
            'designation_name': employee_row[49],
            'department': employee_row[50],
            'dob_state': employee_row[51],
            'present_state': employee_row[52],
            'permanent_state': employee_row[53],
            'dob_district': employee_row[54],
            'present_district': employee_row[55],
            'permanent_district': employee_row[56]
        }
        
        # Convert family members to list for template safety
        family_list = []
        for member in family_members:
            family_list.append(list(member))
        
        # Close connection BEFORE rendering template
        conn.close()
        
        # Now render template with dictionary data
        return render_template('admin/view_employee.html', 
                             employee=employee,
                             family_members=family_list)
    
    except Exception as e:
        if conn:
            try:
                conn.close()
            except:
                pass  # Connection might already be closed
        flash(f'Error loading employee: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard'))








@app.route('/test/employee/<int:employee_id>')
def test_employee_data(employee_id):
    """Test route to check employee and designation data"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'})
    
    try:
        cursor = conn.cursor()
        
        # Get employee data
        cursor.execute("SELECT id, first_name, last_name, designation_id FROM employees WHERE id = ?", (employee_id,))
        employee = cursor.fetchone()
        
        if not employee:
            return jsonify({'error': 'Employee not found'})
        
        # Get all designations
        cursor.execute("SELECT id, designation_name, department FROM designations ORDER BY id")
        designations = cursor.fetchall()
        
        # Get the specific designation for this employee
        cursor.execute("""
            SELECT d.id, d.designation_name, d.department 
            FROM designations d 
            WHERE d.id = ?
        """, (employee[3],))
        employee_designation = cursor.fetchone()
        
        conn.close()
        
        result = {
            'employee': {
                'id': employee[0],
                'name': f"{employee[1]} {employee[2]}",
                'designation_id': employee[3],
                'designation_id_type': str(type(employee[3]).__name__)
            },
            'employee_designation': {
                'id': employee_designation[0] if employee_designation else None,
                'name': employee_designation[1] if employee_designation else None,
                'department': employee_designation[2] if employee_designation else None
            } if employee_designation else None,
            'all_designations': [
                {
                    'id': d[0], 
                    'name': d[1], 
                    'department': d[2],
                    'id_type': str(type(d[0]).__name__)
                } 
                for d in designations[:10]  # Show first 10
            ],
            'total_designations': len(designations)
        }
        
        return jsonify(result)
        
    except Exception as e:
        if conn:
            conn.close()
        return jsonify({'error': str(e)})











@app.route('/admin/employee/<int:employee_id>/print')
@login_required
def print_employee(employee_id):
    """Print employee details"""
    conn = get_db_connection()
    if not conn:
        flash('Database connection failed', 'error')
        return redirect(url_for('admin_dashboard'))
    
    try:
        cursor = conn.cursor()
        
        # Get employee details with all related information
        query = """
            SELECT 
                e.id, e.unit, e.first_name, e.middle_name, e.last_name, e.mobile_no, e.home_mobile_no,
                e.dob, e.doj, e.birth_place, e.gender, e.marital_status, e.spouse_name, 
                e.father_name, e.mother_name, e.education, e.institute_name, e.pf_no, e.esic_no, 
                e.uan_no, e.bank_ac_no, e.ifsc_code, e.bank_name, e.bank_branch_name, 
                e.name_in_passbook, e.pan_no, e.voter_id_no, e.blood_group, e.shoe_size, 
                e.waist, e.height, e.weight, e.chest, e.present_address, e.present_pincode,
                e.permanent_address, e.permanent_post, e.permanent_police_thana, e.permanent_tehsil,
                e.permanent_pincode, e.permanent_mobile_no, e.photo_path, e.signature_path,
                e.aadhar_front_path, e.aadhar_back_path, e.pan_photo_path, e.bank_passbook_path,
                e.certificate_path, e.created_at,
                d.designation_name, d.department,
                s1.state_name AS dob_state, s2.state_name AS present_state, s3.state_name AS permanent_state,
                dist1.district_name AS dob_district, dist2.district_name AS present_district, 
                dist3.district_name AS permanent_district
            FROM employees e
            LEFT JOIN designations d ON e.designation_id = d.id
            LEFT JOIN states s1 ON e.dob_state_id = s1.id
            LEFT JOIN states s2 ON e.present_state_id = s2.id
            LEFT JOIN states s3 ON e.permanent_state_id = s3.id
            LEFT JOIN districts dist1 ON e.dob_district_id = dist1.id
            LEFT JOIN districts dist2 ON e.present_district_id = dist2.id
            LEFT JOIN districts dist3 ON e.permanent_district_id = dist3.id
            WHERE e.id = ?
        """
        
        cursor.execute(query, (employee_id,))
        employee_row = cursor.fetchone()
        
        if not employee_row:
            flash('Employee not found', 'error')
            return redirect(url_for('admin_dashboard'))
        
        # Convert to dictionary
        employee = {
            'id': employee_row[0],
            'unit': employee_row[1],
            'first_name': employee_row[2],
            'middle_name': employee_row[3],
            'last_name': employee_row[4],
            'full_name': f"{employee_row[2]} {employee_row[3] or ''} {employee_row[4]}".strip(),
            'mobile_no': employee_row[5],
            'home_mobile_no': employee_row[6],
            'dob': employee_row[7],
            'doj': employee_row[8],
            'birth_place': employee_row[9],
            'gender': employee_row[10],
            'marital_status': employee_row[11],
            'spouse_name': employee_row[12],
            'father_name': employee_row[13],
            'mother_name': employee_row[14],
            'education': employee_row[15],
            'institute_name': employee_row[16],
            'pf_no': employee_row[17],
            'esic_no': employee_row[18],
            'uan_no': employee_row[19],
            'bank_ac_no': employee_row[20],
            'ifsc_code': employee_row[21],
            'bank_name': employee_row[22],
            'bank_branch_name': employee_row[23],
            'name_in_passbook': employee_row[24],
            'pan_no': employee_row[25],
            'voter_id_no': employee_row[26],
            'blood_group': employee_row[27],
            'shoe_size': employee_row[28],
            'waist': employee_row[29],
            'height': employee_row[30],
            'weight': employee_row[31],
            'chest': employee_row[32],
            'present_address': employee_row[33],
            'present_pincode': employee_row[34],
            'permanent_address': employee_row[35],
            'permanent_post': employee_row[36],
            'permanent_police_thana': employee_row[37],
            'permanent_tehsil': employee_row[38],
            'permanent_pincode': employee_row[39],
            'permanent_mobile_no': employee_row[40],
            'photo_path': employee_row[41],
            'signature_path': employee_row[42],
            'aadhar_front_path': employee_row[43],
            'aadhar_back_path': employee_row[44],
            'pan_photo_path': employee_row[45],
            'bank_passbook_path': employee_row[46],
            'certificate_path': employee_row[47],
            'created_at': employee_row[48],
            'designation_name': employee_row[49],
            'department': employee_row[50],
            'dob_state': employee_row[51],
            'present_state': employee_row[52],
            'permanent_state': employee_row[53],
            'dob_district': employee_row[54],
            'present_district': employee_row[55],
            'permanent_district': employee_row[56]
        }
        
        # Get family members
        cursor.execute("SELECT * FROM family_details WHERE employee_id = ?", (employee_id,))
        family_members = cursor.fetchall()
        
        conn.close()
        
        return render_template('admin/employee_print.html', 
                             employee=employee, 
                             family_members=family_members)
                             
    except Exception as e:
        if conn:
            conn.close()
        flash(f'Error loading employee details: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard'))








# Edit Employee Route
@app.route('/admin/employee/<int:employee_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_employee(employee_id):
    """Edit employee information"""
    conn = get_db_connection()
    if not conn:
        flash('Database connection failed', 'error')
        return redirect(url_for('admin_dashboard'))
    
    cursor = conn.cursor()
    
    if request.method == 'GET':
        try:
            # Get employee data for editing - FIXED QUERY with correct field order
            query = """
                SELECT 
                    e.id, e.unit, e.first_name, e.middle_name, e.last_name, e.mobile_no, e.home_mobile_no,
                    e.dob, e.doj, e.birth_place, 
                    e.dob_state_id, e.dob_district_id, e.designation_id,
                    e.gender, e.marital_status, e.spouse_name, 
                    e.father_name, e.mother_name, e.education, e.institute_name, e.pf_no, e.esic_no, 
                    e.uan_no, e.bank_ac_no, e.ifsc_code, e.bank_name, e.bank_branch_name, 
                    e.name_in_passbook, e.pan_no, e.voter_id_no, e.blood_group, e.shoe_size, 
                    e.waist, e.height, e.weight, e.chest, e.present_address, 
                    e.present_state_id, e.present_district_id, e.present_pincode,
                    e.permanent_address, e.permanent_post, e.permanent_police_thana, e.permanent_tehsil,
                    e.permanent_state_id, e.permanent_district_id, e.permanent_pincode, e.permanent_mobile_no, 
                    e.photo_path, e.signature_path, e.aadhar_front_path, e.aadhar_back_path, 
                    e.pan_photo_path, e.bank_passbook_path, e.certificate_path, e.created_at,
                    d.designation_name, d.department,
                    s1.state_name AS dob_state, s2.state_name AS present_state, s3.state_name AS permanent_state,
                    dist1.district_name AS dob_district, dist2.district_name AS present_district, 
                    dist3.district_name AS permanent_district
                FROM employees e
                LEFT JOIN designations d ON e.designation_id = d.id
                LEFT JOIN states s1 ON e.dob_state_id = s1.id
                LEFT JOIN states s2 ON e.present_state_id = s2.id
                LEFT JOIN states s3 ON e.permanent_state_id = s3.id
                LEFT JOIN districts dist1 ON e.dob_district_id = dist1.id
                LEFT JOIN districts dist2 ON e.present_district_id = dist2.id
                LEFT JOIN districts dist3 ON e.permanent_district_id = dist3.id
                WHERE e.id = ?
            """
            
            cursor.execute(query, (employee_id,))
            employee_row = cursor.fetchone()
            
            if not employee_row:
                flash('Employee not found', 'error')
                return redirect(url_for('admin_dashboard'))
            
            # Convert to dictionary - FIXED INDICES to match the new query order
            employee = {
                'id': employee_row[0],
                'unit': employee_row[1],
                'first_name': employee_row[2],
                'middle_name': employee_row[3],
                'last_name': employee_row[4],
                'mobile_no': employee_row[5],
                'home_mobile_no': employee_row[6],
                'dob': employee_row[7],
                'doj': employee_row[8],
                'birth_place': employee_row[9],
                # ID fields moved up in the query for easier access
                'dob_state_id': employee_row[10],
                'dob_district_id': employee_row[11],
                'designation_id': employee_row[12],  # This is now at index 12
                'gender': employee_row[13],
                'marital_status': employee_row[14],
                'spouse_name': employee_row[15],
                'father_name': employee_row[16],
                'mother_name': employee_row[17],
                'education': employee_row[18],
                'institute_name': employee_row[19],
                'pf_no': employee_row[20],
                'esic_no': employee_row[21],
                'uan_no': employee_row[22],
                'bank_ac_no': employee_row[23],
                'ifsc_code': employee_row[24],
                'bank_name': employee_row[25],
                'bank_branch_name': employee_row[26],
                'name_in_passbook': employee_row[27],
                'pan_no': employee_row[28],
                'voter_id_no': employee_row[29],
                'blood_group': employee_row[30],
                'shoe_size': employee_row[31],
                'waist': employee_row[32],
                'height': employee_row[33],
                'weight': employee_row[34],
                'chest': employee_row[35],
                'present_address': employee_row[36],
                'present_state_id': employee_row[37],
                'present_district_id': employee_row[38],
                'present_pincode': employee_row[39],
                'permanent_address': employee_row[40],
                'permanent_post': employee_row[41],
                'permanent_police_thana': employee_row[42],
                'permanent_tehsil': employee_row[43],
                'permanent_state_id': employee_row[44],
                'permanent_district_id': employee_row[45],
                'permanent_pincode': employee_row[46],
                'permanent_mobile_no': employee_row[47],
                'photo_path': employee_row[48],
                'signature_path': employee_row[49],
                'aadhar_front_path': employee_row[50],
                'aadhar_back_path': employee_row[51],
                'pan_photo_path': employee_row[52],
                'bank_passbook_path': employee_row[53],
                'certificate_path': employee_row[54],
                'created_at': employee_row[55],
                'designation_name': employee_row[56],
                'department': employee_row[57],
                'dob_state': employee_row[58],
                'present_state': employee_row[59],
                'permanent_state': employee_row[60],
                'dob_district': employee_row[61],
                'present_district': employee_row[62],
                'permanent_district': employee_row[63]
            }
            
            # Get states, districts, and designations for dropdowns
            cursor.execute("SELECT id, state_name FROM states ORDER BY state_name")
            states = cursor.fetchall()
            
            cursor.execute("SELECT id, designation_name, department FROM designations ORDER BY designation_name")
            designations = cursor.fetchall()
            
            # Get family details
            cursor.execute("SELECT * FROM family_details WHERE employee_id = ?", (employee_id,))
            family_members = cursor.fetchall()
            
            conn.close()
            
            return render_template('admin/edit_employee.html',
                                 employee=employee,
                                 states=states,
                                 designations=designations,
                                 family_members=family_members)
        
        except Exception as e:
            conn.close()
            flash(f'Error loading employee data: {str(e)}', 'error')
            return redirect(url_for('admin_dashboard'))
    
    elif request.method == 'POST':
        try:
            # Handle file uploads
            file_paths = {}
            file_fields = ['photo', 'signature', 'aadhar_front', 'aadhar_back', 'pan_photo', 'bank_passbook', 'certificate']
            
            for field in file_fields:
                if field in request.files and request.files[field].filename:
                    file = request.files[field]
                    if allowed_file(file.filename):
                        filename = secure_filename(f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}")
                        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                        file.save(file_path)
                        file_paths[f'{field}_path'] = file_path
                    else:
                        file_paths[f'{field}_path'] = None
                else:
                    # Keep existing file path
                    file_paths[f'{field}_path'] = request.form.get(f'existing_{field}_path')
            
            # Update employee data
            update_query = """
                UPDATE employees SET
                    unit = ?, first_name = ?, middle_name = ?, last_name = ?, mobile_no = ?, home_mobile_no = ?,
                    dob = ?, doj = ?, birth_place = ?, dob_state_id = ?, dob_district_id = ?, designation_id = ?,
                    gender = ?, marital_status = ?, spouse_name = ?, father_name = ?, mother_name = ?,
                    education = ?, institute_name = ?, pf_no = ?, esic_no = ?, uan_no = ?, bank_ac_no = ?,
                    ifsc_code = ?, bank_name = ?, bank_branch_name = ?, name_in_passbook = ?, pan_no = ?,
                    voter_id_no = ?, blood_group = ?, shoe_size = ?, waist = ?, height = ?, weight = ?, chest = ?,
                    present_address = ?, present_state_id = ?, present_district_id = ?, present_pincode = ?,
                    permanent_address = ?, permanent_post = ?, permanent_police_thana = ?, permanent_tehsil = ?,
                    permanent_state_id = ?, permanent_district_id = ?, permanent_pincode = ?, permanent_mobile_no = ?,
                    photo_path = ?, signature_path = ?, aadhar_front_path = ?, aadhar_back_path = ?,
                    pan_photo_path = ?, bank_passbook_path = ?, certificate_path = ?
                WHERE id = ?
            """
            
            update_data = (
                request.form.get('unit'),
                request.form.get('first_name'),
                request.form.get('middle_name'),
                request.form.get('last_name'),
                request.form.get('mobile_no'),
                request.form.get('home_mobile_no'),
                request.form.get('dob') or None,
                request.form.get('doj') or None,
                request.form.get('birth_place'),
                int(request.form.get('dob_state')) if request.form.get('dob_state') else None,
                int(request.form.get('dob_district')) if request.form.get('dob_district') else None,
                int(request.form.get('designation')) if request.form.get('designation') else None,
                request.form.get('gender'),
                request.form.get('marital_status'),
                request.form.get('spouse_name'),
                request.form.get('father_name'),
                request.form.get('mother_name'),
                request.form.get('education'),
                request.form.get('institute_name'),
                request.form.get('pf_no'),
                request.form.get('esic_no'),
                request.form.get('uan_no'),
                request.form.get('bank_ac_no'),
                request.form.get('ifsc_code'),
                request.form.get('bank_name'),
                request.form.get('bank_branch_name'),
                request.form.get('name_in_passbook'),
                request.form.get('pan_no'),
                request.form.get('voter_id_no'),
                request.form.get('blood_group'),
                request.form.get('shoe_size'),
                request.form.get('waist'),
                request.form.get('height'),
                request.form.get('weight'),
                request.form.get('chest'),
                request.form.get('present_address'),
                int(request.form.get('present_state')) if request.form.get('present_state') else None,
                int(request.form.get('present_district')) if request.form.get('present_district') else None,
                request.form.get('present_pincode'),
                request.form.get('permanent_address'),
                request.form.get('permanent_post'),
                request.form.get('permanent_police_thana'),
                request.form.get('permanent_tehsil'),
                int(request.form.get('permanent_state')) if request.form.get('permanent_state') else None,
                int(request.form.get('permanent_district')) if request.form.get('permanent_district') else None,
                request.form.get('permanent_pincode'),
                request.form.get('permanent_mobile_no'),
                file_paths['photo_path'],
                file_paths['signature_path'],
                file_paths['aadhar_front_path'],
                file_paths['aadhar_back_path'],
                file_paths['pan_photo_path'],
                file_paths['bank_passbook_path'],
                file_paths['certificate_path'],
                employee_id
            )
            
            cursor.execute(update_query, update_data)
            
            # Update family details (delete existing and insert new)
            cursor.execute("DELETE FROM family_details WHERE employee_id = ?", (employee_id,))
            
            family_data = request.form.get('family_details')
            if family_data:
                try:
                    family_members = json.loads(family_data)
                    for member in family_members:
                        if member.get('name') and member.get('name').strip():
                            family_query = """
                                INSERT INTO family_details (employee_id, name, relationship, aadhar_no, mobile_no, dob)
                                VALUES (?, ?, ?, ?, ?, ?)
                            """
                            family_member_data = (
                                employee_id,
                                member.get('name').strip(),
                                member.get('relationship'),
                                member.get('aadhar_no'),
                                member.get('mobile_no'),
                                member.get('dob') if member.get('dob') else None
                            )
                            cursor.execute(family_query, family_member_data)
                except json.JSONDecodeError:
                    pass
            
            conn.commit()
            conn.close()
            
            flash('Employee updated successfully!', 'success')
            return redirect(url_for('view_employee', employee_id=employee_id))
        
        except Exception as e:
            conn.rollback()
            conn.close()
            flash(f'Error updating employee: {str(e)}', 'error')
            return redirect(url_for('edit_employee', employee_id=employee_id))

# Delete Employee Route
@app.route('/admin/employee/<int:employee_id>/delete', methods=['POST'])
@login_required
def delete_employee(employee_id):
    """Delete employee record"""
    conn = get_db_connection()
    if not conn:
        flash('Database connection failed', 'error')
        return redirect(url_for('admin_dashboard'))
    
    try:
        cursor = conn.cursor()
        
        # Get employee name before deletion
        cursor.execute("SELECT first_name + ' ' + last_name FROM employees WHERE id = ?", (employee_id,))
        result = cursor.fetchone()
        
        if not result:
            flash('Employee not found', 'error')
            return redirect(url_for('admin_dashboard'))
        
        employee_name = result[0]
        
        # Delete family details first (foreign key constraint)
        cursor.execute("DELETE FROM family_details WHERE employee_id = ?", (employee_id,))
        
        # Delete employee
        cursor.execute("DELETE FROM employees WHERE id = ?", (employee_id,))
        
        conn.commit()
        conn.close()
        
        flash(f'Employee "{employee_name}" deleted successfully!', 'success')
        
    except Exception as e:
        conn.rollback()
        conn.close()
        flash(f'Error deleting employee: {str(e)}', 'error')
    
    return redirect(url_for('admin_dashboard'))

# Search Employees Route
@app.route('/admin/search')
@login_required
def search_employees():
    """Search employees"""
    search_term = request.args.get('q', '').strip()
    
    if not search_term:
        return redirect(url_for('admin_dashboard'))
    
    conn = get_db_connection()
    if not conn:
        flash('Database connection failed', 'error')
        return redirect(url_for('admin_dashboard'))
    
    try:
        cursor = conn.cursor()
        
        # Search in multiple fields
        search_query = """
            SELECT 
                e.id,
                e.unit,
                e.first_name + ' ' + ISNULL(e.middle_name + ' ', '') + e.last_name AS full_name,
                e.mobile_no,
                e.doj,
                e.photo_path,
                d.designation_name,
                d.department,
                e.created_at
            FROM employees e
            LEFT JOIN designations d ON e.designation_id = d.id
            WHERE 
                e.first_name LIKE ? OR 
                e.middle_name LIKE ? OR 
                e.last_name LIKE ? OR 
                e.mobile_no LIKE ? OR 
                e.unit LIKE ? OR
                d.designation_name LIKE ?
            ORDER BY e.created_at DESC
        """
        
        search_pattern = f'%{search_term}%'
        cursor.execute(search_query, (search_pattern, search_pattern, search_pattern, 
                                    search_pattern, search_pattern, search_pattern))
        
        employees = []
        for row in cursor.fetchall():
            employees.append({
                'id': row[0],
                'unit': row[1],
                'full_name': row[2],
                'mobile_no': row[3],
                'doj': row[4],
                'photo_path': row[5],
                'designation': row[6],
                'department': row[7],
                'created_at': row[8]
            })
        
        conn.close()
        
        return render_template('admin/dashboard.html', 
                             employees=employees,
                             search_term=search_term,
                             total_employees=len(employees),
                             total_departments=0,
                             recent_hires=0)
    
    except Exception as e:
        conn.close()
        flash(f'Error searching employees: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard'))

# Add session import at the top
from flask import session




















@app.route('/')
def index():
    """Home page with employee registration form"""
    return render_template('index.html')

@app.route('/api/states')
def get_states():
    """API endpoint to get all states"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor()
    cursor.execute("SELECT id, state_name FROM states ORDER BY state_name")
    states = [{'id': row[0], 'name': row[1]} for row in cursor.fetchall()]
    conn.close()
    
    return jsonify(states)

@app.route('/api/districts/<int:state_id>')
def get_districts(state_id):
    """API endpoint to get districts by state"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor()
    cursor.execute("SELECT id, district_name FROM districts WHERE state_id = ? ORDER BY district_name", (state_id,))
    districts = [{'id': row[0], 'name': row[1]} for row in cursor.fetchall()]
    conn.close()
    
    return jsonify(districts)

@app.route('/api/designations')
def get_designations():
    """API endpoint to get all designations"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor()
    cursor.execute("SELECT id, designation_name, department FROM designations ORDER BY designation_name")
    designations = [{'id': row[0], 'name': row[1], 'department': row[2]} for row in cursor.fetchall()]
    conn.close()
    
    return jsonify(designations)

@app.route('/submit', methods=['POST'])
def submit_employee():
    """Handle employee form submission"""
    try:
        conn = get_db_connection()
        if not conn:
            flash('Database connection failed', 'error')
            return redirect(url_for('index'))
        
        cursor = conn.cursor()
        
        # Handle file uploads
        file_paths = {}
        file_fields = ['photo', 'signature', 'aadhar_front', 'aadhar_back', 'pan_photo', 'bank_passbook', 'certificate']
        
        for field in file_fields:
            if field in request.files:
                file = request.files[field]
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}")
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    file_paths[f'{field}_path'] = file_path
                else:
                    file_paths[f'{field}_path'] = None
            else:
                file_paths[f'{field}_path'] = None
        
        # Insert employee data - EXACTLY 53 fields and 53 parameters
        employee_query = """
            INSERT INTO employees (
                unit, first_name, middle_name, last_name, mobile_no, home_mobile_no,
                dob, doj, birth_place, dob_state_id, dob_district_id, designation_id,
                gender, marital_status, spouse_name, father_name, mother_name,
                education, institute_name, pf_no, esic_no, uan_no, bank_ac_no,
                ifsc_code, bank_name, bank_branch_name, name_in_passbook, pan_no,
                voter_id_no, blood_group, shoe_size, waist, height, weight, chest,
                present_address, present_state_id, present_district_id, present_pincode,
                permanent_address, permanent_post, permanent_police_thana, permanent_tehsil,
                permanent_state_id, permanent_district_id, permanent_pincode, permanent_mobile_no,
                photo_path, signature_path, aadhar_front_path, aadhar_back_path,
                pan_photo_path, bank_passbook_path, certificate_path
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        employee_data = (
            request.form.get('unit'),                    # 1
            request.form.get('first_name'),              # 2
            request.form.get('middle_name'),             # 3
            request.form.get('last_name'),               # 4
            request.form.get('mobile_no'),               # 5
            request.form.get('home_mobile_no'),          # 6
            request.form.get('dob') or None,             # 7
            request.form.get('doj') or None,             # 8
            request.form.get('birth_place'),             # 9
            int(request.form.get('dob_state')) if request.form.get('dob_state') else None,      # 10
            int(request.form.get('dob_district')) if request.form.get('dob_district') else None, # 11
            int(request.form.get('designation')) if request.form.get('designation') else None,   # 12
            request.form.get('gender'),                  # 13
            request.form.get('marital_status'),          # 14
            request.form.get('spouse_name'),             # 15
            request.form.get('father_name'),             # 16
            request.form.get('mother_name'),             # 17
            request.form.get('education'),               # 18
            request.form.get('institute_name'),          # 19
            request.form.get('pf_no'),                   # 20
            request.form.get('esic_no'),                 # 21
            request.form.get('uan_no'),                  # 22
            request.form.get('bank_ac_no'),              # 23
            request.form.get('ifsc_code'),               # 24
            request.form.get('bank_name'),               # 25
            request.form.get('bank_branch_name'),        # 26
            request.form.get('name_in_passbook'),        # 27
            request.form.get('pan_no'),                  # 28
            request.form.get('voter_id_no'),             # 29
            request.form.get('blood_group'),             # 30
            request.form.get('shoe_size'),               # 31
            request.form.get('waist'),                   # 32
            request.form.get('height'),                  # 33
            request.form.get('weight'),                  # 34
            request.form.get('chest'),                   # 35
            request.form.get('present_address'),         # 36
            int(request.form.get('present_state')) if request.form.get('present_state') else None,     # 37
            int(request.form.get('present_district')) if request.form.get('present_district') else None, # 38
            request.form.get('present_pincode'),         # 39
            request.form.get('permanent_address'),       # 40
            request.form.get('permanent_post'),          # 41
            request.form.get('permanent_police_thana'),  # 42
            request.form.get('permanent_tehsil'),        # 43
            int(request.form.get('permanent_state')) if request.form.get('permanent_state') else None,    # 44
            int(request.form.get('permanent_district')) if request.form.get('permanent_district') else None, # 45
            request.form.get('permanent_pincode'),       # 46
            request.form.get('permanent_mobile_no'),     # 47
            file_paths['photo_path'],                    # 48
            file_paths['signature_path'],                # 49
            file_paths['aadhar_front_path'],             # 50
            file_paths['aadhar_back_path'],              # 51
            file_paths['pan_photo_path'],                # 52
            file_paths['bank_passbook_path'],            # 53
            file_paths['certificate_path']               # 54 - REMOVED this to match 53 parameters
        )
        
        # Debug: Print the number of parameters for verification
        column_count = len([field.strip() for field in employee_query.split('(')[1].split(')')[0].split(',')])
        placeholder_count = employee_query.count('?')
        parameter_count = len(employee_data)
        
        print(f"SQL columns count: {column_count}")
        print(f"SQL placeholders: {placeholder_count}")
        print(f"Parameters provided: {parameter_count}")
        
        if column_count != placeholder_count or placeholder_count != parameter_count:
            print(f"ERROR: Mismatch detected!")
            print(f"Columns: {column_count}, Placeholders: {placeholder_count}, Parameters: {parameter_count}")
            raise Exception(f"Parameter count mismatch: {column_count} columns, {placeholder_count} placeholders, {parameter_count} parameters")
        
        cursor.execute(employee_query, employee_data)
        
        # Get the employee ID that was just inserted
        cursor.execute("SELECT @@IDENTITY")
        result = cursor.fetchone()
        
        if result and result[0]:
            employee_id = result[0]
            print(f"Employee inserted successfully with ID: {employee_id}")
            
            # Handle family details
            family_data = request.form.get('family_details')
            if family_data:
                try:
                    family_members = json.loads(family_data)
                    family_count = 0
                    for member in family_members:
                        if member.get('name') and member.get('name').strip():  # Only insert if name is provided and not empty
                            family_query = """
                                INSERT INTO family_details (employee_id, name, relationship, aadhar_no, mobile_no, dob)
                                VALUES (?, ?, ?, ?, ?, ?)
                            """
                            family_member_data = (
                                employee_id,
                                member.get('name').strip(),
                                member.get('relationship'),
                                member.get('aadhar_no'),
                                member.get('mobile_no'),
                                member.get('dob') if member.get('dob') else None
                            )
                            cursor.execute(family_query, family_member_data)
                            family_count += 1
                    print(f"Family details inserted successfully: {family_count} members")
                except json.JSONDecodeError as e:
                    print(f"JSON decode error for family data: {e}")
                except Exception as e:
                    print(f"Error inserting family data: {e}")
            else:
                print("No family details provided")
            
            conn.commit()
            conn.close()
            
            flash(f'Employee data submitted successfully! Employee ID: {employee_id}', 'success')
            return redirect(url_for('index'))
        else:
            conn.rollback()
            conn.close()
            flash('Error: Employee was not inserted properly', 'error')
            return redirect(url_for('index'))
        
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        flash(f'Error submitting data: {str(e)}', 'error')
        return redirect(url_for('index'))





if __name__ == '__main__':
    # Initialize database on startup
    init_database()
    
    # Run the app without SSL context
    app.run(debug=True, host='0.0.0.0', port=5000)
