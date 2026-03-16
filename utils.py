"""
UTILS.PY - Helper Functions
============================
This file contains utility functions used throughout the app.
All functions are PURE Python - no JavaScript!
"""

from datetime import datetime, timedelta
from models import db, Question, Answer, SubjectAnalytics
from config import Config
import random


def calculate_score(correct, incorrect, unattempted):
    """
    Calculates total score based on marking scheme
    
    Args:
        correct: Number of correct answers
        incorrect: Number of incorrect answers
        unattempted: Number of unattempted questions
    
    Returns:
        float: Total score
    """
    score = (correct * Config.MARKS_CORRECT) + (incorrect * Config.MARKS_INCORRECT)
    return float(score)


def calculate_xp(correct_answers, last_attempt_date=None):
    """
    Calculates XP earned from a test
    
    Args:
        correct_answers: Number of correct answers
        last_attempt_date: Date of last test (for consistency bonus)
    
    Returns:
        int: Total XP earned
    """
    # Base XP from correct answers
    xp = correct_answers * Config.XP_PER_CORRECT
    
    # Completion bonus
    xp += Config.XP_PER_TEST_COMPLETED
    
    # Consistency bonus (if tested within last 7 days)
    if last_attempt_date:
        days_since_last = (datetime.utcnow() - last_attempt_date).days
        if days_since_last <= 7:
            xp += Config.XP_CONSISTENCY_BONUS
    
    return xp


def get_random_questions(exam_type, questions_per_subject):
    """
    Selects random questions for an exam
    
    Args:
        exam_type: 'JEE' or 'NEET'
        questions_per_subject: Number of questions needed per subject
    
    Returns:
        list: List of Question objects
    """
    config = Config.EXAM_CONFIGS[exam_type]
    subjects = config['subjects']
    
    all_questions = []
    
    for subject in subjects:
        # Get all questions for this subject
        subject_questions = Question.query.filter_by(
            exam_type=exam_type,
            subject=subject
        ).all()
        
        # Randomly select required number
        if len(subject_questions) >= questions_per_subject:
            selected = random.sample(subject_questions, questions_per_subject)
        else:
            # If not enough questions, take all available
            selected = subject_questions
        
        all_questions.extend(selected)
    
    # Shuffle all questions together
    random.shuffle(all_questions)
    
    return all_questions


def calculate_subject_scores(attempt_id, exam_type):
    """
    Calculates score for each subject in the test
    
    Args:
        attempt_id: ID of the test attempt
        exam_type: 'JEE' or 'NEET'
    
    Returns:
        dict: Subject names as keys, scores as values
    """
    config = Config.EXAM_CONFIGS[exam_type]
    subjects = config['subjects']
    
    subject_scores = {}
    
    for subject in subjects:
        # Get all answers for this subject
        answers = db.session.query(Answer).join(Question).filter(
            Answer.attempt_id == attempt_id,
            Question.subject == subject
        ).all()
        
        # Count correct and incorrect
        correct = sum(1 for ans in answers if ans.is_correct)
        incorrect = sum(1 for ans in answers if ans.selected_option and not ans.is_correct)
        
        # Calculate score
        score = calculate_score(correct, incorrect, 0)
        subject_scores[subject] = score
    
    return subject_scores


