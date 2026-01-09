from typing import Optional, List, Any
import uuid
import time
import asyncio
from boto3.dynamodb.conditions import Key, Attr
from app.models.models import Room
from app.utils.errors import NotFoundError, InvalidInputError, ConflictError


class RoomRepository:

    def __init__(self, dynamodb_client: Any, table_name: str) -> None:
        self.dynamodb: Any = dynamodb_client
        self.table: Any = dynamodb_client.Table(table_name)

    async def create(self, room: Room) -> None:
        if not room:
            raise InvalidInputError("Room is required")

        item = {
            "PK": "ROOM",
            "SK": f"ROOM#{room.id}",
            "LSI1": room.floor,
            "LSI2": room.capacity,
            "ID": room.id,
            "Name": room.name,
            "RoomNumber": room.room_number,
            "Capacity": room.capacity,
            "Floor": room.floor,
            "Amenities": room.amenities,
            "Status": room.status,
            "Location": room.location,
            "Description": room.description or "",
            "CreatedAt": room.created_at,
            "UpdatedAt": room.updated_at,
        }

        try:
            await asyncio.to_thread(
                self.table.put_item,
                Item=item,
                ConditionExpression="attribute_not_exists(PK) AND attribute_not_exists(SK)",
            )
        except self.dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
            raise ConflictError("Room already exists")

    async def get_all(self) -> List[Room]:
        response = await asyncio.to_thread(
            self.table.query, KeyConditionExpression=Key("PK").eq("ROOM")
        )

        if not response.get("Items"):
            return []

        rooms = []
        for item in response["Items"]:
            rooms.append(
                Room(
                    id=item["ID"],
                    name=item["Name"],
                    room_number=int(item["RoomNumber"]),
                    capacity=int(item["Capacity"]),
                    floor=int(item["Floor"]),
                    amenities=item.get("Amenities", []),
                    status=item["Status"],
                    location=item["Location"],
                    description=item.get("Description"),
                    created_at=int(item["CreatedAt"]),
                    updated_at=int(item["UpdatedAt"]),
                )
            )

        return rooms

    async def get_by_id(self, room_id: str) -> Optional[Room]:
        if not room_id:
            raise InvalidInputError("Room ID is required")

        response = await asyncio.to_thread(
            self.table.get_item, Key={"PK": "ROOM", "SK": f"ROOM#{room_id}"}
        )

        if "Item" not in response:
            raise NotFoundError("Room not found")

        item = response["Item"]
        return Room(
            id=item["ID"],
            name=item["Name"],
            room_number=int(item["RoomNumber"]),
            capacity=int(item["Capacity"]),
            floor=int(item["Floor"]),
            amenities=item.get("Amenities", []),
            status=item["Status"],
            location=item["Location"],
            description=item.get("Description"),
            created_at=int(item["CreatedAt"]),
            updated_at=int(item["UpdatedAt"]),
        )

    async def update(self, room: Room) -> None:
        if not room:
            raise InvalidInputError("Room is required")

        item = {
            "PK": "ROOM",
            "SK": f"ROOM#{room.id}",
            "LSI1": room.floor,
            "LSI2": room.capacity,
            "ID": room.id,
            "Name": room.name,
            "RoomNumber": room.room_number,
            "Capacity": room.capacity,
            "Floor": room.floor,
            "Amenities": room.amenities,
            "Status": room.status,
            "Location": room.location,
            "Description": room.description or "",
            "CreatedAt": room.created_at,
            "UpdatedAt": room.updated_at,
        }

        try:
            await asyncio.to_thread(
                self.table.put_item,
                Item=item,
                ConditionExpression="attribute_exists(PK) AND attribute_exists(SK)",
            )
        except self.dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
            raise NotFoundError("Room not found")

    async def delete_by_id(self, room_id: str) -> None:
        if not room_id:
            raise InvalidInputError("Room ID is required")

        try:
            await asyncio.to_thread(
                self.table.delete_item,
                Key={"PK": "ROOM", "SK": f"ROOM#{room_id}"},
                ConditionExpression="attribute_exists(PK) AND attribute_exists(SK)",
            )
        except self.dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
            raise NotFoundError("Room not found")

    async def update_availability(self, room_id: str, status: str) -> None:
        if not room_id:
            raise InvalidInputError("Room ID is required")

        try:
            await asyncio.to_thread(
                self.table.update_item,
                Key={"PK": "ROOM", "SK": f"ROOM#{room_id}"},
                UpdateExpression="SET #status = :status, UpdatedAt = :updated_at",
                ExpressionAttributeNames={"#status": "Status"},
                ExpressionAttributeValues={
                    ":status": status,
                    ":updated_at": int(time.time()),
                },
                ConditionExpression="attribute_exists(PK) AND attribute_exists(SK)",
            )
        except self.dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
            raise NotFoundError("Room not found")

    async def check_room_number_exists_on_floor(
        self, room_number: int, floor: int
    ) -> bool:
        try:
            response = await asyncio.to_thread(
                self.table.query,
                KeyConditionExpression=Key("PK").eq("ROOM"),
                FilterExpression=Attr("RoomNumber").eq(room_number)
                & Attr("Floor").eq(floor),
            )
            return len(response.get("Items", [])) > 0
        except Exception:
            return False
