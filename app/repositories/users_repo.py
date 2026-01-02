from typing import Optional, List
from app.models.models import User


class UserRepository:

    def __init__(self, dynamodb_client, table_name: str):
        pass

    def find_user_id_by_email(self, email: str) -> Optional[str]:
        pass

    def find_by_email(self, email: str) -> Optional[User]:
        pass

    def get_by_id(self, user_id: str) -> Optional[User]:
        pass

    def create(self, user: User) -> None:
        pass

    def get_all(self) -> List[User]:
        pass

    def delete_by_id(self, user_id: str) -> None:
        pass
