from datetime import timedelta

from django.contrib.auth.models import User
from django.utils import timezone

from events.models import Event

organizer = User.objects.filter(is_superuser=True).first() or User.objects.filter(is_staff=True).first()
if organizer is None:
    raise SystemExit("Pahila createsuperuser chalaunu.")

now = timezone.now().replace(minute=0, second=0, microsecond=0)

# (title, description, location, days_from_now, duration_hours, capacity)
EVENTS = [
    ("Django REST API Workshop", "Hands-on workshop: build REST APIs with Django and DRF.", "Patan Multiple Campus, Lalitpur", 5, 4, 40),
    ("Web Development Bootcamp", "Full-day bootcamp covering HTML, CSS, JavaScript and backend basics.", "Kathmandu IT Park, Baneshwor", 8, 8, 60),
    ("Tech Meetup Kathmandu", "Monthly meetup for developers: lightning talks and networking.", "Thamel, Kathmandu", 12, 3, 100),
    ("AI & Machine Learning Seminar", "Introduction to AI/ML with real-world examples and Q&A.", "Tribhuvan University, Kirtipur", 15, 3, 150),
    ("Resume & Interview Preparation", "Tips for CVs, GitHub profiles and technical interviews for students.", "Online (Google Meet)", 18, 2, 200),
    ("Hackathon 2026: Build for Nepal", "24-hour hackathon to solve local problems with technology.", "Pulchowk Campus, Lalitpur", 25, 24, 80),
    ("Cyber Security Awareness Day", "Learn how to stay safe online: passwords, phishing and privacy.", "Bhaktapur Multiple Campus", 30, 5, 120),
    ("Startup Pitch Night", "Student teams pitch startup ideas to mentors and investors.", "Jawalakhel, Lalitpur", 40, 4, 50),
]

created = 0
for title, desc, loc, days, hours, cap in EVENTS:
    start = now + timedelta(days=days, hours=2)
    _, was_created = Event.objects.get_or_create(
        title=title,
        defaults=dict(
            organizer=organizer, description=desc, location=loc,
            start_time=start, end_time=start + timedelta(hours=hours), capacity=cap,
        ),
    )
    created += was_created

print(f"{created} new event(s) added. Total events: {Event.objects.count()}")
