import json

import pytest
from fastapi import status

from app.api import summaries

from .errors import ERRORS
from .helpers import create_summary


def test_create_summary(test_app_with_db, monkeypatch):
    # Given
    # test_app_with_db

    # And
    # Mock generate summary
    def mock_generate_summary(summary_id, url):
        return None

    monkeypatch.setattr(summaries, "generate_summary", mock_generate_summary)

    # When
    # posting the json
    # {"url": "https://foo.bar"} to /summaries/
    response = test_app_with_db.post(
        "/summaries/", data=json.dumps({"url": "https://foo.bar"})
    )

    # Then
    # The status code will be 201 created
    # And the response will be {"url": "https://foo.bar"}
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["url"] == "https://foo.bar"


def test_create_summary_missing_url(test_app):
    # Given
    # test_app

    # When
    # There is no url submitted
    response = test_app.post("/summaries/", data=json.dumps({}))

    # Then
    # The status code is 422 Unprocessable entity
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # And
    # The json reponse detail explains what is missing
    assert response.json()["detail"] == ERRORS["missing_url"]


def test_create_summary_invalid_url(test_app):
    # Given
    # test_app

    # When
    # An invalid url is submitted
    response = test_app.post("/summaries/", data=json.dumps({"url": "invalid://url"}))

    # Then
    # The resposne status code should be 422 unprocessable entity
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # And
    # The json reponse detail should state that the URL is not permitted
    assert response.json()["detail"][0]["msg"] == "URL scheme not permitted"


def test_read_summary(test_app_with_db, monkeypatch):
    # Given
    # test_app_with_db

    # And
    # Mock generate summary
    def mock_generate_summary(summary_id, url):
        return None

    monkeypatch.setattr(summaries, "generate_summary", mock_generate_summary)

    response = test_app_with_db.post(
        "/summaries/", data=json.dumps({"url": "https://foo.bar"})
    )
    summary_id = response.json()["id"]

    response = test_app_with_db.get(f"/summaries/{summary_id}/")
    assert response.status_code == status.HTTP_200_OK

    response_dict = response.json()
    assert response_dict["id"] == summary_id
    assert response_dict["url"] == "https://foo.bar"
    assert response_dict["summary"] == ""
    assert response_dict["created_at"]


def test_read_summary_nonexistent_id(test_app_with_db):
    # Given
    # test_app_with_db

    # When
    # An incorrect id is supplied
    response = test_app_with_db.get("/summaries/999/")

    # Then
    # The status code will be 404 not found
    assert response.status_code == status.HTTP_404_NOT_FOUND

    # And
    # The response will be Summary not found
    assert response.json()["detail"] == ERRORS["not_found"]


def test_read_summary_0_or_less(test_app_with_db):
    # Given
    # test_app_with_db

    # When
    # An id of 0 or below is supplied
    response = test_app_with_db.get("/summaries/0/")

    # Then
    # The status code will be 422 unprocessable entity
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # And
    # The response will explain that the id should be greater than 0
    assert response.json() == {
        "detail": [
            {
                "loc": ["path", "id"],
                "msg": "ensure this value is greater than 0",
                "type": "value_error.number.not_gt",
                "ctx": {"limit_value": 0},
            }
        ]
    }


def test_read_summary_non_int_id(test_app):
    # Given
    # test_app

    # When
    # A non-int id is supplied
    response = test_app.get("/summaries/test/")

    # Then
    # The status code will be 422 unprocessable entity
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # And
    # The response will explain the the id should be an int
    assert response.json() == {
        "detail": [
            {
                "loc": ["path", "id"],
                "msg": "value is not a valid integer",
                "type": "type_error.integer",
            }
        ]
    }


def test_read_all_summaries(test_app_with_db, monkeypatch):
    # Given
    # test_app_with_db

    # And
    # Mock generate summary
    def mock_generate_summary(summary_id, url):
        return None

    monkeypatch.setattr(summaries, "generate_summary", mock_generate_summary)

    # When a url is posted
    response = test_app_with_db.post(
        "/summaries/", data=json.dumps({"url": "https://foo.bar"})
    )
    summary_id = response.json()["id"]
    response = test_app_with_db.get("/summaries/")

    # Then
    # The status code will be 200 ok
    assert response.status_code == status.HTTP_200_OK

    # And
    # The response json will be a list of urls with the new summary
    response_list = response.json()
    assert len(list(filter(lambda d: d["id"] == summary_id, response_list))) == 1
    # Todo improve summaries testing


def test_remove_summary(test_app_with_db, monkeypatch):
    # Given
    # test_app_with_db

    # And
    # Mock generate summary
    def mock_generate_summary(summary_id, url):
        return None

    monkeypatch.setattr(summaries, "generate_summary", mock_generate_summary)

    # And
    # There is a summary in the database

    response = test_app_with_db.post(
        "/summaries/", data=json.dumps({"url": "https://foo.bar"})
    )
    summary_id = response.json()["id"]

    # When
    # The user executes a delete on "/summaries/{id}"
    response = test_app_with_db.delete(f"/summaries/{summary_id}/")

    # And
    # The user checks the deletion was executed
    is_deleted = test_app_with_db.get(f"/summaries/{summary_id}/")

    # Then
    # The status code is 200 ok
    assert response.status_code == status.HTTP_200_OK

    # And
    # The response content is {"id": "{summary_id"}
    assert response.json() == {"id": summary_id, "url": "https://foo.bar"}

    # And
    # The summary entry is no longer available in the database
    assert is_deleted.status_code == status.HTTP_404_NOT_FOUND
    assert is_deleted.json()["detail"] == "Summary not found"


