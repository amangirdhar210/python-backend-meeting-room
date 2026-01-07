from typing import Optional, List, Any
import uuid
import time
from boto3.dynamodb.conditions import Key, Attr
from app.models.models import Room
from app.utils.errors import NotFoundError, InvalidInputError, ConflictError


class RoomRepository:

    def __init__(self, dynamodb_client: Any, table_name: str) -> None:
        self.dynamodb: Any = dynamodb_client
        self.table: Any = dynamodb_client.Table(table_name)

    def create(self, room: Room) -> None:
        if not room:
            raise InvalidInputError("Room is required")

        try:
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

            self.table.put_item(
                Item=item,
                ConditionExpression="attribute_not_exists(PK) AND attribute_not_exists(SK)",
            )
        except self.dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
            raise ConflictError("Room already exists")
        except Exception as e:
            raise Exception(f"Failed to create room: {str(e)}")

    def get_all(self) -> List[Room]:
        try:
            response = self.table.query(KeyConditionExpression=Key("PK").eq("ROOM"))

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
        except Exception as e:
            raise Exception(f"Failed to get all rooms: {str(e)}")

    def get_by_id(self, room_id: str) -> Optional[Room]:
        if not room_id:
            raise InvalidInputError("Room ID is required")

        try:
            response = self.table.get_item(Key={"PK": "ROOM", "SK": f"ROOM#{room_id}"})

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
        except Exception as e:
            if isinstance(e, (NotFoundError, InvalidInputError)):
                raise
            raise Exception(f"Failed to get room by ID: {str(e)}")

    def delete_by_id(self, room_id: str) -> None:
        if not room_id:
            raise InvalidInputError("Room ID is required")

        try:
            self.table.delete_item(
                Key={"PK": "ROOM", "SK": f"ROOM#{room_id}"},
                ConditionExpression="attribute_exists(PK) AND attribute_exists(SK)",
            )
        except self.dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
            raise NotFoundError("Room not found")
        except Exception as e:
            raise Exception(f"Failed to delete room: {str(e)}")

    def update_availability(self, room_id: str, status: str) -> None:
        if not room_id:
            raise InvalidInputError("Room ID is required")

        try:
            self.table.update_item(
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
        except Exception as e:
            raise Exception(f"Failed to update room availability: {str(e)}")

    def search_with_filters(
        self, min_capacity: int, max_capacity: int, floor: Optional[int]
    ) -> List[Room]:
        try:
            if floor is not None:
                response = self.table.query(
                    IndexName="LSI-1",
                    KeyConditionExpression=Key("PK").eq("ROOM") & Key("LSI1").eq(floor),
                )

                items = response.get("Items", [])

                if min_capacity > 0 or max_capacity > 0:
                    filtered_items = []
                    for item in items:
                        capacity = int(item.get("LSI2", 0))
                        if min_capacity > 0 and capacity < min_capacity:
                            continue
                        if max_capacity > 0 and capacity > max_capacity:
                            continue
                        filtered_items.append(item)
                    items = filtered_items

            elif min_capacity > 0 or max_capacity > 0:
                if min_capacity > 0 and max_capacity > 0:
                    response = self.table.query(
                        IndexName="LSI-2",
                        KeyConditionExpression=Key("PK").eq("ROOM")
                        & Key("LSI2").between(min_capacity, max_capacity),
                    )
                elif min_capacity > 0:
                    response = self.table.query(
                        IndexName="LSI-2",
                        KeyConditionExpression=Key("PK").eq("ROOM")
                        & Key("LSI2").gte(min_capacity),
                    )
                else:
                    response = self.table.query(
                        IndexName="LSI-2",
                        KeyConditionExpression=Key("PK").eq("ROOM")
                        & Key("LSI2").lte(max_capacity),
                    )

                items = response.get("Items", [])
            else:
                response = self.table.query(KeyConditionExpression=Key("PK").eq("ROOM"))
                items = response.get("Items", [])

            rooms = []
            for item in items:
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
        except Exception as e:
            raise Exception(f"Failed to search rooms: {str(e)}")

    def check_room_number_exists_on_floor(self, room_number: int, floor: int) -> bool:
        try:
            response = self.table.query(
                IndexName="LSI-1",
                KeyConditionExpression=Key("PK").eq("ROOM") & Key("LSI1").eq(floor),
                FilterExpression=Attr("RoomNumber").eq(room_number),
            )

            return len(response.get("Items", [])) > 0
        except Exception:
            return False
