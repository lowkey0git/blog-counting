
# app/__ai
# ===============================================
from typing import Dict, List
from app.env import WorkRecord


def analyze_worker_productivity(work_record: WorkRecord) -> Dict:
    """Analyze productivity and return insights"""
    duration_hours = work_record.calculate_work_duration_hours()
    blog_posts = work_record.blog_posts_count

    productivity_score = calculate_productivity_score(duration_hours, blog_posts)
    productivity_rating = get_productivity_rating(productivity_score)
    analysis = generate_productivity_analysis(duration_hours, blog_posts, productivity_score)
    recommendations = generate_recommendations(duration_hours, blog_posts, productivity_score)
    anomaly_info = detect_anomalies(duration_hours, blog_posts)

    return {
        "duration_hours": duration_hours,
        "productivity_score": productivity_score,
        "productivity_rating": productivity_rating,
        "analysis": analysis,
        "recommendations": recommendations,
        "is_anomaly": anomaly_info["is_anomaly"],
        "anomaly_reason": anomaly_info["reason"]
    }


def calculate_productivity_score(duration_hours: float, blog_posts: int) -> float:
    """Calculate productivity score from 0-100"""
    time_score = 0
    output_score = 0
    efficiency_score = 0

    # Time score (0-40 points)
    if duration_hours <= 0:
        time_score = 0
    elif duration_hours <= 4:
        time_score = duration_hours * 5
    elif duration_hours <= 8:
        time_score = 20 + (duration_hours - 4) * 5
    elif duration_hours <= 10:
        time_score = 40 - (duration_hours - 8) * 2.5
    else:
        time_score = max(30, 40 - (duration_hours - 8) * 3)

    # Output score (0-40 points)
    if blog_posts == 0:
        output_score = 0
    elif blog_posts <= 3:
        output_score = blog_posts * 10
    elif blog_posts <= 6:
        output_score = 30 + (blog_posts - 3) * 3
    else:
        output_score = min(40, 30 + (blog_posts - 3) * 2)

    # Efficiency score (0-20 points)
    if duration_hours > 0 and blog_posts > 0:
        posts_per_hour = blog_posts / duration_hours
        if posts_per_hour >= 1:
            efficiency_score = 20
        elif posts_per_hour >= 0.5:
            efficiency_score = 15
        elif posts_per_hour >= 0.25:
            efficiency_score = 10
        else:
            efficiency_score = 5
    else:
        efficiency_score = 0

    total_score = time_score + output_score + efficiency_score
    return min(100, max(0, round(total_score, 1)))


def get_productivity_rating(score: float) -> str:
    """Convert score to rating"""
    if score >= 90:
        return "Excellent"
    elif score >= 75:
        return "Good"
    elif score >= 60:
        return "Above Average"
    elif score >= 40:
        return "Average"
    elif score >= 25:
        return "Below Average"
    else:
        return "Poor"


def generate_productivity_analysis(duration_hours: float, blog_posts: int, score: float) -> str:
    """Generate human-readable analysis"""
    analysis_parts = []

    # Time analysis
    if duration_hours < 4:
        analysis_parts.append(f"Worked {duration_hours} hours, which is quite short.")
    elif duration_hours < 6:
        analysis_parts.append(f"Worked {duration_hours} hours, below a full workday.")
    elif duration_hours <= 8:
        analysis_parts.append(f"Worked {duration_hours} hours, a standard workday.")
    elif duration_hours <= 10:
        analysis_parts.append(f"Worked {duration_hours} hours, slightly longer than standard.")
    else:
        analysis_parts.append(f"Worked {duration_hours} hours, which is quite long.")

    # Output analysis
    if blog_posts == 0:
        analysis_parts.append("No blog posts were completed.")
    elif blog_posts == 1:
        analysis_parts.append("Completed 1 blog post.")
    elif blog_posts <= 3:
        analysis_parts.append(f"Completed {blog_posts} blog posts, solid output.")
    elif blog_posts <= 6:
        analysis_parts.append(f"Completed {blog_posts} blog posts, high productivity.")
    else:
        analysis_parts.append(f"Completed {blog_posts} blog posts, exceptional output.")

    # Overall assessment
    if score >= 80:
        analysis_parts.append("Overall, this was a highly productive day.")
    elif score >= 60:
        analysis_parts.append("Overall, this was a reasonably productive day.")
    elif score >= 40:
        analysis_parts.append("Overall, this was an average productivity day.")
    else:
        analysis_parts.append("Overall, there's significant room for improvement.")

    return " ".join(analysis_parts)


def generate_recommendations(duration_hours: float, blog_posts: int, score: float) -> List[str]:
    """Generate improvement recommendations"""
    recommendations = []

    if duration_hours < 6:
        recommendations.append("Consider working closer to a full 8-hour day.")
    elif duration_hours > 10:
        recommendations.append("Consider breaking up very long work sessions.")

    if blog_posts == 0:
        recommendations.append("Focus on completing at least one blog post per session.")
    elif blog_posts < 2 and duration_hours >= 6:
        recommendations.append("Try to increase blog post output - aim for 2-3 posts.")

    if duration_hours > 0 and blog_posts > 0:
        posts_per_hour = blog_posts / duration_hours
        if posts_per_hour < 0.25:
            recommendations.append("Consider time-blocking techniques to improve efficiency.")

    if score < 50:
        recommendations.append("Set specific daily goals for both time and output.")
    elif score < 70:
        recommendations.append("You're doing well! Try to maintain consistency.")

    if not recommendations:
        recommendations.append("Great work! Keep maintaining this level of productivity.")

    return recommendations


def detect_anomalies(duration_hours: float, blog_posts: int) -> Dict:
    """Detect anomalous work patterns"""
    is_anomaly = False
    reasons = []

    if duration_hours > 12:
        is_anomaly = True
        reasons.append("Extremely long work session (>12 hours)")
    elif duration_hours < 1:
        is_anomaly = True
        reasons.append("Very short work session (<1 hour)")

    if blog_posts > 10:
        is_anomaly = True
        reasons.append("Unusually high blog post output")
    elif duration_hours > 6 and blog_posts == 0:
        is_anomaly = True
        reasons.append("Long work session with no blog posts")

    if duration_hours > 0 and blog_posts > 0:
        posts_per_hour = blog_posts / duration_hours
        if posts_per_hour > 2:
            is_anomaly = True
            reasons.append("Unusually high productivity rate")
        elif posts_per_hour < 0.1 and duration_hours > 4:
            is_anomaly = True
            reasons.append("Unusually low productivity rate")

    return {
        "is_anomaly": is_anomaly,
        "reason": "; ".join(reasons) if reasons else None
    }

