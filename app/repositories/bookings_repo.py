from typing import List, Any
import uuid
import time
from boto3.dynamodb.conditions import Key, Attr
from app.models.models import Booking
from app.utils.errors import NotFoundError


class BookingRepository:

    def __init__(self, dynamodb_client: Any, table_name: str) -> None:
        self.dynamodb: Any = dynamodb_client
        self.table: Any = dynamodb_client.Table(table_name)

    def create(self, booking: Booking) -> None:
        try:
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

            self.table.put_item(Item=item)
        except Exception as e:
            raise Exception(f"Failed to create booking: {str(e)}")

    def get_by_id(self, booking_id: str) -> Booking:
        try:
            response = self.table.get_item(
                Key={"PK": "BOOKING", "SK": f"BOOKING#{booking_id}"}
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
        except Exception as e:
            if isinstance(e, NotFoundError):
                raise
            raise Exception(f"Failed to get booking: {str(e)}")

    def get_all(self) -> List[Booking]:
        try:
            response = self.table.query(KeyConditionExpression=Key("PK").eq("BOOKING"))

            return self._unmarshal_bookings(response.get("Items", []))
        except Exception as e:
            raise Exception(f"Failed to get all bookings: {str(e)}")

    def get_by_room_and_time(
        self, room_id: str, start_time: int, end_time: int
    ) -> List[Booking]:
        try:
            response = self.table.query(
                IndexName="LSI-5",
                KeyConditionExpression=Key("PK").eq("BOOKING")
                & Key("RoomID").eq(room_id),
                FilterExpression=Attr("EndTime").gt(start_time)
                & Attr("StartTime").lt(end_time),
            )

            return self._unmarshal_bookings(response.get("Items", []))
        except Exception as e:
            raise Exception(f"Failed to get bookings by room and time: {str(e)}")

    def get_by_room_id(self, room_id: str) -> List[Booking]:
        try:
            response = self.table.query(
                IndexName="LSI-5",
                KeyConditionExpression=Key("PK").eq("BOOKING")
                & Key("RoomID").eq(room_id),
            )

            return self._unmarshal_bookings(response.get("Items", []))
        except Exception as e:
            raise Exception(f"Failed to get bookings by room: {str(e)}")

    def get_by_user_id(self, user_id: str) -> List[Booking]:
        try:
            response = self.table.query(
                IndexName="LSI-3",
                KeyConditionExpression=Key("PK").eq("BOOKING")
                & Key("UserID").eq(user_id),
            )

            return self._unmarshal_bookings(response.get("Items", []))
        except Exception as e:
            raise Exception(f"Failed to get bookings by user: {str(e)}")

    def cancel(self, booking_id: str) -> None:
        try:
            self.table.delete_item(
                Key={"PK": "BOOKING", "SK": f"BOOKING#{booking_id}"},
                ConditionExpression="attribute_exists(PK) AND attribute_exists(SK)",
            )
        except self.dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
            raise NotFoundError("Booking not found")
        except Exception as e:
            raise Exception(f"Failed to delete booking: {str(e)}")

    def get_by_date_range(self, start_date: int, end_date: int) -> List[Booking]:
        try:
            response = self.table.query(
                IndexName="LSI-4",
                KeyConditionExpression=Key("PK").eq("BOOKING")
                & Key("Date").between(start_date, end_date),
            )

            return self._unmarshal_bookings(response.get("Items", []))
        except Exception as e:
            raise Exception(f"Failed to get bookings by date range: {str(e)}")

    def get_by_room_id_and_date(self, room_id: str, date: int) -> List[Booking]:
        try:
            start_of_day = (date // 86400) * 86400
            end_of_day = start_of_day + 86400

            response = self.table.query(
                IndexName="LSI-5",
                KeyConditionExpression=Key("PK").eq("BOOKING")
                & Key("RoomID").eq(room_id),
                FilterExpression=Attr("EndTime").gt(start_of_day)
                & Attr("StartTime").lt(end_of_day),
            )

            return self._unmarshal_bookings(response.get("Items", []))
        except Exception as e:
            raise Exception(f"Failed to get bookings by room and date: {str(e)}")

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
