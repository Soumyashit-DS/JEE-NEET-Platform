from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Create the database object
# This will be used throughout the application
db = SQLAlchemy()


# ================================================================
# USER MODEL - Stores Student Information
# ================================================================

class User(UserMixin, db.Model):
    """
    Represents a student/user in the system
    Like a student ID card with all details
    
    UserMixin provides: is_authenticated, is_active, is_anonymous, get_id()
    """
    
    # Table name in database
    __tablename__ = 'user'
    
    # ===== PRIMARY KEY =====
    id = db.Column(db.Integer, primary_key=True)
    
    # ===== LOGIN CREDENTIALS =====
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(200), nullable=False)
    
    # ===== STUDENT PROFILE =====
    full_name = db.Column(db.String(100), nullable=False)
    target_exam = db.Column(db.String(10), nullable=False)  # 'JEE' or 'NEET'
    
    # ===== GAMIFICATION FIELDS =====
    xp = db.Column(db.Integer, default=0)              # Experience points
    level = db.Column(db.Integer, default=1)           # Current level
    total_tests_taken = db.Column(db.Integer, default=0)
    
    # ===== TIMESTAMPS =====
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # ===== RELATIONSHIPS =====
    # Link to test attempts (one user can have many attempts)
    attempts = db.relationship('TestAttempt', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """
        Encrypts and stores the password
        NEVER store passwords in plain text!
        """
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """
        Checks if the provided password is correct
        """
        return check_password_hash(self.password_hash, password)
    
    def add_xp(self, xp_points):
        """
        Adds XP and automatically handles level-up
        
        Example: If user has 80 XP at level 1, and earns 30 XP:
        - Total XP = 110
        - Levels up to 2 (needs 100 XP for level 1)
        - Remaining XP = 110 - 100 = 10
        """
        self.xp += xp_points
        
        # Check for level up
        # Each level requires (level × 100) XP
        while self.xp >= self.level * 100:
            self.xp -= self.level * 100
            self.level += 1
    
    def __repr__(self):
        """How to represent this object when debugging"""
        return f'<User {self.username}>'


# ================================================================
# QUESTION MODEL - Stores Exam Questions
# ================================================================

class Question(db.Model):
    """
    Represents a single question in the question bank
    """
    
    __tablename__ = 'question'
    
    # ===== PRIMARY KEY =====
    id = db.Column(db.Integer, primary_key=True)
    
    # ===== QUESTION DETAILS =====
    exam_type = db.Column(db.String(10), nullable=False, index=True)  # 'JEE' or 'NEET'
    subject = db.Column(db.String(50), nullable=False, index=True)
    chapter = db.Column(db.String(100))  # NEW: Chapter/Topic name
    question_text = db.Column(db.Text, nullable=False)
    
    # ===== OPTIONS =====
    option_a = db.Column(db.Text, nullable=False)
    option_b = db.Column(db.Text, nullable=False)
    option_c = db.Column(db.Text, nullable=False)
    option_d = db.Column(db.Text, nullable=False)
    
    # ===== ANSWER =====
    correct_answer = db.Column(db.String(1), nullable=False)  # 'A', 'B', 'C', or 'D'
    
    # ===== METADATA =====
    difficulty = db.Column(db.String(20))  # 'Easy', 'Medium', 'Hard'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Question {self.id}: {self.subject}>'


# ================================================================
# TEST ATTEMPT MODEL - Records Each Test Taken
# ================================================================

class TestAttempt(db.Model):
    """
    Records every time a student takes a test
    Stores all details: timing, scores, answers, etc.
    """
    
    __tablename__ = 'test_attempt'
    
    # ===== PRIMARY KEY =====
    id = db.Column(db.Integer, primary_key=True)
    
    # ===== FOREIGN KEY =====
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # ===== TEST DETAILS =====
    exam_type = db.Column(db.String(10), nullable=False)  # 'JEE' or 'NEET'
    
    # ===== TIMING =====
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    submitted_at = db.Column(db.DateTime)
    time_taken_minutes = db.Column(db.Integer)
    
    # ===== SCORES =====
    total_questions = db.Column(db.Integer, nullable=False)
    correct_answers = db.Column(db.Integer, default=0)
    incorrect_answers = db.Column(db.Integer, default=0)
    unattempted = db.Column(db.Integer, default=0)
    total_score = db.Column(db.Float, default=0.0)
    
    # ===== SUBJECT-WISE SCORES (stored as string) =====
    # Format: "Physics:80,Chemistry:72,Math:88"
    subject_scores = db.Column(db.Text)
    
    # ===== XP EARNED =====
    xp_earned = db.Column(db.Integer, default=0)
    
    # ===== STATUS =====
    is_completed = db.Column(db.Boolean, default=False)
    
    # ===== RELATIONSHIPS =====
    answers = db.relationship('Answer', backref='attempt', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<TestAttempt {self.id} by User {self.user_id}>'


# ================================================================
# ANSWER MODEL - Individual Answer for Each Question
# ================================================================

class Answer(db.Model):
    """
    Stores each individual answer given by student
    """
    
    __tablename__ = 'answer'
    
    # ===== PRIMARY KEY =====
    id = db.Column(db.Integer, primary_key=True)
    
    # ===== FOREIGN KEYS =====
    attempt_id = db.Column(db.Integer, db.ForeignKey('test_attempt.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    
    # ===== ANSWER DETAILS =====
    selected_option = db.Column(db.String(1))  # 'A', 'B', 'C', 'D', or None
    is_correct = db.Column(db.Boolean)
    
    # ===== METADATA =====
    answered_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # ===== RELATIONSHIPS =====
    question = db.relationship('Question', backref='student_answers')
    
    def __repr__(self):
        return f'<Answer Q{self.question_id}: {self.selected_option}>'


# ================================================================
# SUBJECT ANALYTICS MODEL - Performance Tracking
# ================================================================

class SubjectAnalytics(db.Model):
    """
    Tracks performance in each subject over time
    Used for the "Strengths & Weaknesses" dashboard
    """
    
    __tablename__ = 'subject_analytics'
    
    # ===== PRIMARY KEY =====
    id = db.Column(db.Integer, primary_key=True)
    
    # ===== FOREIGN KEY =====
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # ===== SUBJECT DETAILS =====
    exam_type = db.Column(db.String(10), nullable=False)
    subject = db.Column(db.String(50), nullable=False, index=True)
    
    # ===== PERFORMANCE METRICS =====
    total_attempts = db.Column(db.Integer, default=0)
    total_questions = db.Column(db.Integer, default=0)
    correct_answers = db.Column(db.Integer, default=0)
    accuracy_percentage = db.Column(db.Float, default=0.0)
    average_score = db.Column(db.Float, default=0.0)
    
    # ===== CLASSIFICATION =====
    category = db.Column(db.String(20))  # 'Strength' or 'Weakness'
    
    # ===== TIMESTAMPS =====
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # ===== UNIQUE CONSTRAINT =====
    # Each user can have only ONE analytics record per subject
    __table_args__ = (
        db.UniqueConstraint('user_id', 'exam_type', 'subject', name='unique_user_subject'),
    )
    
    def __repr__(self):
        return f'<Analytics User:{self.user_id} {self.subject}>'