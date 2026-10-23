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


# ---------- cold start: brands the model has never seen ----------
def test_lookalike_fuses_lists_of_similar_brands(client):
    r = client.post("/lookalike/recommendations", json={"similar_brands": ["@GlowSkin", "fitfuel"]}).json()
    items = r["items"]
    # c_2 is #3 for glowskin and #1 for fitfuel: 1/63 + 1/61 beats a single #1 (1/61)
    assert [i["creator_id"] for i in items] == ["c_0000000002", "c_0000000000", "c_0000000001"]
    assert [i["rank"] for i in items] == [1, 2, 3]
    assert items[0]["reasons"][0] == {"code": "lookalike", "brands": ["fitfuel", "glowskin"],
                                      "text": "Ranked highly for similar brands: @fitfuel, @glowskin"}
    assert r["similar_brands"] == ["glowskin", "fitfuel"]


def test_lookalike_filters_and_unknown_brands(client):
    post = lambda **kw: client.post("/lookalike/recommendations", json={"similar_brands": ["glowskin"], **kw})
    assert [i["creator_id"] for i in post(max_followers=50000, exclude=["c_0000000000"]).json()["items"]] == \
        ["c_0000000001"]
    assert client.post("/lookalike/recommendations", json={"similar_brands": ["nope"]}).status_code == 422
    assert client.post("/lookalike/recommendations", json={"similar_brands": []}).status_code == 422


def test_lookalike_fuses_the_brand_niche(client):
    r = client.post("/lookalike/recommendations",
                    json={"similar_brands": ["fitfuel"], "brand_niche": "beauty & makeup"}).json()
    by_id = {i["creator_id"]: i for i in r["items"]}
    assert set(by_id) == {"c_0000000000", "c_0000000001", "c_0000000002"}
    # c_0 comes only from the niche list, c_2 only from the similar brand
    assert [x["code"] for x in by_id["c_0000000000"]["reasons"]] == ["same_niche"]
    assert by_id["c_0000000000"]["reasons"][0]["text"] == "Same niche as the brand: beauty & makeup"
    assert by_id["c_0000000002"]["reasons"][0]["code"] == "lookalike"
