"""
Shared utility functions for the Quiz App.
"""
import uuid
import string
import random
from django.utils import timezone


def generate_unique_code(length=8):
    """Generate a random alphanumeric code."""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=length))


def get_client_ip(request):
    """Extract the client IP address from the request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def format_duration(seconds):
    """Format seconds into a human-readable duration string."""
    if seconds is None:
        return 'N/A'
    hours, remainder = divmod(int(seconds), 3600)
    minutes, secs = divmod(remainder, 60)
    if hours > 0:
        return f'{hours}h {minutes}m {secs}s'
    if minutes > 0:
        return f'{minutes}m {secs}s'
    return f'{secs}s'


def get_time_greeting():
    """Return a greeting based on the current time."""
    hour = timezone.now().hour
    if hour < 12:
        return 'Good morning'
    elif hour < 17:
        return 'Good afternoon'
    return 'Good evening'
