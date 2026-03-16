import os

class Config:
    """
    Configuration class that stores all application settings
    """
    
    # ==================================================
    # SECURITY SETTINGS
    # ==================================================
    
    # SECRET_KEY: Used to encrypt session data
    # IMPORTANT: Change this to a random string for production!
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production-xyz123'
    
    # ==================================================
    # DATABASE SETTINGS
    # ==================================================
    
    # Where to store the database file
    # 'sqlite:///database.db' means: use SQLite, create file named 'database.db'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
    
    # Disable modification tracking (we don't need it, saves memory)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # ==================================================
    # SESSION SETTINGS (Important for timer!)
    # ==================================================
    
    # How long sessions last (in seconds)
    # For exams: 4 hours = 14400 seconds (longer than any exam)
    PERMANENT_SESSION_LIFETIME = 14400
    
    # ==================================================
    # EXAM CONFIGURATIONS
    # ==================================================
    
    # Define JEE and NEET exam parameters
    EXAM_CONFIGS = {
        'JEE': {
            'name': 'JEE Mains',
            'total_marks': 300,
            'duration_minutes': 180,  # 3 hours
            'subjects': ['Physics', 'Chemistry', 'Mathematics'],
            'questions_per_subject': 25,
            'total_questions': 75,  # 25 x 3 subjects
        },
        'NEET': {
            'name': 'NEET',
            'total_marks': 720,
            'duration_minutes': 210,  # 3.5 hours = 210 minutes
            'subjects': ['Physics', 'Chemistry', 'Biology'],
            'questions_per_subject': 45,
            'total_questions': 135,  # 45 x 3 subjects
        }
    }
    
    # ==================================================
    # SCORING RULES (Hard-coded as per requirement)
    # ==================================================
    
    MARKS_CORRECT = 4      # +4 for every correct answer
    MARKS_INCORRECT = -1   # -1 for every wrong answer
    MARKS_UNATTEMPTED = 0  # 0 for skipped questions
    
    # ==================================================
    # XP (EXPERIENCE POINTS) SYSTEM
    # ==================================================
    
    # How students earn XP and level up
    XP_PER_CORRECT = 40             # 40 XP for each correct answer
    XP_LOST_PER_INCORRECT = 10      # Lose 10 XP for each wrong answer
    XP_PER_TEST_COMPLETED = 50       # 50 bonus XP for completing test
    XP_CONSISTENCY_BONUS = 25        # 25 XP if tested within last 7 days
    XP_PER_LEVEL = 200              # Need 100 XP to level up
    
    # ==================================================
    # ANALYTICS THRESHOLDS
    # ==================================================
    
    # How to classify subjects as strength/weakness
    STRENGTH_THRESHOLD = 70.0   # 70% accuracy = Strength
    WEAKNESS_THRESHOLD = 50.0   # Below 50% = Needs serious work
    
    # ==================================================
    # PAGINATION (For future features)
    # ==================================================
    
    QUESTIONS_PER_PAGE = 1   # Show 1 question at a time
    RESULTS_PER_PAGE = 10    # Show 10 results in history
    
    # ==================================================
    # TIME WARNING THRESHOLDS (in minutes)
    # ==================================================
    
    TIME_WARNING_MINUTES = 10  # Show warning when 10 minutes left