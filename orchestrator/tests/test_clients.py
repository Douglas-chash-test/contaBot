
from fastapi.testclient import TestClient


def test_cria_client_valido(
    client: TestClient,
    dados_client: dict[str, object],
) -> None:
    res = client.post("/clients", json=dados_client)
    assert res.status_code == 200

def test_cnpj_duplicado(client: TestClient, dados_client: dict[str, object]) -> None:
    
    client.post("/clients", json=dados_client)
    res_duplicado = client.post(
        "/clients",
          json=dados_client
          )
    assert res_duplicado.status_code == 409
    
    

def test_cnpj_ouverflow(client: TestClient, dados_client: dict[str, object]) -> None:

    req_json = {
        "cnpj": "123456789012345",
        "inscricao_estadual": str(dados_client['inscricao_estadual']),
        "razao_social": "Empresa Teste LTDA",
        "whatsapp_dest": "11987654321",
        "erp_type": "ERP Teste",
        "db_type": "PostgreSQL",
        "document_types": ["nfce", "nfe"],
        "config_json": {"key": "value"},
    }

    res = client.post("/clients", json=req_json)
    assert res.status_code == 422
    assert len(req_json["cnpj"]) > 14 

def test_document_type_vazio(
    client: TestClient,
    dados_client: dict[str, object],
) -> None:

    req_json = {
        "cnpj": dados_client['cnpj'],
        "inscricao_estadual": dados_client['inscricao_estadual'],
        "razao_social": "Empresa Teste LTDA",
        "whatsapp_dest": "11987654321",
        "erp_type": "ERP Teste",
        "db_type": "PostgreSQL",
        "document_types": [],
        "config_json": {"key": "value"},
    }
    
    res = client.post("/clients", json=req_json)
    assert res.status_code == 422

def test_document_type_incorreto(
        client: TestClient,
        dados_client: dict[str, object]
          ) -> None:

    req_json = {
        "cnpj": dados_client['cnpj'],
        "inscricao_estadual": dados_client['inscricao_estadual'],
        "razao_social": "Empresa Teste LTDA",
        "whatsapp_dest": "11987654321",
        "erp_type": "ERP Teste",
        "db_type": "PostgreSQL",
        "document_types": ["cte", "nfe"],
        "config_json": {"key": "value"},
    }

    res = client.post("/clients", json=req_json)
    assert res.status_code == 422


    