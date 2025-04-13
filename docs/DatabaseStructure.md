# Database Structure

This document outlines the database schema for PromptLane, including tables, relationships, and indexes.

## Overview

PromptLane uses PostgreSQL as the primary database with SQLAlchemy ORM. The database schema is defined in `app/db/models/` and migrations are managed with Alembic.

## Entity Relationship Diagram

```
+----------------+       +----------------+       +----------------+
|     User       |       |     Team       |       |    Project     |
+----------------+       +----------------+       +----------------+
| id             |<----->| id             |       | id             |
| username       |       | name           |<----->| name           |
| email          |       | description    |       | description    |
| hashed_password|       | created_by     |       | created_by     |
| full_name      |       | created_at     |       | updated_by     |
| is_active      |       | updated_at     |       | created_at     |
| is_admin       |       +----------------+       | updated_at     |
| status         |               ^                | team_id        |
| invitation_token|              |                +----------------+
| invitation_expiry|             |                        ^
+----------------+               |                        |
        ^                        |                        |
        |                        |                        |
        |                +----------------+               |
        |                |  TeamMember    |               |
        +--------------->| id             |               |
        |                | team_id        |               |
        |                | user_id        |               |
        |                | role           |               |
        |                | status         |               |
        |                +----------------+               |
        |                                                 |
+----------------+                               +----------------+
|    Activity    |                               |     Prompt     |
+----------------+                               +----------------+
| id             |                               | id             |
| user_id        |                               | key            |
| activity_type  |                               | name           |
| timestamp      |                               | version        |
| details        |                               | system_prompt  |
+----------------+                               | user_prompt    |
                                                 | is_active      |
                                                 | created_by     |
                                                 | updated_by     |
                                                 | created_at     |
                                                 | updated_at     |
                                                 | project_id     |
                                                 | parent_id      |
                                                 +----------------+
```

## Tables

### Base Model

All models inherit from `BaseModel` which provides common fields:

| Column           | Type           | Description                            |
|------------------|----------------|----------------------------------------|
| id               | UUID           | Primary key (auto-generated)           |
| created_at       | DateTime       | Creation timestamp (auto-set)          |
| updated_at       | DateTime       | Last update timestamp (auto-updated)   |
| created_by       | UUID           | Foreign key to creator User            |
| updated_by       | UUID           | Foreign key to updater User            |

Relationships:
- Many-to-one with User (`creator`) for created_by
- Many-to-one with User (`updater`) for updated_by

### User

Stores user account information.

| Column           | Type           | Description                            |
|------------------|----------------|----------------------------------------|
| username         | String(50)     | Unique username                        |
| email            | String(255)    | Unique email address                   |
| hashed_password  | String(255)    | Securely hashed password               |
| full_name        | String(100)    | User's full name (nullable)            |
| is_active        | Boolean        | Account status (default: True)         |
| is_admin         | Boolean        | Admin status (default: False)          |
| status           | Enum           | User status (active/invited/disabled)  |
| invitation_token | String(255)    | Unique invitation token               |
| invitation_expiry| DateTime       | Invitation expiry time                |

Relationships:
- One-to-many with Project (`projects`)
- One-to-many with TeamMember (`team_memberships`)
- One-to-many with Activity (`activities`)

Indexes:
- Primary key on `id`
- Unique index on `username`
- Unique index on `email`
- Index on `status`

### Project

Organizes collections of prompts.

| Column           | Type           | Description                            |
|------------------|----------------|----------------------------------------|
| name             | String(100)    | Project name                           |
| key              | String(50)     | Unique project identifier              |
| description      | String(500)    | Project description                    |
| team_id          | UUID           | Foreign key to Team                    |

Relationships:
- Many-to-one with Team (`team`)
- One-to-many with Prompt (`prompts`)
- Many-to-one with User (`owner`) through created_by
- Cascade delete for prompts

Indexes:
- Primary key on `id`
- Unique index on `key`
- Index on `team_id`

### Prompt

Stores prompt templates with versioning support.

| Column           | Type           | Description                            |
|------------------|----------------|----------------------------------------|
| name             | String(100)    | Prompt name                            |
| key              | String(50)     | Unique prompt identifier               |
| description      | String(500)    | Prompt description                     |
| system_prompt    | Text           | System instructions                    |
| user_prompt      | Text           | User-facing prompt template            |
| is_active        | Boolean        | Active status (default: True)          |
| version          | Integer        | Version number (default: 1)            |
| project_id       | UUID           | Foreign key to Project                 |
| parent_id        | UUID           | Self-reference for versions            |

Relationships:
- Many-to-one with Project (`project`)
- Self-referential for versions (`parent` and `versions`)
- Cascade delete with project

