from typing import Dict
from src.domain.entities.user import User
from src.domain.entities.session import Session
from src.domain.entities.activity import Activity

users_db: Dict[int, User] = {}
sessions_db: Dict[str, Session] = {}
activities_db: Dict[str, Activity] = {}