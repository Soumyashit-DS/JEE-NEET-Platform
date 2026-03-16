from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta
from models import db, User, Question, TestAttempt, Answer, SubjectAnalytics
from config import Config
from utils import (
    calculate_score, calculate_xp, get_random_questions,
    calculate_subject_scores, update_analytics, get_time_remaining,
    format_time_display, is_exam_expired, parse_subject_scores,
    get_answer_summary
)
import os

# ================================================================
# INITIALIZE APPLICATION
# ================================================================

app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
db.init_app(app)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    """Required by Flask-Login - loads user from ID"""
    return User.query.get(int(user_id))


# ================================================================
# SAMPLE QUESTIONS FUNCTION (MUST BE BEFORE DATABASE INIT)
# ================================================================

def add_sample_questions():
    """
    Adds sample questions to the database
    In a real app, you'd import hundreds of questions from a file
    """
    
    sample_questions = [
        # JEE Physics
        Question(exam_type='JEE', subject='Physics', chapter='Kinematics',
                question_text='A ball is thrown vertically upward with velocity 20 m/s. Maximum height reached? (g=10 m/s²)',
                option_a='10 m', option_b='20 m', option_c='30 m', option_d='40 m',
                correct_answer='B', difficulty='Easy'),
        
        Question(exam_type='JEE', subject='Physics', chapter='Electrostatics',
                question_text='Unit of electric field is:',
                option_a='N/C', option_b='C/N', option_c='J/C', option_d='C/J',
                correct_answer='A', difficulty='Easy'),
        
        Question(exam_type='JEE', subject='Physics', chapter='Work, Energy and Power',
                question_text='SI unit of power is:',
                option_a='Joule', option_b='Watt', option_c='Newton', option_d='Pascal',
                correct_answer='B', difficulty='Easy'),

        Question(exam_type='JEE', subject='Physics', chapter='Laws of Motion',
                question_text='Acceleration due to gravity is:',
                option_a='9.8 m/s²', option_b='8.9 m/s²', option_c='10.8 m/s²', option_d='7.8 m/s²',
                correct_answer='A', difficulty='Easy'),
        
        Question(exam_type='JEE', subject='Physics', chapter='Kinematics',
                question_text='A car accelerates from rest at 2 m/s² for 10 seconds. Distance covered?',
                option_a='50 m', option_b='100 m', option_c='150 m', option_d='200 m',
                correct_answer='B', difficulty='Medium'),

        Question(exam_type='JEE', subject='Physics', chapter='Thermodynamics',
                question_text='Which law of thermodynamics introduces the concept of Entropy?',
                option_a='Zeroth Law', option_b='First Law', option_c='Second Law', option_d='Third Law',
                correct_answer='C', difficulty='Easy'),

        Question(exam_type='JEE', subject='Physics', chapter='Thermodynamics',
                question_text='An ideal gas undergoes isothermal expansion. The change in internal energy is:',
                option_a='Positive', option_b='Negative', option_c='Zero', option_d='Infinite',
                correct_answer='C', difficulty='Hard'),
        
        # JEE Chemistry
        Question(exam_type='JEE', subject='Chemistry', chapter='Atomic Structure',
                question_text='Atomic number of Carbon is:',
                option_a='4', option_b='6', option_c='8', option_d='12',
                correct_answer='B', difficulty='Easy'),
        
        Question(exam_type='JEE', subject='Chemistry', chapter='Chemical Bonding',
                question_text='Laughing gas is:',
                option_a='N2O', option_b='NO2', option_c='CO2', option_d='SO2',
                correct_answer='A', difficulty='Easy'),
        
        Question(exam_type='JEE', subject='Chemistry', chapter='Ionic Equilibrium',
                question_text='pH of pure water at 25°C is:',
                option_a='6', option_b='7', option_c='8', option_d='9',
                correct_answer='B', difficulty='Easy'),

        Question(exam_type='NEET', subject='Chemistry', chapter='Basic Concepts',
                question_text='Chemical formula of water is:',
                option_a='H2O', option_b='HO2', option_c='H2O2', option_d='HO',
                correct_answer='A', difficulty='Easy'),

        Question(exam_type='NEET', subject='Chemistry', chapter='Atomic Structure',
                question_text='The maximum number of electrons that can be accommodated in an orbital is:',
                option_a='1', option_b='2', option_c='6', option_d='10',
                correct_answer='B', difficulty='Easy'),

        Question(exam_type='NEET', subject='Chemistry', chapter='Chemical Bonding',
                question_text='Which of the following molecules has a trigonal planar geometry?',
                option_a='NH3', option_b='BF3', option_c='PCl3', option_d='IF5',
                correct_answer='B', difficulty='Medium'),

        Question(exam_type='NEET', subject='Chemistry', chapter='Atomic Structure',
                question_text='The uncertainty in position of an electron is 10⁻¹⁰ m. The uncertainty in its momentum is:',
                option_a='5.27 x 10⁻²⁵ kgm/s', option_b='1.05 x 10⁻²⁴ kgm/s', option_c='Zero', option_d='Infinite',
                correct_answer='A', difficulty='Hard'),
        
        # JEE Mathematics
        Question(exam_type='JEE', subject='Mathematics', chapter='Differential Calculus',
                question_text='Derivative of x² is:',
                option_a='x', option_b='2x', option_c='x²', option_d='2x²',
                correct_answer='B', difficulty='Easy'),
        
        Question(exam_type='JEE', subject='Mathematics', chapter='Trigonometry',
                question_text='Value of sin(90°) is:',
                option_a='0', option_b='1', option_c='-1', option_d='undefined',
                correct_answer='B', difficulty='Easy'),
        
        Question(exam_type='JEE', subject='Mathematics', chapter='Functions',
                question_text='If f(x) = 3x + 2, then f(2) = ?',
                option_a='6', option_b='8', option_c='10', option_d='12',
                correct_answer='B', difficulty='Easy'),

        Question(exam_type='JEE', subject='Maths', chapter='Calculus',
                question_text='What is the derivative of sin(x²)?',
                option_a='cos(x²)', option_b='2x cos(x²)', option_c='-2x cos(x²)', option_d='2 sin(x)',
                correct_answer='B', difficulty='Medium'),

        Question(exam_type='JEE', subject='Maths', chapter='Algebra',
                question_text='If the roots of x² - 5x + 6 = 0 are p and q, then p + q is:',
                option_a='5', option_b='6', option_c='-5', option_d='1',
                correct_answer='A', difficulty='Easy'),
        
        # NEET Biology
        Question(exam_type='NEET', subject='Biology', chapter='Cell Biology',
                question_text='Powerhouse of the cell is:',
                option_a='Nucleus', option_b='Ribosome', option_c='Mitochondria', option_d='Chloroplast',
                correct_answer='C', difficulty='Easy'),
        
        Question(exam_type='NEET', subject='Biology', chapter='Molecular Basis of Inheritance',
                question_text='DNA stands for:',
                option_a='Deoxyribonucleic Acid', option_b='Dinitrogen Acid',
                option_c='Dynamic Nuclear Acid', option_d='None',
                correct_answer='A', difficulty='Easy'),
        
        Question(exam_type='NEET', subject='Biology', chapter='Human Physiology',
                question_text='Human heart has how many chambers?',
                option_a='2', option_b='3', option_c='4', option_d='5',
                correct_answer='C', difficulty='Easy'),

        Question(exam_type='NEET', subject='Biology', chapter='Plant Physiology',
                question_text='The primary CO2 acceptor in C4 plants is:',
                option_a='RuBP', option_b='PEP', option_c='PGA', option_d='OAA',
                correct_answer='B', difficulty='Hard'),

        
    ]
    
    for q in sample_questions:
        db.session.add(q)
    
    db.session.commit()


