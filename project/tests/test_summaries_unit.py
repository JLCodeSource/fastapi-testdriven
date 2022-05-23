import json
from datetime import datetime

import pytest
from fastapi import status

from app.api import crud, summaries

from .errors import ERRORS


def test_create_summary(test_app, monkeypatch):
    # Given
    # test_app

    # And
    # Mock generate summary
    def mock_generate_summary(summary_id, url):
        return None

    monkeypatch.setattr(summaries, "generate_summary", mock_generate_summary)

    # And
    # mock test payloads for request & response
    test_request_payload = {"url": "https://foo.bar"}
    test_response_payload = {"id": 1, "url": "https://foo.bar"}

    # And
    # a mock function to post a payload, returning the id
    async def mock_post(payload):
        return 1

    # And
    # The monkeypatch overrides crud post to mock_post
    monkeypatch.setattr(crud, "post", mock_post)

    # When
    # The test_request_payload is posted
    response = test_app.post(
        "/summaries/",
        data=json.dumps(test_request_payload),
    )

    # Then
    # The status code is 201 created
    assert response.status_code == status.HTTP_201_CREATED

    # And
    # The response is the test response payload
    assert response.json() == test_response_payload


def test_create_summaries_empty_json(test_app):
    # Given
    # test_app

    # When
    # An empty json is posted to summaries
    response = test_app.post("/summaries/", data=json.dumps({}))

    # Then
    # The status code is 422 unprocessable entity
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # And
    # The json response detail is missing url
    assert response.json()["detail"] == ERRORS["missing_url"]


def test_create_summaries_invalid_url(test_app):
    # Given
    # test_app

    # When
    # An invalid url is posted to summaries
    response = test_app.post("/summaries/", data=json.dumps({"url": "invalid://url"}))

    # Then
    # The status code is 422 unprocessable entity
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # And
    # The json response detail message is URL scheme not permitted
    assert response.json()["detail"][0]["msg"] == ERRORS["invalid_url"]


def test_read_summary(test_app, monkeypatch):
    # Given
    # test_app

    # And
    # test_data
    test_data = {
        "id": 1,
        "url": "https://foo.bar",
        "summary": "summary",
        "created_at": datetime.utcnow().isoformat(),
    }

    # And
    # A mock_get overriding the crud get
    async def mock_get(id):
        return test_data

    monkeypatch.setattr(crud, "get", mock_get)

    # When
    # A user gets a summary
    response = test_app.get("/summaries/1/")

    # Then
    # The status_code is 200 ok
    assert response.status_code == status.HTTP_200_OK

    # And
    # The json is the test data
    assert response.json() == test_data


def test_read_summary_incorrect_id(test_app, monkeypatch):
    # Given
    # test_app

    # And
    # A mock get
    async def mock_get(id):
        return None

    monkeypatch.setattr(crud, "get", mock_get)

    # When
    # A user gets a summary that doesn't exist
    response = test_app.get("/summaries/1/")

    # Then
    # The status code is 404 not found
    response.status_code == status.HTTP_404_NOT_FOUND

    # And
    # The json response detail is "Summary not found"
    response.json()["detail"] == "Test not found"


def test_read_all_summaries(test_app, monkeypatch):
    # Given
    # test_app

    # And
    # Mock data
    test_data = [
        {
            "id": 1,
            "url": "https://foo.bar",
            "summary": "summary",
            "created_at": datetime.utcnow().isoformat(),
        },
        {
            "id": 2,
            "url": "https://testdriven.io/",
            "summary": "summary",
            "created_at": datetime.utcnow().isoformat(),
        },
    ]

    # And
    # Mock get all
    async def mock_get_all():
        return test_data

    monkeypatch.setattr(crud, "get_all", mock_get_all)

    # When
    # Get is executed against summaries
    response = test_app.get("/summaries/")

    # Then
    # The status code is 200 ok
    assert response.status_code == status.HTTP_200_OK

    # And
    # The json response is the test_data
    assert response.json() == test_data