Indexes:
- Primary key on `id`
- Unique index on `key`
- Index on `project_id`
- Index on `parent_id`

### Team

Represents a group of users collaborating on projects.

| Column           | Type           | Description                            |
|------------------|----------------|----------------------------------------|
| name             | String(100)    | Team name                              |
| description      | String(500)    | Team description                       |

Relationships:
- One-to-many with TeamMember (`members`)
- One-to-many with Project (`projects`)
- Cascade delete for members and projects

Indexes:
- Primary key on `id`
- Index on `created_by`

### TeamMember

Manages user membership in teams.

| Column           | Type           | Description                            |
|------------------|----------------|----------------------------------------|
| team_id          | UUID           | Foreign key to Team                    |
| user_id          | UUID           | Foreign key to User                    |
| role             | Enum           | TeamRole (owner/admin/editor/viewer)   |
| status           | Enum           | MemberStatus (active/pending/inactive) |

Relationships:
- Many-to-one with Team (`team`)
- Many-to-one with User (`user`)
- Cascade delete with team

Indexes:
- Primary key on `id`
- Unique composite index on `team_id` and `user_id`
- Index on `user_id`

### Activity

Tracks user activities for analytics and history.

| Column           | Type           | Description                            |
|------------------|----------------|----------------------------------------|
| id               | UUID           | Primary key (auto-generated)           |
| user_id          | UUID           | Foreign key to User                    |
| activity_type    | String         | Type of activity                       |
| timestamp        | DateTime       | Activity timestamp (auto-set)          |
| details          | JSONB          | Additional activity details            |

Indexes:
- Primary key on `id`
- Index on `user_id`
- Index on `timestamp`

Relationships:
- Many-to-one with User (`user`)

## Enumeration Types

### TeamRole
```python
class TeamRole(Enum):
    OWNER = "owner"     # Full access
    ADMIN = "admin"     # Project and prompt management
    EDITOR = "editor"   # Edit access, no management
    VIEWER = "viewer"   # Read-only access
```

### MemberStatus
- `active`: Active team member
- `pending`: Pending invitation
- `inactive`: Inactive member

### UserStatus
- `active`: Active user
- `invited`: Pending invitation
- `disabled`: Disabled account

### ActivityType
Types of actions tracked:
- `login`: User logged in
- `logout`: User logged out
- `register`: User registered
- `update_user`: User updated their profile
- `create_user`: Admin created a user
- `create_project`: User created a project
- `update_project`: User updated a project
- `delete_project`: User deleted a project
- `create_prompt`: User created a prompt
- `update_prompt`: User updated a prompt
- `delete_prompt`: User deleted a prompt
- `create_prompt_version`: User created a new prompt version
- `execute_prompt`: User executed a prompt
- `view_dashboard`: User viewed dashboard
- `view_project`: User viewed a project
- `view_prompt`: User viewed a prompt
- `view_teams`: User viewed teams list
- `view_team`: User viewed a team
- `create_team`: User created a team
- `update_team`: User updated team details
- `delete_team`: User deleted a team
- `add_team_member`: User added a member to a team
- `remove_team_member`: User removed a member from a team
- `update_team_member_role`: User updated a member's role
- `add_project_to_team`: User added a project to a team

## Database Migrations

Database migrations are managed with Alembic:

1. Migrations are stored in `alembic/versions/`
2. New migrations can be generated with:
   ```bash
   alembic revision --autogenerate -m "Description of changes"
   ```
3. Apply migrations with:
   ```bash
   alembic upgrade head
   ```

## Best Practices

When working with the database:

1. Always use SQLAlchemy ORM for database operations
2. Use transactions when performing multiple related operations
3. Handle database errors gracefully
4. Create database indexes for frequently queried columns
5. Implement proper validation before writing to the database
6. Use foreign keys to maintain data integrity
7. Document any schema changes in commit messages

## Schema Evolution

When making changes to the database schema:

1. Add new tables or columns rather than modifying existing ones when possible
2. Write migrations that both upgrade and downgrade cleanly
3. Test migrations on a copy of production data before deploying
4. Consider backward compatibility for API consumers

## Example Usage

### Creating a New User

```python
from app.db.models import User
from sqlalchemy.orm import Session
import uuid

def create_user(db: Session, username: str, email: str, hashed_password: str):
    user = User(
        id=uuid.uuid4(),
        username=username,
        email=email,
        hashed_password=hashed_password
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
```

### Querying Related Data

```python
from app.db.models import Project, Prompt
from sqlalchemy.orm import Session

def get_project_with_prompts(db: Session, project_id: uuid.UUID):
    return db.query(Project).filter(Project.id == project_id).options(
        sqlalchemy.orm.joinedload(Project.prompts)
    ).first()
``` 