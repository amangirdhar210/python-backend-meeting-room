import pytest
from fastapi.testclient import TestClient
from main import app
from httpx import Response
from logging import log
from json import loads
client = TestClient(app)


def test_login():
    res: Response = client.post(
        "/login", json= {"email":"amangirdhar2004@wg.com", "password":"12345678"}
    )

    res_dict: dict= loads(res.content)

    # print(res_dict)
    token=res_dict.get("token")
    print(token)
    # log(5,res_dict)
