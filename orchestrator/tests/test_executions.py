
from typing import Any

from fastapi.testclient import TestClient


def test_execution_valido(client: TestClient, client_criado: dict[str, object]) -> None:

    req_json = {
        "client_id":client_criado['id'],
        "periodo": "2026-06"
    }

    res = client.post(
        "/executions/start",
        json=req_json
          )
    assert res.status_code == 200
    assert res.json()['status'] == "started"

def test_client_invalido(client: TestClient) -> None:
    req_json = {
        "client_id":9999999 ,
        "periodo": "2026-06"
    }

    res = client.post(
        "/executions/start",
        json=req_json
        )
    assert res.status_code == 404

def test_execution_data_incorreta(
        client: TestClient,
        client_criado: dict[str, object]
        ) -> None:
    
    req_json = {
        "client_id":client_criado['id'],
        "periodo":"2026/06"
    }

    res = client.post(
        "/executions/start",
        json=req_json
        )
    assert res.status_code == 422

def test_execution_diagnose_valida(
        client: TestClient,
        execution: dict[str, object]
          ) -> None:
    
    req_json = {
        "periodo": "2026-06",
        "total_notas": 1,
        "status_banco": "ok",
        "notas_por_status": {
            "pendentes": 0,
            "canceladas": 0,
            "rejeitadas": 0,
            "autorizadas": 1
        },
        
        "status":"em_progresso"
    }

    res = client.post(
        f"/executions/{execution['id']}/diagnose",
          json=req_json
          )
    assert res.status_code == 200

def test_execution_diagnose_invalida(client: TestClient) -> None:

    req_json = {
        "periodo": "2026-06",
        "total_notas": 1,
        "status_banco": "ok",
        "notas_por_status": {
            "pendentes": 0,
            "canceladas": 0,
            "rejeitadas": 0,
            "autorizadas": 1
        },
        
        "status":"em_progresso"
    }

    res = client.post(
        "/executions/999999999/diagnose" , 
        json=req_json
        )
    assert res.status_code == 404

def test_execution_xml_valido(
        execution: dict[str, object],
        execution_diagnose: dict[str, object],
        execution_xml: Any
        ) -> None:
    
    assert execution_xml.status_code == 200

def test_execution_xml_invalido(
    client: TestClient,
    execution: dict[str, object],
) -> None:
    req_json = {
        "total_recebidos": "1",
        "storage_path": "/path/to/storage",
    }

    req_fild = [
        ("file",
        ("31180821367015000162550010000000051000000058-nfe.xml", 
        open(r"C:\Users\tutol\Documents\31180821367015000162550010000000051000000058-nfe.xml", 
        "rb")
        , "application/xml"))
    ]

    res = client.post(
        f"/executions/{execution['id']}/xmls", 
        data=req_json , 
        files=req_fild
        )
    
    assert res.status_code == 400

def test_execution_no_xml(
        client: TestClient, 
        execution: dict[str, object], 
        execution_diagnose: dict[str, object]
        ) -> None:
    
    req_json = {
        "total_recebidos": "1",
        "storage_path": "/path/to/storage",
    }

    req_fild = [
        ("file",
        ("Douglas.docx",
        open(r"C:\Users\tutol\Documents\Douglas.docx", 
        "rb"), 
        "application/xml"))
    ]

    res = client.post(
        f"/executions/{execution['id']}/xmls",
          data=req_json , 
          files=req_fild
          )
    
    assert res.status_code == 400 

def test_execution_xml_incompativel(
        client: TestClient,
        execution: dict[str, object],
        execution_diagnose: dict[str, object]
        ) -> None:
    
    req_json = {
        "total_recebidos": "1",
        "storage_path": "/path/to/storage",
    }

    req_fild = [

        ("file",
        ("31180821367015000162550010000000051000000058-nfe.xml", 
         open(r"C:\Users\tutol\Documents\31180821367015000162550010000000051000000058-nfe.xml", 
        "rb"),
        "application/xml")),

        ("file",
        ("31180821367015000162550010000000051000000058-nfe.xml", 
        open(r"C:\Users\tutol\Documents\31180821367015000162550010000000051000000058-nfe.xml",
        "rb"), 
        "application/xml"))
    ]

    res = client.post(
        f"/executions/{execution['id']}/xmls",
        data=req_json ,
        files=req_fild
            )
    assert res.status_code == 400


