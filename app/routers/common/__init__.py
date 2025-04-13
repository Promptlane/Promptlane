"""
Common routes package for shared endpoints and error handlers
"""
from fastapi import APIRouter
from .routes import router

__all__ = ['router'] 