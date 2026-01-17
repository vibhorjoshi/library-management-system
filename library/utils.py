"""
Utility functions for the library management system.
"""

from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


def send_notification_email(subject, email_to, message_text, template_name=None, context=None):
    """
    Send email notification to user.
    
    Args:
        subject: Email subject
        email_to: Recipient email address (or list of emails)
        message_text: Plain text message
        template_name: Optional HTML email template path
        context: Optional context dict for template rendering
    
    Returns:
        Number of emails sent (1 for success, 0 for failure)
    """
    try:
        if template_name and context:
            # Send HTML email with template
            html_message = render_to_string(template_name, context)
            text_message = strip_tags(html_message) if not message_text else message_text
        else:
            html_message = message_text.replace('\n', '<br>')
            text_message = message_text
        
        # Convert single email to list
        if isinstance(email_to, str):
            email_to = [email_to]
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=email_to
        )
        
        if template_name and context:
            email.attach_alternative(html_message, "text/html")
        
        result = email.send(fail_silently=False)
        logger.info(f"Email sent to {email_to}: {subject}")
        return result
    
    except Exception as e:
        logger.error(f"Error sending email to {email_to}: {str(e)}")
        return 0


def send_registration_confirmation(user):
    """Send welcome email to newly registered user."""
    subject = f"Welcome to Library Management System, {user.username}!"
    message = f"""
    Hello {user.get_full_name() or user.username},

    Welcome to our Library Management System!
    
    Your account has been successfully created.
    Username: {user.username}
    Email: {user.email}

    You can now log in and start using all library features.

    Best regards,
    Library Management Team
    """
    
    return send_notification_email(
        subject=subject,
        email_to=user.email,
        message_text=message
    )


def send_book_issue_notification(user, issued_book):
    """Send notification when a book is issued to user."""
    subject = f"Book Issued: {issued_book.book.title}"
    message = f"""
    Hello {user.get_full_name() or user.username},

    A book has been issued to your account.

    Book Details:
    Title: {issued_book.book.title}
    Author: {issued_book.book.author}
    ISBN: {issued_book.book.isbn}

    Issue Date: {issued_book.issue_date.strftime('%Y-%m-%d')}
    Due Date: {issued_book.due_date.strftime('%Y-%m-%d')}

    Please return the book on or before the due date to avoid fines.

    Best regards,
    Library Management Team
    """
    
    return send_notification_email(
        subject=subject,
        email_to=user.email,
        message_text=message
    )


def send_book_return_notification(user, issued_book):
    """Send confirmation when a book is returned."""
    subject = f"Book Returned: {issued_book.book.title}"
    message = f"""
    Hello {user.get_full_name() or user.username},

    We confirm receipt of the returned book.

    Book Details:
    Title: {issued_book.book.title}
    Author: {issued_book.book.author}

    Return Date: {issued_book.return_date.strftime('%Y-%m-%d')}

    Thank you for using our library!

    Best regards,
    Library Management Team
    """
    
    return send_notification_email(
        subject=subject,
        email_to=user.email,
        message_text=message
    )


def send_due_reminder(user, issued_book):
    """Send reminder about upcoming book due date."""
    days_remaining = (issued_book.due_date.date() - timezone.now().date()).days
    
    subject = f"Book Due Reminder: {issued_book.book.title}"
    message = f"""
    Hello {user.get_full_name() or user.username},

    This is a friendly reminder that the following book is due soon.

    Book Details:
    Title: {issued_book.book.title}
    Author: {issued_book.book.author}
    ISBN: {issued_book.book.isbn}

    Issue Date: {issued_book.issue_date.strftime('%Y-%m-%d')}
    Due Date: {issued_book.due_date.strftime('%Y-%m-%d')}
    Days Remaining: {max(0, days_remaining)}

    Please return the book on time to avoid fines.

    Best regards,
    Library Management Team
    """
    
    return send_notification_email(
        subject=subject,
        email_to=user.email,
        message_text=message
    )


def send_overdue_notification(user, issued_book):
    """Send overdue book notification."""
    subject = f"OVERDUE NOTICE: {issued_book.book.title}"
    message = f"""
    Hello {user.get_full_name() or user.username},

    The following book is now OVERDUE!

    Book Details:
    Title: {issued_book.book.title}
    Author: {issued_book.book.author}
    ISBN: {issued_book.book.isbn}

    Issue Date: {issued_book.issue_date.strftime('%Y-%m-%d')}
    Due Date: {issued_book.due_date.strftime('%Y-%m-%d')}

    Overdue Amount: {issued_book.fine_amount}

    Please return the book immediately to avoid additional fines.

    Best regards,
    Library Management Team
    """
    
    return send_notification_email(
        subject=subject,
        email_to=user.email,
        message_text=message
    )


def send_fine_notification(user, fine):
    """Send fine payment notification."""
    subject = f"Fine Notice - Amount Due: Rs. {fine.amount}"
    message = f"""
    Hello {user.get_full_name() or user.username},

    A fine has been applied to your account.

    Fine Details:
    Amount: Rs. {fine.amount}
    Reason: {fine.reason}
    Date: {fine.created_at.strftime('%Y-%m-%d')}
    Status: {'Paid' if fine.paid else 'Pending'}

    Please settle the fine at your earliest convenience.

    Best regards,
    Library Management Team
    """
    
    return send_notification_email(
        subject=subject,
        email_to=user.email,
        message_text=message
    )


def send_reservation_fulfilled(user, reservation):
    """Send notification when a reserved book becomes available."""
    subject = f"Book Available: {reservation.book.title}"
    message = f"""
    Hello {user.get_full_name() or user.username},

    Good news! The book you reserved is now available.

    Book Details:
    Title: {reservation.book.title}
    Author: {reservation.book.author}
    ISBN: {reservation.book.isbn}

    Please visit the library to pick up your reserved copy.

    Best regards,
    Library Management Team
    """
    
    return send_notification_email(
        subject=subject,
        email_to=user.email,
        message_text=message
    )


def send_batch_overdue_reminders():
    """
    Send overdue reminders to all users with overdue books.
    This function should be called periodically via Celery or Cron job.
    """
    from .models import IssuedBook
    
    overdue_books = IssuedBook.objects.filter(
        status='overdue',
        return_date__isnull=True
    )
    
    count = 0
    for issued_book in overdue_books:
        try:
            send_overdue_notification(issued_book.user, issued_book)
            count += 1
        except Exception as e:
            logger.error(f"Failed to send overdue notification: {str(e)}")
    
    logger.info(f"Sent {count} overdue notifications")
    return count


def send_batch_due_reminders(days_ahead=3):
    """
    Send due reminders to users whose books are due in N days.
    This function should be called periodically via Celery or Cron job.
    """
    from .models import IssuedBook
    
    target_date = timezone.now() + timedelta(days=days_ahead)
    
    upcoming_due_books = IssuedBook.objects.filter(
        due_date__date=target_date.date(),
        return_date__isnull=True,
        status__in=['issued', 'overdue']
    )
    
    count = 0
    for issued_book in upcoming_due_books:
        try:
            send_due_reminder(issued_book.user, issued_book)
            count += 1
        except Exception as e:
            logger.error(f"Failed to send due reminder: {str(e)}")
    
    logger.info(f"Sent {count} due reminders for books due in {days_ahead} days")
    return count