def test_remove_summary_incorrect_id(test_app_with_db):
    # Given
    # test_app_with_db

    # When
    # The user executes a delete on an incorrect id
    response = test_app_with_db.delete("/summaries/999/")

    # Then
    # The status code is 404 not found
    assert response.status_code == status.HTTP_404_NOT_FOUND

    # And
    # The response content is "Summary not found"
    assert response.json()["detail"] == "Summary not found"


def test_remove_summary_non_int_id(test_app):
    # Given
    # test_app

    # When
    # A non-int id is supplied
    response = test_app.delete("/summaries/test/")

    # Then
    # The status code will be 422 unprocessable entity
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # And
    # The response will explain the the id should be an int
    assert response.json() == {
        "detail": [
            {
                "loc": ["path", "id"],
                "msg": "value is not a valid integer",
                "type": "type_error.integer",
            }
        ]
    }


def test_remove_summary_with_id_0_or_less(test_app_with_db):
    # Given
    # test_app_with_db

    # When
    # User tries to delete id with value 0 or less
    response = test_app_with_db.delete("/summaries/0/")

    # Then
    # Response status code is 422 unprocessable entity
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # And
    # Response json detail explains the value needs to be greater than 0
    assert response.json() == {
        "detail": [
            {
                "loc": ["path", "id"],
                "msg": "ensure this value is greater than 0",
                "type": "value_error.number.not_gt",
                "ctx": {"limit_value": 0},
            }
        ]
    }


def test_update_summary(test_app_with_db, monkeypatch):
    # Given
    # test_app_with_db

    # And
    # Mock generate summary
    def mock_generate_summary(summary_id, url):
        return None

    monkeypatch.setattr(summaries, "generate_summary", mock_generate_summary)

    # And
    # There is a summary in the database

    response = test_app_with_db.post(
        "/summaries/", data=json.dumps({"url": "https://foo.bar"})
    )
    summary_id = response.json()["id"]

    # When
    # The user sends a put message to /summaries/{id}
    response = test_app_with_db.put(
        f"/summaries/{summary_id}/",
        data=json.dumps({"url": "https://bar.baz", "summary": "updated"}),
    )

    # Then
    # The status code will be 200 ok
    assert response.status_code == 200

    # And
    # It will update the details as per the request
    response_dict = response.json()
    assert response_dict["id"] == summary_id
    assert response_dict["url"] == "https://bar.baz"
    assert response_dict["summary"] == "updated"
    assert response_dict["created_at"]


def test_update_summary_with_invalid_url(test_app_with_db, monkeypatch):
    # Given
    # test_app_with_db

    # And
    # Mock generate summary
    def mock_generate_summary(summary_id, url):
        return None

    monkeypatch.setattr(summaries, "generate_summary", mock_generate_summary)

    # And
    # There is a summary in the database

    response = test_app_with_db.post(
        "/summaries/", data=json.dumps({"url": "https://foo.bar"})
    )
    summary_id = response.json()["id"]

    # When
    # User tries to update the summary using an invalid url
    response = test_app_with_db.put(
        f"/summaries/{summary_id}/",
        data=json.dumps({"url": "invalid://url", "summary": "updated"}),
    )

    # Then
    # The response status code is 422 unprocessable entity
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # And the response detail explains that the URL scheme is not permitted
    assert response.json()["detail"][0]["msg"] == ERRORS["invalid_url"]


@pytest.mark.parametrize(
    ("add_summary", "summary_id", "payload", "status_code", "detail"),
    [
        [
            0,
            999,
            {"url": "https://bar.baz", "summary": "updated"},
            status.HTTP_404_NOT_FOUND,
            ERRORS["not_found"],
        ],
        [
            0,
            "test",
            {"url": "https://bar.baz", "summary": "update"},
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            ERRORS["not_int"],
        ],
        [
            0,
            0,
            {"url": "https://baz.bar", "summary": "updated"},
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            ERRORS["not_gt_0"],
        ],
        [
            1,
            None,
            {},
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            ERRORS["missing_url_&_summary"],
        ],
        [
            1,
            None,
            {"url": "https://bar.baz"},
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            ERRORS["missing_summary"],
        ],
    ],
    ids=[
        "e2e_non_existent_id,",
        "e2e_non_int_id",
        "e2e_id_0_or_less",
        "e2e_empty_json",
        "e2e_missing_summary",
    ],
)
def test_update_summary_invalid(
    test_app_with_db, monkeypatch, add_summary, summary_id, payload, status_code, detail
):
    # Given
    # test_app_with_db

    # And
    # Mock generate summary
    def mock_generate_summary(summary_id, url):
        return None

    monkeypatch.setattr(summaries, "generate_summary", mock_generate_summary)

    # And
    # [If there is a summary in the database]
    if add_summary:
        summary_id = create_summary(test_app_with_db, "https://bar.baz")

    # When
    # User tries to update the summary using invalid data
    response = test_app_with_db.put(
        f"/summaries/{summary_id}/", data=json.dumps(payload)
    )

    # Then
    # The status_code is status_code
    response.status_code == status_code

    # And
    # The json detail is detail
    response.json()["detail"] == detail