def test_remove_summary(test_app, monkeypatch):
    # Given
    # test_app

    # And
    # A test get
    async def mock_get(id):
        return {
            "id": 1,
            "url": "https://foo.bar",
            "summary": "summary",
            "created_at": datetime.utcnow().isoformat(),
        }

    monkeypatch.setattr(crud, "get", mock_get)

    # And
    # test_data
    test_data = {"id": 1, "url": "https://foo.bar"}

    # And
    # Mock delete
    async def mock_delete(id):
        return id

    monkeypatch.setattr(crud, "delete", mock_delete)

    # When
    # A delete is executed
    response = test_app.delete("/summaries/1/")

    # Then
    # The status code is 200 ok
    assert response.status_code == status.HTTP_200_OK

    # And
    # The response json is the id and url
    assert response.json() == test_data


def test_remove_summary_incorrect_id(test_app, monkeypatch):
    # Given
    # test_app

    # And
    # Mock get returning no summary
    async def mock_get(id):
        return None

    monkeypatch.setattr(crud, "get", mock_get)

    # When
    # A user gets a missing summary
    response = test_app.get("/summaries/1/")

    # Then
    # The status code is 404 not found
    assert response.status_code == status.HTTP_404_NOT_FOUND

    # And
    # The json response detail is "Summary not found"
    assert response.json()["detail"] == ERRORS["not_found"]


def test_update_summary(test_app, monkeypatch):
    # Given
    # test_app

    # And
    # Mock data
    test_request_payload = {"url": "https://foo.bar", "summary": "updated"}
    test_response_payload = {
        "id": 1,
        "url": "https://foo.bar",
        "summary": "updated",
        "created_at": datetime.utcnow().isoformat(),
    }

    # And
    # A mock put
    async def mock_put(id, payload):
        return test_response_payload

    monkeypatch.setattr(crud, "put", mock_put)

    # When
    # An update request is sent
    response = test_app.put(
        "/summaries/1/",
        data=json.dumps(test_request_payload),
    )

    # Then
    # The status code will be 200 ok
    assert response.status_code == status.HTTP_200_OK

    # And
    # The response detail will be the response payload
    assert response.json() == test_response_payload


@pytest.mark.parametrize(
    ("summary_id", "payload", "status_code", "detail"),
    [
        [
            999,
            {"url": "https://bar.baz", "summary": "updated"},
            status.HTTP_404_NOT_FOUND,
            ERRORS["not_found"],
        ],
        [
            "test",
            {"url": "https://bar.baz", "summary": "update"},
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            ERRORS["not_int"],
        ],
        [
            0,
            {"url": "https://baz.bar", "summary": "updated"},
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            ERRORS["not_gt_0"],
        ],
        [
            1,
            {},
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            ERRORS["missing_url_&_summary"],
        ],
        [
            1,
            {"url": "https://bar.baz"},
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            ERRORS["missing_summary"],
        ],
    ],
    ids=[
        "unit_non_existent_id",
        "unit_non_int_id",
        "unit_id_0_or_less",
        "unit_empty_json",
        "unit_missing_summary",
    ],
)
def test_update_summary_invalid(
    test_app, monkeypatch, summary_id, payload, status_code, detail
):
    # TODO
    # Work out how this actually tests anything

    # Given
    # test_app
    # And
    # The above fixtures

    # And
    # A mock function for put
    async def mock_put(id, payload):
        return None

    # And
    # monkeypatch overrides the crud put
    monkeypatch.setattr(crud, "put", mock_put)

    # When
    # User tries to update the summary using invalid data
    response = test_app.put(
        f"/summaries/{summary_id}/",
        data=json.dumps(payload),
    )

    # Then
    # The status code is status_code
    response.status_code == status_code

    # And
    # The json response detail is detail
    response.json()["detail"] == detail


def test_update_summary_invalid_url(test_app):
    # Given
    # test_app

    # When
    # An invalid url is posted to the summary id
    response = test_app.put(
        "/summaries/1/",
        data=json.dumps({"url": "invalid://url", "summary": "updated"}),
    )

    # Then
    # The status code will be 422 unprocessable entity
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # And
    # The json detail message will be that the URL scheme is not permitted
    assert response.json()["detail"][0]["msg"] == ERRORS["invalid_url"]
