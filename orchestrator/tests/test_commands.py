from fastapi.testclient import TestClient


def test_commands(
        client: TestClient,
        execution:dict[str, object],
        commands:dict[str, object]
        )-> None:
    assert commands['status'] == "pendente"
    assert commands['execution_id'] == execution['id']
