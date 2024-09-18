from dataclasses import dataclass
from backend_client import AbstractAPIClient
from src.services.auth_service import AbstractAuthService
from src.services.notes_service import AbstractNotesService

@dataclass
class NaiveSimpleDIContainer:
    api_client: AbstractAPIClient
    auth_service: AbstractAuthService
    notes_service: AbstractNotesService