import json

from fastapi import status


def test_create_summary(test_app_with_db):

    # Given
    # test_app_with_db

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
    assert response.json() == {
        "detail": [
            {
                "loc": ["body", "url"],
                "msg": "field required",
                "type": "value_error.missing",
            }
        ]
    }


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


def test_read_summary(test_app_with_db):
    response = test_app_with_db.post(
        "/summaries/", data=json.dumps({"url": "https://foo.bar"})
    )
    summary_id = response.json()["id"]

    response = test_app_with_db.get(f"/summaries/{summary_id}/")
    assert response.status_code == status.HTTP_200_OK

    response_dict = response.json()
    assert response_dict["id"] == summary_id
    assert response_dict["url"] == "https://foo.bar"
    assert response_dict["summary"]
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
    assert response.json()["detail"] == "Summary not found"


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


def test_read_all_summaries(test_app_with_db):
    response = test_app_with_db.post(
        "/summaries/", data=json.dumps({"url": "https://foo.bar"})
    )

    summary_id = response.json()["id"]

    response = test_app_with_db.get("/summaries/")
    assert response.status_code == status.HTTP_200_OK

    response_list = response.json()
    assert len(list(filter(lambda d: d["id"] == summary_id, response_list))) == 1


def test_remove_summary(test_app_with_db):
    # Given
    # test_app_with_db

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


def test_update_summary(test_app_with_db):
    # Given
    # test_app_with_db

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


def test_update_summary_incorect_id(test_app_with_db):
    # Given
    # test_app_with_db

    # When
    # The user sends an update with an incorrect id
    response = test_app_with_db.put(
        "/summaries/999/",
        data=json.dumps({"url": "https://bar.baz", "summary": "updated"}),
    )

    # Then
    # The status code will be 404 not found
    assert response.status_code == 404

    # And
    # The detail will be "Summary not found"
    assert response.json()["detail"] == "Summary not found"


def test_update_summary_non_int_id(test_app):
    # Given
    # test_app

    # When
    # A non-int id is supplied
    response = test_app.put(
        "/summaries/test/",
        data=json.dumps({"url": "https://bar.baz", "summary": "updated"}),
    )

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


def test_update_summary_id_0_or_less(test_app):
    # Given
    # test_app

    # When
    # The user attempts to update a summary with an id of 0 or less
    response = test_app.put(
        "/summaries/0/",
        data=json.dumps({"url": "https://foo.bar", "summary": "updated"}),
    )

    # Then
    # The status code will be 422 unprocessable entity
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # And
    # The response json detail will explain that the id must be greater than 0
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


def test_update_summary_invalid_json(test_app_with_db):
    # Given
    # test_app_with_db

    # And
    # There is a summary in the database

    response = test_app_with_db.post(
        "/summaries/", data=json.dumps({"url": "https://foo.bar"})
    )
    summary_id = response.json()["id"]

    # When
    # The user sends an update with invalid json
    response = test_app_with_db.put(f"/summaries/{summary_id}/", data=json.dumps({}))

    # Then
    # The response will be 422 UNPROCESSABLE_ENTITY
    assert response.status_code == 422

    # And
    # The json will have the required detail
    assert response.json() == {
        "detail": [
            {
                "loc": ["body", "url"],
                "msg": "field required",
                "type": "value_error.missing",
            },
            {
                "loc": ["body", "summary"],
                "msg": "field required",
                "type": "value_error.missing",
            },
        ]
    }


def test_update_summary_missing_summary(test_app_with_db):
    # Given
    # test_app_with_db

    # And
    # There is a summary in the database

    response = test_app_with_db.post(
        "/summaries/", data=json.dumps({"url": "https://foo.bar"})
    )
    summary_id = response.json()["id"]

    # When
    # The user sends a url without a summary
    response = test_app_with_db.put(
        f"/summaries/{summary_id}/", data=json.dumps({"url": "https://bar.baz"})
    )

    # Then
    # The response will be 422 Unprocessable entity
    assert response.status_code == 422

    # And
    # The response json will highlight the missing summary
    assert response.json() == {
        "detail": [
            {
                "loc": ["body", "summary"],
                "msg": "field required",
                "type": "value_error.missing",
            }
        ]
    }


def test_update_summary_with_invalid_url(test_app_with_db):
    # Given
    # test_app_with_db

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
    assert response.json()["detail"][0]["msg"] == "URL scheme not permitted"
