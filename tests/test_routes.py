class TestOperatorRoutes:

    def test_create_operator(self, client):
        response = client.post(
            "/operators/", json={
                "name": "John Doe",
                "is_active": True,
                "max_load": 15
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "John Doe"
        assert data["max_load"] == 15
        assert "id" in data

    def test_create_operator_defaults(self, client):
        response = client.post(
            "/operators/", json={
                "name": "Jane Doe"
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["is_active"] is True
        assert data["max_load"] == 10

    def test_list_operators(self, client, test_operator):
        response = client.get("/operators/")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert "current_load" in data[0]

    def test_get_operator(self, client, test_operator):
        response = client.get(f"/operators/{test_operator.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_operator.id
        assert data["name"] == test_operator.name

    def test_get_operator_not_found(self, client):
        response = client.get("/operators/9999")

        assert response.status_code == 404

    def test_update_operator(self, client, test_operator):
        response = client.patch(
            f"/operators/{test_operator.id}", json={
                "is_active": False,
                "max_load": 20
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is False
        assert data["max_load"] == 20

    def test_update_operator_partial(self, client, test_operator):
        response = client.patch(
            f"/operators/{test_operator.id}", json={
                "max_load": 25
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["max_load"] == 25
        assert data["is_active"] == test_operator.is_active


class TestSourceRoutes:

    def test_create_source(self, client):
        response = client.post(
            "/sources/", json={
                "name": "Telegram Bot",
                "description": "Main bot"
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Telegram Bot"
        assert "id" in data

    def test_list_sources(self, client, test_source):
        response = client.get("/sources/")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_get_source(self, client, test_source):
        response = client.get(f"/sources/{test_source.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_source.id

    def test_configure_weights(self, client, test_source, test_operators):
        response = client.post(
            f"/sources/{test_source.id}/weights", json=[
                {"operator_id": test_operators[0].id, "weight": 10},
                {"operator_id": test_operators[1].id, "weight": 30}
            ]
        )

        assert response.status_code == 200
        assert "message" in response.json()

    def test_configure_weights_invalid_operator(self, client, test_source):
        response = client.post(
            f"/sources/{test_source.id}/weights", json=[
                {"operator_id": 9999, "weight": 10}
            ]
        )

        assert response.status_code == 404

    def test_get_weights(self, client, test_source_with_weights):
        response = client.get(
            f"/sources/{test_source_with_weights.id}/weights"
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        assert "operator_id" in data[0]
        assert "weight" in data[0]


class TestAppealRoutes:

    def test_create_appeal(self, client, test_source_with_weights):
        response = client.post(
            "/appeals/", json={
                "lead_external_id": "test_lead_api",
                "source_id": test_source_with_weights.id,
                "message": "Hello from API",
                "lead_name": "API Test User",
                "lead_phone": "+79991234567"
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["lead_external_id"] == "test_lead_api"
        assert data["source_id"] == test_source_with_weights.id
        assert "appeal_id" in data
        assert "operator" in data

    def test_create_appeal_existing_lead(
        self, client, test_lead, test_source_with_weights
    ):
        response = client.post(
            "/appeals/", json={
                "lead_external_id": test_lead.external_id,
                "source_id": test_source_with_weights.id,
                "message": "Second appeal"
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["lead_external_id"] == test_lead.external_id

    def test_create_appeal_invalid_source(self, client):
        response = client.post(
            "/appeals/", json={
                "lead_external_id": "lead_123",
                "source_id": 9999,
                "message": "Test"
            }
        )

        assert response.status_code == 404

    def test_create_appeal_no_operators(self, client, test_source):
        response = client.post(
            "/appeals/", json={
                "lead_external_id": "lead_no_ops",
                "source_id": test_source.id,
                "message": "No operators"
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["operator"] is None

    def test_close_appeal(self, client, test_lead, test_source, test_operator):
        create_response = client.post(
            "/appeals/", json={
                "lead_external_id": test_lead.external_id,
                "source_id": test_source.id,
                "message": "To be closed"
            }
        )
        appeal_id = create_response.json()["appeal_id"]

        response = client.patch(f"/appeals/{appeal_id}/close")

        assert response.status_code == 200
        assert "message" in response.json()

    def test_close_nonexistent_appeal(self, client):
        response = client.patch("/appeals/9999/close")

        assert response.status_code == 404

    def test_list_leads(self, client, test_lead):
        response = client.get("/appeals/leads")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert "appeals_count" in data[0]

    def test_get_lead_appeals(
        self, client, test_lead, test_source, test_operator
    ):
        client.post(
            "/appeals/", json={
                "lead_external_id": test_lead.external_id,
                "source_id": test_source.id,
                "message": "Test"
            }
        )

        response = client.get(f"/appeals/leads/{test_lead.id}/appeals")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert "source" in data[0]

    def test_get_lead_appeals_not_found(self, client):
        response = client.get("/appeals/leads/9999/appeals")

        assert response.status_code == 404


class TestStatsRoutes:

    def test_get_distribution_stats(
        self, client, test_source, test_operators, test_lead
    ):
        for _ in range(3):
            client.post(
                "/appeals/", json={
                    "lead_external_id": f"lead_{_}",
                    "source_id": test_source.id,
                    "message": "Test"
                }
            )

        response = client.get("/stats/distribution")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_available_operators(self, client, test_source_with_weights):
        response = client.get(
            f"/stats/sources/{test_source_with_weights.id}/operators"
        )

        assert response.status_code == 200
        data = response.json()
        assert "source_id" in data
        assert "operators" in data
        assert isinstance(data["operators"], list)

        if len(data["operators"]) > 0:
            op = data["operators"][0]
            assert "id" in op
            assert "weight" in op
            assert "current_load" in op
            assert "is_available" in op


class TestRootRoutes:

    def test_root(self, client):
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data

    def test_health(self, client):
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestEndToEndScenario:

    def test_complete_workflow(self, client):
        op1 = client.post(
            "/operators/", json={
                "name": "Operator A",
                "max_load": 5
            }
        ).json()

        op2 = client.post(
            "/operators/", json={
                "name": "Operator B",
                "max_load": 10
            }
        ).json()

        source = client.post(
            "/sources/", json={
                "name": "Telegram",
                "description": "Telegram bot"
            }
        ).json()

        client.post(
            f"/sources/{source['id']}/weights", json=[
                {"operator_id": op1["id"], "weight": 25},
                {"operator_id": op2["id"], "weight": 75}
            ]
        )

        appeals = []
        for i in range(5):
            appeal = client.post(
                "/appeals/", json={
                    "lead_external_id": f"lead_{i}",
                    "source_id": source["id"],
                    "message": f"Message {i}"
                }
            ).json()
            appeals.append(appeal)

        assigned_operators = [a["operator"]["id"] for a in appeals if
                              a["operator"]]
        assert len(assigned_operators) == 5

        stats = client.get("/stats/distribution").json()
        assert len(stats) >= 1

        close_response = client.patch(
            f"/appeals/{appeals[0]['appeal_id']}/close"
        )
        assert close_response.status_code == 200

        operators_list = client.get("/operators/").json()
        op1_load = next(op for op in operators_list if op["id"] == op1["id"])
        assert op1_load["current_load"] < 5

    def test_load_balancing(self, client):
        op1 = client.post(
            "/operators/", json={
                "name": "Small Load Op",
                "max_load": 2
            }
        ).json()

        op2 = client.post(
            "/operators/", json={
                "name": "Big Load Op",
                "max_load": 10
            }
        ).json()

        source = client.post(
            "/sources/", json={
                "name": "Bot"
            }
        ).json()

        client.post(
            f"/sources/{source['id']}/weights", json=[
                {"operator_id": op1["id"], "weight": 50},
                {"operator_id": op2["id"], "weight": 50}
            ]
        )

        appeals = []
        for i in range(10):
            appeal = client.post(
                "/appeals/", json={
                    "lead_external_id": f"load_test_{i}",
                    "source_id": source["id"],
                    "message": f"Load test {i}"
                }
            ).json()
            appeals.append(appeal)

        op1_count = sum(
            1 for a in appeals if
            a["operator"] and a["operator"]["id"] == op1["id"]
        )
        op2_count = sum(
            1 for a in appeals if
            a["operator"] and a["operator"]["id"] == op2["id"]
        )

        assert op1_count <= 2
        assert op2_count >= 8
