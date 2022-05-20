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


def test_create_summary_invalid_json(test_app):
    response = test_app.post("/summaries/", data=json.dumps({}))
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json() == {
        "detail": [
            {
                "loc": ["body", "url"],
                "msg": "field required",
                "type": "value_error.missing",
            }
        ]
    }


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


def test_read_summary_incorrect_id(test_app_with_db):
    response = test_app_with_db.get("/summaries/999/")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Summary not found"


def test_read_all_summaries(test_app_with_db):
    response = test_app_with_db.post(
        "/summaries/", data=json.dumps({"url": "https://foo.bar"})
    )

    summary_id = response.json()["id"]

    response = test_app_with_db.get("/summaries/")
    assert response.status_code == status.HTTP_200_OK

    response_list = response.json()
    assert len(
        list(filter(lambda d: d["id"] == summary_id, response_list))
    ) == 1


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
    response = test_app_with_db.delete(
        f"/summaries/{summary_id}/"
    )

    # Then
    # The status code is 200 ok
    assert response.status_code == status.HTTP_200_OK

    # And
    # The response content is {"id": "{summary_id"}
    assert response.json() == {"id": summary_id,
                               "url": "https://foo.bar"}

    # And
    # The summary database is removed from the database
    # TODO


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
    response = test_app_with_db.put(f"/summaries/{summary_id}/",
                                    data=json.dumps({"url": "https://bar.baz",
                                                     "summary": "updated"}))

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
    response = test_app_with_db.put("/summaries/999/",
                                    data=json.dumps({"url": "https://bar.baz",
                                                     "summary": "updated"}))

    # Then
    # The status code will be 404 not found
    assert response.status_code == 404

    # And
    # The detail will be "Summary not found"
    assert response.json()["detail"] == "Summary not found"


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
    response = test_app_with_db.put(
        f"/summaries/{summary_id}/",
        data=json.dumps({})
    )

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
                "type": "value_error.missing"
            }
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
        f"/summaries/{summary_id}/", data=json.dumps({"url":
                                                      "https://bar.baz"})
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
