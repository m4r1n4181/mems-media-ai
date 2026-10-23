def test_health_reports_data(client):
    r = client.get("/health").json()
    assert r["data"]["loaded"] and r["data"]["client_brands"] == 2


def test_brands_and_unknown_brand(client):
    assert {b["brand"] for b in client.get("/brands").json()} == {"glowskin", "fitfuel"}
    assert client.get("/brands/nope").status_code == 404
    assert client.get("/brands/nope/recommendations").status_code == 404


def test_recommendations_are_ranked_and_explained(client):
    r = client.get("/brands/glowskin/recommendations?k=10").json()
    assert [i["rank"] for i in r["items"]] == [1, 2, 3]
    top = r["items"][0]
    assert top["creator"]["niche"] == "beauty & makeup"
    assert top["reasons"][0]["text"].startswith("Mentioned the brand 2 time(s)")


def test_recommendation_filters(client):
    items = lambda q: [i["creator_id"] for i in client.get(f"/brands/glowskin/recommendations?{q}").json()["items"]]
    assert items("max_followers=50000") == ["c_0000000000", "c_0000000001"]
    assert items("min_followers=10000&max_followers=50000") == ["c_0000000001"]
    assert items("niche=fitness") == ["c_0000000002"]
    assert items("exclude=c_0000000000,c_0000000001") == ["c_0000000002"]
    assert items("k=1") == ["c_0000000000"]


def test_creator_profile(client):
    assert client.get("/creators/c_0000000001").json()["size_tier"] == "micro"
    assert client.get("/creators/c_x").status_code == 404
