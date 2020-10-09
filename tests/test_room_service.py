from executor.room_service import RoomService


def test_room_service():
    rs = RoomService()
    assert rs is not None
