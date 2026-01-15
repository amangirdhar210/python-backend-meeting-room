from typing import Optional, List, Any
import boto3
import asyncio
from boto3.dynamodb.conditions import Key
from app.models.models import User
from app.utils.errors import ApplicationError, ErrorCode
import time


class UserRepository:
    def __init__(self, dynamodb_client: Any, table_name: str) -> None:
        self.dynamodb: Any = dynamodb_client
        self.table: Any = dynamodb_client.Table(table_name)

    async def find_user_id_by_email(self, email: str) -> str:
        response = await asyncio.to_thread(
            self.table.query,
            KeyConditionExpression=Key("PK").eq("USER") & Key("SK").eq(email),
        )

        if not response.get("Items"):
            raise ApplicationError(ErrorCode.USER_NOT_FOUND)

        user_id = response["Items"][0].get("ID")
        return str(user_id) if user_id else ""

    async def find_by_email(self, email: str) -> User:
        user_id: str = await self.find_user_id_by_email(email)
        return await self.get_by_id(user_id)

    async def get_by_id(self, user_id: str) -> User:
        response = await asyncio.to_thread(
            self.table.query,
            KeyConditionExpression=Key("PK").eq("USER")
            & Key("SK").eq(f"USER#{user_id}"),
        )

        if not response.get("Items"):
            raise ApplicationError(ErrorCode.USER_NOT_FOUND)

        item = response["Items"][0]
        return User(
            id=item["ID"],
            name=item["Name"],
            email=item["Email"],
            password=item["Password"],
            role=item["Role"],
            created_at=int(item["CreatedAt"]),
            updated_at=int(item["UpdatedAt"]),
        )

    async def create(self, user: User) -> None:
        await asyncio.to_thread(
            self.table.meta.client.transact_write_items,
            TransactItems=[
                {
                    "Put": {
                        "TableName": self.table.table_name,
                        "Item": {"PK": "USER", "SK": user.email, "ID": user.id},
                    }
                },
                {
                    "Put": {
                        "TableName": self.table.table_name,
                        "Item": {
                            "PK": "USER",
                            "SK": f"USER#{user.id}",
                            "ID": user.id,
                            "Name": user.name,
                            "Email": user.email,
                            "Password": user.password,
                            "Role": user.role,
                            "CreatedAt": user.created_at,
                            "UpdatedAt": user.updated_at,
                        },
                    }
                },
            ],
        )

    async def get_all(self) -> List[User]:
        response = await asyncio.to_thread(
            self.table.query,
            KeyConditionExpression=Key("PK").eq("USER")
            & Key("SK").begins_with("USER#"),
        )

        if not response.get("Items"):
            return []

        users = []
        for item in response["Items"]:
            users.append(
                User(
                    id=item["ID"],
                    name=item["Name"],
                    email=item["Email"],
                    password=item["Password"],
                    role=item["Role"],
                    created_at=int(item["CreatedAt"]),
                    updated_at=int(item["UpdatedAt"]),
                )
            )

        return users

    async def update(self, user: User, old_email: Optional[str] = None) -> None:
        transact_items = []

        if old_email and old_email != user.email:
            transact_items.append(
                {
                    "Delete": {
                        "TableName": self.table.table_name,
                        "Key": {"PK": "USER", "SK": old_email},
                    }
                }
            )
            transact_items.append(
                {
                    "Put": {
                        "TableName": self.table.table_name,
                        "Item": {"PK": "USER", "SK": user.email, "ID": user.id},
                    }
                }
            )

        transact_items.append(
            {
                "Put": {
                    "TableName": self.table.table_name,
                    "Item": {
                        "PK": "USER",
                        "SK": f"USER#{user.id}",
                        "ID": user.id,
                        "Name": user.name,
                        "Email": user.email,
                        "Password": user.password,
                        "Role": user.role,
                        "CreatedAt": user.created_at,
                        "UpdatedAt": user.updated_at,
                    },
                }
            }
        )

        await asyncio.to_thread(
            self.table.meta.client.transact_write_items,
            TransactItems=transact_items,
        )

    async def delete_by_id(self, user_id: str) -> None:
        user = await self.get_by_id(user_id)

        await asyncio.to_thread(
            self.table.meta.client.transact_write_items,
            TransactItems=[
                {
                    "Delete": {
                        "TableName": self.table.table_name,
                        "Key": {"PK": "USER", "SK": user.email},
                    }
                },
                {
                    "Delete": {
                        "TableName": self.table.table_name,
                        "Key": {"PK": "USER", "SK": f"USER#{user_id}"},
                    }
                },
            ],
        )
