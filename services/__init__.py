"""
Services package for LinkFarm backend
Contains business logic and external service integrations
"""
from .email_service import send_inquiry_notification, send_welcome_email

__all__ = ['send_inquiry_notification', 'send_welcome_email']