def update_analytics(user_id, attempt):
    """
    Updates subject-wise analytics after a test
    
    Args:
        user_id: ID of the user
        attempt: TestAttempt object
    """
    # Parse subject scores
    if attempt.subject_scores:
        # Format: "Physics:80,Chemistry:72,Math:88"
        subject_score_dict = {}
        for item in attempt.subject_scores.split(','):
            subject, score = item.split(':')
            subject_score_dict[subject] = float(score)
    else:
        return
    
    # Get all answers for this attempt
    answers = Answer.query.filter_by(attempt_id=attempt.id).all()
    
    # Group answers by subject
    from collections import defaultdict
    subject_answers = defaultdict(list)
    
    for answer in answers:
        question = Question.query.get(answer.question_id)
        if question:
            subject_answers[question.subject].append(answer)
    
    # Update or create analytics for each subject
    for subject, score in subject_score_dict.items():
        # Get or create analytics record
        analytics = SubjectAnalytics.query.filter_by(
            user_id=user_id,
            exam_type=attempt.exam_type,
            subject=subject
        ).first()
        
        if not analytics:
            analytics = SubjectAnalytics(
                user_id=user_id,
                exam_type=attempt.exam_type,
                subject=subject,
                total_attempts=0,
                total_questions=0,
                correct_answers=0,
                accuracy_percentage=0.0,
                average_score=0.0
            )
            db.session.add(analytics)
        
        # Ensure fields are not None (database safety)
        if analytics.total_attempts is None:
            analytics.total_attempts = 0
        if analytics.total_questions is None:
            analytics.total_questions = 0
        if analytics.correct_answers is None:
            analytics.correct_answers = 0
        if analytics.average_score is None:
            analytics.average_score = 0.0
        
        # Get answers for this subject
        subj_answers = subject_answers.get(subject, [])
        
        # Count statistics
        total_qs = len(subj_answers)
        correct_qs = sum(1 for ans in subj_answers if ans.is_correct)
        
        # Update analytics
        analytics.total_attempts += 1
        analytics.total_questions += total_qs
        analytics.correct_answers += correct_qs
        
        # Calculate accuracy
        if analytics.total_questions > 0:
            analytics.accuracy_percentage = (analytics.correct_answers / analytics.total_questions) * 100
        
        # Calculate average score
        old_avg = analytics.average_score
        old_count = analytics.total_attempts - 1
        
        if old_count > 0:
            analytics.average_score = ((old_avg * old_count) + score) / analytics.total_attempts
        else:
            analytics.average_score = score
        
        # Classify as Strength or Weakness
        if analytics.accuracy_percentage >= Config.STRENGTH_THRESHOLD:
            analytics.category = 'Strength'
        else:
            analytics.category = 'Weakness'
        
        analytics.updated_at = datetime.utcnow()
    
    db.session.commit()


def get_time_remaining(start_time, duration_minutes):
    """
    Calculates remaining time in an exam
    
    Args:
        start_time: datetime when exam started
        duration_minutes: Total duration in minutes
    
    Returns:
        dict: Hours, minutes, seconds remaining (or None if time expired)
    """
    if not start_time:
        return None
    
    # Calculate end time
    end_time = start_time + timedelta(minutes=duration_minutes)
    
    # Calculate remaining time
    now = datetime.utcnow()
    remaining = end_time - now
    
    if remaining.total_seconds() <= 0:
        return {
            'hours': 0,
            'minutes': 0,
            'seconds': 0,
            'expired': True
        }
    
    # Convert to hours, minutes, seconds
    total_seconds = int(remaining.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    
    return {
        'hours': hours,
        'minutes': minutes,
        'seconds': seconds,
        'expired': False,
        'total_seconds': total_seconds
    }


def format_time_display(time_dict):
    """
    Formats time dictionary into display string
    
    Args:
        time_dict: Dictionary from get_time_remaining
    
    Returns:
        str: Formatted time string (e.g., "02:30:15")
    """
    if not time_dict or time_dict.get('expired'):
        return "00:00:00"
    
    return "{:02d}:{:02d}:{:02d}".format(
        time_dict['hours'],
        time_dict['minutes'],
        time_dict['seconds']
    )


def is_exam_expired(start_time, duration_minutes):
    """
    Checks if exam time has expired
    
    Args:
        start_time: datetime when exam started
        duration_minutes: Total duration in minutes
    
    Returns:
        bool: True if expired, False otherwise
    """
    if not start_time:
        return False
    
    end_time = start_time + timedelta(minutes=duration_minutes)
    return datetime.utcnow() >= end_time


def get_chart_data(analytics_list):
    """
    Prepares data for charts (for template rendering)
    
    Args:
        analytics_list: List of SubjectAnalytics objects
    
    Returns:
        dict: Chart data with labels and values
    """
    subjects = [a.subject for a in analytics_list]
    accuracies = [round(a.accuracy_percentage, 1) for a in analytics_list]
    avg_scores = [round(a.average_score, 1) for a in analytics_list]
    
    return {
        'subjects': subjects,
        'accuracies': accuracies,
        'avg_scores': avg_scores
    }


def parse_subject_scores(score_string):
    """
    Parses subject score string into dictionary
    
    Args:
        score_string: String like "Physics:80,Chemistry:72,Math:88"
    
    Returns:
        dict: Subject names as keys, scores as values
    """
    if not score_string:
        return {}
    
    result = {}
    for item in score_string.split(','):
        try:
            subject, score = item.split(':')
            result[subject] = float(score)
        except:
            continue
    
    return result


def get_answer_summary(attempt_id):
    """
    Gets summary of answers (for submission confirmation)
    
    Args:
        attempt_id: ID of test attempt
    
    Returns:
        dict: Count of answered, unanswered, marked questions
    """
    answers = Answer.query.filter_by(attempt_id=attempt_id).all()
    
    answered = sum(1 for ans in answers if ans.selected_option)
    unanswered = len(answers) - answered
    
    return {
        'answered': answered,
        'unanswered': unanswered,
        'total': len(answers)
    }