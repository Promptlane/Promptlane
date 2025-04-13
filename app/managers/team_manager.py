"""
Team management operations and business logic
"""
from sqlalchemy.orm import Session
import uuid
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
from app.db import models
from app.models.team import TeamRole
from app.exceptions import TeamCreationError, TeamNotFoundError, TeamUpdateError
from app.db.database import db
from app.managers.base_manager import BaseManager
import logging

logger = logging.getLogger(__name__)

class TeamManager(BaseManager):
    """Manager class for handling team-related operations"""
    
    def __init__(self, db_session: Optional[Session] = None):
        super().__init__(models.Team, db_session)

    def get_team(self, team_id: uuid.UUID) -> Optional[models.Team]:
        """Get a team by ID"""
        return self.get(team_id)

    def get_team_by_name(self, name: str) -> Optional[models.Team]:
        """Get a team by name"""
        return self.get_by_field('name', name)

    def get_team_by_key(self, key: str) -> Optional[models.Team]:
        """Get a team by key"""
        return self.get_by_field('key', key)

    def get_all_teams(self, skip: int = 0, limit: int = 100) -> List[models.Team]:
        """Get all teams with pagination"""
        return self.get_multi(skip=skip, limit=limit)

    def has_team_access(
        self,
        team_id: uuid.UUID,
        user_id: uuid.UUID,
        required_role: Optional[TeamRole] = None
    ) -> bool:
        """Check if a user has access to a team with optional role requirement"""
        try:
            # Get the team
            team = self.get_team(team_id)
            if not team:
                return False
            
            # Team creator has full access
            if team.created_by == user_id:
                return True
            
            # Get the user's role in the team
            team_member = self._db.query(models.TeamMember).filter(
                models.TeamMember.team_id == team_id,
                models.TeamMember.user_id == user_id
            ).first()
            
            if not team_member:
                return False
            
            # If no specific role required, any membership is sufficient
            if required_role is None:
                return True
            
            # Check if user's role meets the requirement
            role_hierarchy = {
                TeamRole.VIEWER: 0,
                TeamRole.EDITOR: 1,
                TeamRole.ADMIN: 2,
                TeamRole.OWNER: 3
            }
            
            return role_hierarchy[team_member.role] >= role_hierarchy[required_role]
            
        except Exception as e:
            raise TeamCreationError(f"Failed to check team access: {str(e)}")

    def get_team_project_count(self, team_id: uuid.UUID) -> int:
        """Get the number of projects in a team"""
        try:
            return self._db.query(models.Project).filter(
                models.Project.team_id == team_id
            ).count()
        except Exception as e:
            raise TeamCreationError(f"Failed to get team project count: {str(e)}")

    def create_team(
        self,
        name: str,
        description: str,
        created_by: uuid.UUID
    ) -> Tuple[Optional[models.Team], str]:
        """Create a new team"""
        try:
            # Check if team name already exists
            existing_team = self.get_team_by_key(name.lower().replace(" ", "-"))
            if existing_team:
                return None, "Team name already exists"

            # Create team
            team = self.create({
                'id': str(uuid.uuid4()),
                'name': name,
                'key': name.lower().replace(" ", "-"),
                'description': description,
                'created_by': created_by,
                'created_at': datetime.utcnow()
            })

            if not team:
                return None, "Failed to create team"

            # Add creator as team member
            self._add_team_member(team.id, created_by, models.TeamRole.ADMIN)

            # Log activity
            self._log_activity(created_by, models.ActivityType.CREATE_TEAM, {
                "team_id": team.id,
                "name": name
            })

            return team, ""
        except Exception as e:
            logger.error(f"Error creating team: {str(e)}")
            return None, str(e)

    def update_team(
        self,
        team_id: uuid.UUID,
        name: Optional[str] = None,
        description: Optional[str] = None,
        updated_by: Optional[uuid.UUID] = None
    ) -> Tuple[Optional[models.Team], str]:
        """Update a team"""
        try:
            team = self.get_team(team_id)
            if not team:
                return None, "Team not found"

            # Update fields
            update_data = {}
            if name is not None:
                update_data['name'] = name
                update_data['key'] = name.lower().replace(" ", "-")
            if description is not None:
                update_data['description'] = description
            if updated_by is not None:
                update_data['updated_by'] = updated_by
                update_data['updated_at'] = datetime.utcnow()

            updated_team = self.update(team, update_data)
            if not updated_team:
                return None, "Failed to update team"

            # Log activity
            self._log_activity(updated_by or team.created_by, models.ActivityType.UPDATE_TEAM, {
                "team_id": team_id,
                "updated_fields": [k for k, v in update_data.items() if v is not None]
            })

            return updated_team, ""
        except Exception as e:
            logger.error(f"Error updating team: {str(e)}")
            return None, str(e)

    def delete_team(self, team_id: uuid.UUID) -> bool:
        """Delete a team"""
        try:
            team = self.get_team(team_id)
            if not team:
                return False

            success = self.delete(team_id)
            if not success:
                return False

            # Log activity
            self._log_activity(team.created_by, models.ActivityType.DELETE_TEAM, {
                "team_id": team_id,
                "name": team.name
            })

            return True
        except Exception as e:
            logger.error(f"Error deleting team: {str(e)}")
            return False

    def get_user_teams(self, user_id: uuid.UUID) -> List[models.Team]:
        """Get all teams a user is a member of"""
        try:
            return self._db.query(models.Team).join(
                models.TeamMember
            ).filter(
                models.TeamMember.user_id == user_id
            ).all()
        except Exception as e:
            logger.error(f"Error getting user teams: {str(e)}")
            return []

    def get_team_members(self, team_id: uuid.UUID) -> List[models.TeamMember]:
        """Get all members of a team"""
        try:
            return self._db.query(models.TeamMember).filter(
                models.TeamMember.team_id == team_id
            ).all()
        except Exception as e:
            logger.error(f"Error getting team members: {str(e)}")
            return []

    def add_team_member(
        self,
        team_id: uuid.UUID,
        user_id: uuid.UUID,
        role: models.TeamRole = models.TeamRole.MEMBER
    ) -> bool:
        """Add a user to a team"""
        try:
            # Check if user is already a member
            existing_member = self._db.query(models.TeamMember).filter(
                models.TeamMember.team_id == team_id,
                models.TeamMember.user_id == user_id
            ).first()
            
            if existing_member:
                return False

            # Add member
            member = models.TeamMember(
                id=str(uuid.uuid4()),
                team_id=team_id,
                user_id=user_id,
                role=role,
                joined_at=datetime.utcnow()
            )
            
            self._db.add(member)
            self._db.commit()

            # Log activity
            self._log_activity(user_id, models.ActivityType.ADD_TEAM_MEMBER, {
                "team_id": team_id,
                "user_id": user_id,
                "role": role.value
            })

            return True
        except Exception as e:
            logger.error(f"Error adding team member: {str(e)}")
            self._db.rollback()
            return False

    def remove_team_member(self, team_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """Remove a user from a team"""
        try:
            member = self._db.query(models.TeamMember).filter(
                models.TeamMember.team_id == team_id,
                models.TeamMember.user_id == user_id
            ).first()
            
            if not member:
                return False

            self._db.delete(member)
            self._db.commit()

            # Log activity
            self._log_activity(user_id, models.ActivityType.REMOVE_TEAM_MEMBER, {
                "team_id": team_id,
                "user_id": user_id
            })

            return True
        except Exception as e:
            logger.error(f"Error removing team member: {str(e)}")
            self._db.rollback()
            return False

    def update_team_member_role(
        self,
        team_id: uuid.UUID,
        user_id: uuid.UUID,
        role: models.TeamRole
    ) -> bool:
        """Update a team member's role"""
        try:
            member = self._db.query(models.TeamMember).filter(
                models.TeamMember.team_id == team_id,
                models.TeamMember.user_id == user_id
            ).first()
            
            if not member:
                return False

            member.role = role
            self._db.commit()

            # Log activity
            self._log_activity(user_id, models.ActivityType.UPDATE_TEAM_MEMBER_ROLE, {
                "team_id": team_id,
                "user_id": user_id,
                "new_role": role.value
            })

            return True
        except Exception as e:
            logger.error(f"Error updating team member role: {str(e)}")
            self._db.rollback()
            return False

    def check_team_permissions(
        self,
        team_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Check user permissions for a team"""
        try:
            member = self._db.query(models.TeamMember).filter(
                models.TeamMember.team_id == team_id,
                models.TeamMember.user_id == user_id
            ).first()

            if not member:
                return {"has_access": False, "is_admin": False}

            return {
                "has_access": True,
                "is_admin": member.role == models.TeamRole.ADMIN
            }
        except Exception as e:
            logger.error(f"Error checking team permissions: {str(e)}")
            return {"has_access": False, "is_admin": False}

    def _add_team_member(
        self,
        team_id: uuid.UUID,
        user_id: uuid.UUID,
        role: models.TeamRole
    ) -> bool:
        """Internal method to add a team member without logging"""
        try:
            member = models.TeamMember(
                id=str(uuid.uuid4()),
                team_id=team_id,
                user_id=user_id,
                role=role,
                joined_at=datetime.utcnow()
            )
            
            self._db.add(member)
            self._db.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding team member: {str(e)}")
            self._db.rollback()
            return False

    def _log_activity(self, user_id: uuid.UUID, activity_type: models.ActivityType, details: Dict[str, Any]):
        """Log team activity"""
        try:
            activity = models.Activity(
                id=str(uuid.uuid4()),
                user_id=user_id,
                activity_type=activity_type,
                details=details,
                created_at=datetime.utcnow()
            )
            self._db.add(activity)
            self._db.commit()
        except Exception as e:
            logger.error(f"Error logging activity: {str(e)}")
            self._db.rollback()

    def create_project(
        self,
        team_id: uuid.UUID,
        user_id: uuid.UUID,
        name: str,
        description: Optional[str] = None
    ) -> models.Project:
        """Create a new project in a team"""
        try:
            # Create project
            project = models.Project(
                id=uuid.uuid4(),
                name=name,
                description=description,
                team_id=team_id,
                created_by=user_id,
                updated_by=user_id
            )
            
            # Add to database
            self._db.add(project)
            self._db.commit()
            self._db.refresh(project)
            
            return project
        except Exception as e:
            self._db.rollback()
            raise TeamCreationError(f"Failed to create project: {str(e)}") 