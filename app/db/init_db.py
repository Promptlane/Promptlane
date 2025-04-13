import bcrypt
import uuid
import logging
from datetime import datetime, timedelta
from sqlalchemy import inspect

from app.db.models import Base, User, Team, TeamMember, Project, Prompt, Activity, ActivityType, TeamRole
from app.db.database import db
from app.managers.user_manager import UserManager
from app.managers.project_manager import ProjectManager
from app.managers.prompt_manager import PromptManager
from app.managers.activity_manager import ActivityManager
from typing import List, Dict, Any
import random

# Configure logging
logger = logging.getLogger(__name__)

def init_db(db=None):
    """Initialize the database with tables and demo data"""
    create_tables(db)
    populate_demo_data(db)

# Define init_database as an alias for init_db for backward compatibility
init_database = init_db

def create_admin_user(username: str, email: str, password: str) -> User:
    """Create an admin user"""
    logger.info(f"Creating admin user: {username}")
    try:
        user_manager = UserManager()
        
        # Check if user already exists
        user = user_manager.get_user_by_username(username)
        if user:
            logger.info(f"Admin user {username} already exists")
            # Ensure the user is an admin
            if not user.is_admin:
                user, error = user_manager.set_user_admin_status(user.id, True)
                if error:
                    logger.error(f"Failed to update admin status: {error}")
                    return None
                logger.info(f"Updated {username} to admin status")
            return user
        
        # Create a new admin user
        user, error = user_manager.create_user(username, email, password, is_admin=True)
        if error:
            logger.error(f"Failed to create admin user: {error}")
            return None
        
        logger.info(f"Admin user {username} created successfully")
        return user
    finally:
        pass

def create_tables(db=None):
    """Create tables in the database"""
    if db is None:
        db = db.get_session()
    
    inspector = inspect(db.connection())
    existing_tables = inspector.get_table_names()
    
    # Check if tables already exist
    if 'users' in existing_tables and 'projects' in existing_tables and 'prompts' in existing_tables and 'activities' in existing_tables:
        logger.info("Tables already exist, skipping creation")
        return
    
    # Create tables
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=db.connection())
    logger.info("Database tables created successfully")

def populate_demo_data(db=None):
    """Populate the database with demo data if it doesn't exist yet"""
        
    try:
        user_manager = UserManager()
        project_manager = ProjectManager()
        prompt_manager = PromptManager()
        
        # Set the database session for each manager
        user_manager._db = db
        project_manager._db = db
        prompt_manager._db = db
        
        # Check if demo data already exists
        user_count = len(user_manager.get_users())
        
        if user_count > 0:
            logger.info("Demo data already exists, skipping population")
            return
        
        logger.info("Populating database with demo data...")
        
        # Create demo users
        demo_users = []
        for i in range(1, 4):
            username = f"user{i}"
            try:
                user = user_manager.create_user(username, f"{username}@example.com", "password123")
                demo_users.append(user)
            except Exception as e:
                logger.error(f"Failed to create demo user {username}: {e}")
                continue
        
        # Create demo projects
        demo_projects = []
        project_names = ["AI Chatbot", "Content Generator", "Support Assistant"]
        project_descriptions = [
            "Conversational AI for customer interactions",
            "Generate marketing and social media content",
            "Help desk support automation"
        ]
        
        for i, user in enumerate(demo_users):
            project_key = project_names[i].lower().replace(" ", "_")
            project, error = project_manager.create_project(
                project_key=project_key,
                name=project_names[i],
                description=project_descriptions[i],
                created_by=user.id
            )
            if error:
                logger.error(f"Failed to create demo project {project_names[i]}: {error}")
                continue
            demo_projects.append(project)
        
        # Create demo prompts
        prompts_data = [
            {
                "name": "Welcome Message",
                "key": "welcome_message",
                "description": "A friendly welcome message for new users",
                "system_prompt": "You are a friendly AI assistant for our e-commerce store.",
                "user_prompt": "Greet the user and ask how you can help them with their shopping today. Keep it brief and friendly."
            },
            {
                "name": "Product Recommendation",
                "key": "product_recommendation",
                "description": "AI-powered product recommendations",
                "system_prompt": "You are a knowledgeable product recommendation assistant.",
                "user_prompt": "Ask the user about their preferences and recommend products based on {category} and {price_range}."
            },
            {
                "name": "Order Status",
                "key": "order_status",
                "description": "Order tracking and status updates",
                "system_prompt": "You are an order tracking assistant with access to order information.",
                "user_prompt": "Check the status of order number {order_id} and provide an update on its current status and estimated delivery date."
            }
        ]
        
        for project in demo_projects:
            for prompt_data in prompts_data:
                # Create a unique key by combining project key and prompt key
                unique_key = f"{project.key}_{prompt_data['key']}"
                prompt, error = prompt_manager.create_prompt(
                    prompt_key=unique_key,
                    name=prompt_data["name"],
                    description=prompt_data["description"],
                    system_prompt=prompt_data["system_prompt"],
                    user_prompt=prompt_data["user_prompt"],
                    project_id=project.id,
                    created_by=project.created_by
                )
                if error:
                    logger.error(f"Failed to create demo prompt {prompt_data['name']}: {error}")
                    continue
        
        # Create activity history for the past 30 days
        create_demo_activity_history(demo_users)
        
        logger.info("Demo data populated successfully")
    finally:
        pass

def create_demo_activity_history(users):
    """Create demo activity history for users"""
    logger.info("Creating demo activity history...")
    
    db_session = db.get_session()
    try:
        activity_manager = ActivityManager()
        activity_manager._db = db_session
        
        activity_types = [
            ActivityType.CREATE_USER,
            ActivityType.UPDATE_USER,
            ActivityType.CREATE_TEAM,
            ActivityType.UPDATE_TEAM,
            ActivityType.CREATE_PROJECT,
            ActivityType.UPDATE_PROJECT,
            ActivityType.CREATE_PROMPT,
            ActivityType.UPDATE_PROMPT,
            ActivityType.ADD_TEAM_MEMBER,
            ActivityType.UPDATE_TEAM_MEMBER_ROLE
        ]
        
        for user in users:
            # Create all activity types for each user
            for activity_type in activity_types:
                # Create activity with current timestamp
                activity_manager.create_activity(
                    user_id=user.id,
                    activity_type=activity_type,
                    details={"description": f"Demo activity of type {activity_type}"}
                )
        
        logger.info("Demo activity history created successfully")
    finally:
        db.close_session(db_session)

if __name__ == "__main__":
    init_db() 