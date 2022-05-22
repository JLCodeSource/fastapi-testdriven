import json


def create_summary(testclient, url):
    response = testclient.post("/summaries/", data=json.dumps({"url": f"{url}"}))
    summary_id = response.json()["id"]

    return summary_id
