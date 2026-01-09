from typing import List, Any
import uuid
import time
import asyncio
from boto3.dynamodb.conditions import Key, Attr
from app.models.models import Booking
from app.utils.errors import NotFoundError


class BookingRepository:

    def __init__(self, dynamodb_client: Any, table_name: str) -> None:
        self.dynamodb: Any = dynamodb_client
        self.table: Any = dynamodb_client.Table(table_name)

    async def create(self, booking: Booking) -> None:
        item = {
            "PK": "BOOKING",
            "SK": f"BOOKING#{booking.id}",
            "UserID": booking.user_id,
            "UserName": booking.user_name,
            "RoomID": booking.room_id,
            "RoomNumber": booking.room_number,
            "Date": (booking.start_time // 86400) * 86400,
            "ID": booking.id,
            "StartTime": booking.start_time,
            "EndTime": booking.end_time,
            "Purpose": booking.purpose,
            "Status": booking.status,
            "CreatedAt": booking.created_at,
            "UpdatedAt": booking.updated_at,
        }

        await asyncio.to_thread(self.table.put_item, Item=item)

    async def get_by_id(self, booking_id: str) -> Booking:
        response = await asyncio.to_thread(
            self.table.get_item,
            Key={"PK": "BOOKING", "SK": f"BOOKING#{booking_id}"},
        )

        if "Item" not in response:
            raise NotFoundError("Booking not found")

        item = response["Item"]
        return Booking(
            id=item["ID"],
            user_id=item["UserID"],
            user_name=item["UserName"],
            room_id=item["RoomID"],
            room_number=int(item["RoomNumber"]),
            start_time=int(item["StartTime"]),
            end_time=int(item["EndTime"]),
            purpose=item["Purpose"],
            status=item["Status"],
            created_at=int(item["CreatedAt"]),
            updated_at=int(item["UpdatedAt"]),
        )

    async def get_all(self) -> List[Booking]:
        response = await asyncio.to_thread(
            self.table.query, KeyConditionExpression=Key("PK").eq("BOOKING")
        )
        return self._unmarshal_bookings(response.get("Items", []))

    async def get_by_room_and_time(
        self, room_id: str, start_time: int, end_time: int
    ) -> List[Booking]:
        response = await asyncio.to_thread(
            self.table.query,
            IndexName="RoomIDIndex",
            KeyConditionExpression=Key("PK").eq("BOOKING") & Key("RoomID").eq(room_id),
            FilterExpression=Attr("EndTime").gt(start_time)
            & Attr("StartTime").lt(end_time),
        )
        return self._unmarshal_bookings(response.get("Items", []))

    async def get_by_room_id(self, room_id: str) -> List[Booking]:
        response = await asyncio.to_thread(
            self.table.query,
            IndexName="RoomIDIndex",
            KeyConditionExpression=Key("PK").eq("BOOKING") & Key("RoomID").eq(room_id),
        )
        return self._unmarshal_bookings(response.get("Items", []))

    async def get_by_user_id(self, user_id: str) -> List[Booking]:
        response = await asyncio.to_thread(
            self.table.query,
            IndexName="UserIDIndex",
            KeyConditionExpression=Key("PK").eq("BOOKING") & Key("UserID").eq(user_id),
        )
        return self._unmarshal_bookings(response.get("Items", []))

    async def cancel(self, booking_id: str) -> None:
        try:
            await asyncio.to_thread(
                self.table.delete_item,
                Key={"PK": "BOOKING", "SK": f"BOOKING#{booking_id}"},
                ConditionExpression="attribute_exists(PK) AND attribute_exists(SK)",
            )
        except self.dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
            raise NotFoundError("Booking not found")

    async def delete_by_user_id(self, user_id: str) -> int:
        response = await asyncio.to_thread(
            self.table.query,
            IndexName="UserIDIndex",
            KeyConditionExpression=Key("PK").eq("BOOKING") & Key("UserID").eq(user_id),
            ProjectionExpression="SK",
        )

        items = response.get("Items", [])
        if not items:
            return 0

        deleted_count = 0
        chunk_size = 25

        for i in range(0, len(items), chunk_size):
            chunk = items[i : i + chunk_size]
            delete_requests = [
                {"DeleteRequest": {"Key": {"PK": "BOOKING", "SK": item["SK"]}}}
                for item in chunk
            ]

            await asyncio.to_thread(
                self.dynamodb.meta.client.batch_write_item,
                RequestItems={self.table.name: delete_requests},
            )
            deleted_count += len(chunk)

        return deleted_count

    async def get_by_date_range(self, start_date: int, end_date: int) -> List[Booking]:
        response = await asyncio.to_thread(
            self.table.query,
            IndexName="DateIndex",
            KeyConditionExpression=Key("PK").eq("BOOKING")
            & Key("Date").between(start_date, end_date),
        )
        return self._unmarshal_bookings(response.get("Items", []))

    async def get_by_room_id_and_date(self, room_id: str, date: int) -> List[Booking]:
        start_of_day = (date // 86400) * 86400
        end_of_day = start_of_day + 86400

        response = await asyncio.to_thread(
            self.table.query,
            IndexName="RoomIDIndex",
            KeyConditionExpression=Key("PK").eq("BOOKING") & Key("RoomID").eq(room_id),
            FilterExpression=Attr("EndTime").gt(start_of_day)
            & Attr("StartTime").lt(end_of_day),
        )
        return self._unmarshal_bookings(response.get("Items", []))

    def _unmarshal_bookings(self, items: List[dict]) -> List[Booking]:
        if not items:
            return []

        bookings = []
        for item in items:
            bookings.append(
                Booking(
                    id=item["ID"],
                    user_id=item["UserID"],
                    user_name=item["UserName"],
                    room_id=item["RoomID"],
                    room_number=int(item["RoomNumber"]),
                    start_time=int(item["StartTime"]),
                    end_time=int(item["EndTime"]),
                    purpose=item["Purpose"],
                    status=item["Status"],
                    created_at=int(item["CreatedAt"]),
                    updated_at=int(item["UpdatedAt"]),
                )
            )

        return bookings
