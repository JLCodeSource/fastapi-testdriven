ERRORS = {
    "not_found": "Summary not found",
    "invalid_url": "URL scheme not permitted",
    "not_int": [
        {
            "loc": ["path", "id"],
            "msg": "value is not a valid integer",
            "type": "type_error.integer",
        }
    ],
    "not_gt_0": [
        {
            "loc": ["path", "id"],
            "msg": "ensure this value is greater than 0",
            "type": "value_error.number.not_gt",
            "ctx": {"limit_value": 0},
        }
    ],
    "missing_url_&_summary": [
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
    ],
    "missing_summary": [
        {
            "loc": ["body", "summary"],
            "msg": "field required",
            "type": "value_error.missing",
        }
    ],
    "missing_url": [
        {
            "loc": ["body", "url"],
            "msg": "field required",
            "type": "value_error.missing",
        }
    ],
}