# ================================================================
# DATABASE INITIALIZATION
# ================================================================

with app.app_context():
    # Create instance folder if it doesn't exist
    if not os.path.exists('instance'):
        os.makedirs('instance')
    
    # Create all database tables
    db.create_all()
    
    # Add sample questions if database is empty
    if Question.query.count() == 0:
        add_sample_questions()
        print("✓ Sample questions added!")


# ================================================================
# ROUTE: HOME PAGE
# ================================================================

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')


# ================================================================
# ROUTE: REGISTER
# ================================================================

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password')
        full_name = request.form.get('full_name', '').strip()
        target_exam = request.form.get('target_exam')
        
        # Validation
        if not all([username, email, password, full_name, target_exam]):
            flash('All fields are required!', 'danger')
            return redirect(url_for('register'))
        
        if target_exam not in ['JEE', 'NEET']:
            flash('Invalid exam selection!', 'danger')
            return redirect(url_for('register'))
        
        # Check if username exists
        if User.query.filter_by(username=username).first():
            flash('Username already taken!', 'danger')
            return redirect(url_for('register'))
        
        # Check if email exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered!', 'danger')
            return redirect(url_for('register'))
        
        # Create new user
        user = User(
            username=username,
            email=email,
            full_name=full_name,
            target_exam=target_exam
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')


# ================================================================
# ROUTE: LOGIN
# ================================================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            flash(f'Welcome back, {user.full_name}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password!', 'danger')
    
    return render_template('login.html')


# ================================================================
# ROUTE: LOGOUT
# ================================================================

@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    
    # Clear session data
    session.clear()
    
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


# ================================================================
# ROUTE: DASHBOARD
# ================================================================

@app.route('/dashboard')
@login_required
def dashboard():
    """Student dashboard with stats and analytics"""
    
    # Get recent attempts
    recent_attempts = TestAttempt.query.filter_by(
        user_id=current_user.id,
        is_completed=True
    ).order_by(TestAttempt.submitted_at.desc()).limit(5).all()
    
    # Get analytics
    analytics = SubjectAnalytics.query.filter_by(
        user_id=current_user.id
    ).all()
    
    # Calculate stats
    if recent_attempts:
        avg_score = sum(a.total_score for a in recent_attempts) / len(recent_attempts)
        best_score = max(a.total_score for a in recent_attempts)
    else:
        avg_score = 0
        best_score = 0
    
    # Get chapter-wise performance for dashboard
    # Get all user's test attempts
    all_attempts = TestAttempt.query.filter_by(
        user_id=current_user.id,
        is_completed=True
    ).all()
    
    # Collect chapter data for each subject
    subject_chapters = {}
    for attempt in all_attempts:
        answers = Answer.query.filter_by(attempt_id=attempt.id).all()
        
        for answer in answers:
            question = Question.query.get(answer.question_id)
            if question and question.chapter:
                subject = question.subject
                chapter = question.chapter
                
                if subject not in subject_chapters:
                    subject_chapters[subject] = {'correct': {}, 'incorrect': {}}
                
                if answer.is_correct:
                    if chapter not in subject_chapters[subject]['correct']:
                        subject_chapters[subject]['correct'][chapter] = 0
                    subject_chapters[subject]['correct'][chapter] += 1
                elif answer.selected_option:  # Incorrect
                    if chapter not in subject_chapters[subject]['incorrect']:
                        subject_chapters[subject]['incorrect'][chapter] = 0
                    subject_chapters[subject]['incorrect'][chapter] += 1
    
    return render_template('dashboard.html',
                         recent_attempts=recent_attempts,
                         analytics=analytics,
                         avg_score=round(avg_score, 2),
                         best_score=round(best_score, 2),
                         subject_chapters=subject_chapters)


# ================================================================
# ROUTE: EXAM SELECTION
# ================================================================

@app.route('/exam/select')
@login_required
def exam_select():
    """Select exam type (JEE or NEET)"""
    return render_template('exam_select.html', exam_configs=Config.EXAM_CONFIGS)


# ================================================================
# ROUTE: START EXAM
# ================================================================

@app.route('/exam/start/<exam_type>')
@login_required
def start_exam(exam_type):
    """Start a new exam attempt"""
    
    if exam_type not in ['JEE', 'NEET']:
        flash('Invalid exam type!', 'danger')
        return redirect(url_for('exam_select'))
    
    # Get exam configuration
    config = Config.EXAM_CONFIGS[exam_type]
    
    # Get random questions
    questions = get_random_questions(exam_type, config['questions_per_subject'])
    
    if not questions:
        flash('No questions available for this exam!', 'warning')
        return redirect(url_for('exam_select'))
    
    # Create test attempt
    attempt = TestAttempt(
        user_id=current_user.id,
        exam_type=exam_type,
        total_questions=len(questions),
        started_at=datetime.utcnow()
    )
    db.session.add(attempt)
    db.session.commit()
    
    # Create answer records (unanswered initially)
    for question in questions:
        answer = Answer(
            attempt_id=attempt.id,
            question_id=question.id
        )
        db.session.add(answer)
    
    db.session.commit()
    
    # Store in session
    session['current_attempt_id'] = attempt.id
    session['exam_start_time'] = attempt.started_at.isoformat()
    session['exam_type'] = exam_type
    session['current_question_index'] = 0
    
    flash('Exam started! Good luck!', 'info')
    return redirect(url_for('take_exam'))


# ================================================================
# ROUTE: TAKE EXAM
# ================================================================

@app.route('/exam/take', methods=['GET', 'POST'])
@login_required
def take_exam():
    """Main exam interface - one question at a time"""
    
    # Check if exam is active
    if 'current_attempt_id' not in session:
        flash('No active exam found!', 'warning')
        return redirect(url_for('exam_select'))
    
    attempt_id = session['current_attempt_id']
    attempt = TestAttempt.query.get(attempt_id)
    
    if not attempt or attempt.user_id != current_user.id:
        flash('Invalid exam session!', 'danger')
        session.clear()
        return redirect(url_for('exam_select'))
    
    # Check if time expired
    start_time = datetime.fromisoformat(session['exam_start_time'])
    config = Config.EXAM_CONFIGS[session['exam_type']]
    
    if is_exam_expired(start_time, config['duration_minutes']):
        flash('Time expired! Exam auto-submitted.', 'warning')
        return redirect(url_for('submit_exam'))
    
    # Get all answers for this attempt (with questions)
    answers = Answer.query.filter_by(attempt_id=attempt_id).all()
    questions = []
    for ans in answers:
        q = Question.query.get(ans.question_id)
        if q:
            questions.append({'question': q, 'answer': ans})
    
    # Get current question index
    current_index = session.get('current_question_index', 0)
    
    # Handle POST (navigation or answer submission)
    if request.method == 'POST':
        action = request.form.get('action')
        
        # Save current answer
        selected_option = request.form.get('selected_option')
        if selected_option:
            current_answer = answers[current_index]
            current_question = Question.query.get(current_answer.question_id)
            
            current_answer.selected_option = selected_option
            current_answer.is_correct = (selected_option == current_question.correct_answer)
            current_answer.answered_at = datetime.utcnow()
            db.session.commit()
        
        # Handle navigation
        if action == 'next' and current_index < len(questions) - 1:
            current_index += 1
        elif action == 'previous' and current_index > 0:
            current_index -= 1
        elif action == 'jump':
            jump_to = int(request.form.get('jump_to', 0))
            if 0 <= jump_to < len(questions):
                current_index = jump_to
        
        session['current_question_index'] = current_index
        return redirect(url_for('take_exam'))
    
    # Get current question
    current_q = questions[current_index] if current_index < len(questions) else None
    
    # Calculate time remaining
    time_remaining = get_time_remaining(start_time, config['duration_minutes'])
    time_display = format_time_display(time_remaining)
    
    # Get answer summary
    answered_count = sum(1 for ans in answers if ans.selected_option)
    unanswered_count = len(answers) - answered_count
    
    return render_template('exam.html',
                         current_question=current_q,
                         current_index=current_index,
                         total_questions=len(questions),
                         all_answers=answers,
                         time_remaining=time_display,
                         time_data=time_remaining,
                         answered_count=answered_count,
                         unanswered_count=unanswered_count,
                         exam_config=config)


# ================================================================
# ROUTE: SUBMIT EXAM
# ================================================================

@app.route('/exam/submit', methods=['GET', 'POST'])
@login_required
def submit_exam():
    """Submit and grade the exam"""
    
    if 'current_attempt_id' not in session:
        flash('No active exam to submit!', 'warning')
        return redirect(url_for('exam_select'))
    
    attempt_id = session['current_attempt_id']
    attempt = TestAttempt.query.get(attempt_id)
    
    if not attempt or attempt.user_id != current_user.id:
        flash('Invalid exam session!', 'danger')
        return redirect(url_for('exam_select'))
    
    # Confirmation page
    if request.method == 'GET':
        summary = get_answer_summary(attempt_id)
        return render_template('submit_confirm.html', summary=summary)
    
    # Process submission
    attempt.submitted_at = datetime.utcnow()
    
    # Calculate time taken
    time_taken = (attempt.submitted_at - attempt.started_at).total_seconds() / 60
    attempt.time_taken_minutes = int(time_taken)
    
    # Get all answers
    answers = Answer.query.filter_by(attempt_id=attempt_id).all()
    
    # Count results
    correct = sum(1 for ans in answers if ans.is_correct)
    incorrect = sum(1 for ans in answers if ans.selected_option and not ans.is_correct)
    unattempted = sum(1 for ans in answers if not ans.selected_option)
    
    # Calculate score
    total_score = calculate_score(correct, incorrect, unattempted)
    
    # Update attempt
    attempt.correct_answers = correct
    attempt.incorrect_answers = incorrect
    attempt.unattempted = unattempted
    attempt.total_score = total_score
    attempt.is_completed = True
    
    # Calculate subject-wise scores
    subject_scores = calculate_subject_scores(attempt_id, attempt.exam_type)
    attempt.subject_scores = ','.join([f"{k}:{v}" for k, v in subject_scores.items()])
    
    # Calculate XP
    last_attempt = TestAttempt.query.filter_by(
        user_id=current_user.id,
        is_completed=True
    ).filter(TestAttempt.id != attempt_id).order_by(
        TestAttempt.submitted_at.desc()
    ).first()
    
    last_date = last_attempt.submitted_at if last_attempt else None
    xp_earned = calculate_xp(correct, last_date)
    attempt.xp_earned = xp_earned
    
    # Update user
    current_user.add_xp(xp_earned)
    current_user.total_tests_taken += 1
    
    # Update analytics
    update_analytics(current_user.id, attempt)
    
    db.session.commit()
    
    # Clear session
    session.pop('current_attempt_id', None)
    session.pop('exam_start_time', None)
    session.pop('exam_type', None)
    session.pop('current_question_index', None)
    
    flash('Exam submitted successfully!', 'success')
    return redirect(url_for('view_results', attempt_id=attempt.id))


# ================================================================
# ROUTE: VIEW RESULTS
# ================================================================

@app.route('/results/<int:attempt_id>')
@login_required
def view_results(attempt_id):
    """View detailed results of a test"""
    
    attempt = TestAttempt.query.get_or_404(attempt_id)
    
    # Security check
    if attempt.user_id != current_user.id:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get all answers with questions
    answers = Answer.query.filter_by(attempt_id=attempt_id).all()
    
    results = []
    for ans in answers:
        question = Question.query.get(ans.question_id)
        if question:
            results.append({
                'question': question,
                'answer': ans
            })
    
    # Parse subject scores
    subject_scores = parse_subject_scores(attempt.subject_scores)
    
    return render_template('results.html',
                         attempt=attempt,
                         results=results,
                         subject_scores=subject_scores)


# ================================================================
# ROUTE: ADMIN 
# ================================================================

@app.route('/admin/users')
def admin_users():
    """
    Admin page to view all registered users
    WARNING: In production, add authentication to protect this!
    """
    users = User.query.all()
    
    # Create HTML page with all users
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Registered Users - Admin</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
    </head>
    <body>
        <nav class="navbar navbar-dark bg-dark">
            <div class="container">
                <span class="navbar-brand">
                    <i class="bi bi-shield-lock"></i> Admin Panel
                </span>
            </div>
        </nav>
        
        <div class="container my-5">
            <div class="row mb-4">
                <div class="col">
                    <h2><i class="bi bi-people-fill"></i> Registered Users</h2>
                    <p class="text-muted">Total Users: <strong>{}</strong></p>
                </div>
                <div class="col text-end">
                    <a href="/" class="btn btn-primary">
                        <i class="bi bi-house"></i> Back to Home
                    </a>
                </div>
            </div>
            
            <div class="card shadow">
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table table-striped table-hover">
                            <thead class="table-dark">
                                <tr>
                                    <th>ID</th>
                                    <th>Username</th>
                                    <th>Email</th>
                                    <th>Full Name</th>
                                    <th>Target Exam</th>
                                    <th>Level</th>
                                    <th>XP</th>
                                    <th>Tests Taken</th>
                                    <th>Registered</th>
                                    <th>Last Login</th>
                                </tr>
                            </thead>
                            <tbody>
    """.format(len(users))
    
    for user in users:
        last_login = user.last_login.strftime('%d %b %Y, %I:%M %p') if user.last_login else 'Never'
        
        html += f"""
                                <tr>
                                    <td>{user.id}</td>
                                    <td><strong>{user.username}</strong></td>
                                    <td>{user.email}</td>
                                    <td>{user.full_name}</td>
                                    <td>
                                        <span class="badge bg-{'primary' if user.target_exam == 'JEE' else 'success'}">
                                            {user.target_exam}
                                        </span>
                                    </td>
                                    <td>
                                        <span class="badge bg-warning text-dark">
                                            Level {user.level}
                                        </span>
                                    </td>
                                    <td>{user.xp}</td>
                                    <td>{user.total_tests_taken}</td>
                                    <td>{user.created_at.strftime('%d %b %Y')}</td>
                                    <td>
                                        <small class="text-muted">{last_login}</small>
                                    </td>
                                </tr>
        """
    
    if not users:
        html += """
                                <tr>
                                    <td colspan="10" class="text-center text-muted">
                                        <i class="bi bi-inbox"></i> No users registered yet
                                    </td>
                                </tr>
        """
    
    html += """
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            
            <div class="alert alert-warning mt-4">
                <i class="bi bi-exclamation-triangle-fill"></i>
                <strong>Note:</strong> This is an admin panel for development. 
                In production, this should be protected with authentication!
            </div>
        </div>
    </body>
    </html>
    """
    
    return html


# ================================================================
# RUN APPLICATION
# ================================================================

if __name__ == '__main__':
    app.run(debug=True, port=5000)