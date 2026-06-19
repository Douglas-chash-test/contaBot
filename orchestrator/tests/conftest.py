import os
import tempfile
import uuid
from collections.abc import Generator
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.server import app


@pytest.fixture
def xml_temp() -> Generator[Any,Any,Any]: 
    xml_content = b'''
    <?xml version="1.0"
     encoding="UTF-8"?><nfe><infNFe 
     Id="1"></infNFe></nfe>
     '''

    with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as f:
        f.write(xml_content)
        tmp_path = f.name

    yield tmp_path
    os.remove(tmp_path)

@pytest.fixture
def docx_temp() -> Generator[Any,Any,Any]:
    with tempfile.NamedTemporaryFile(
        suffix=".docx", 
        delete=False
        ) as f:

        f.write(b"conteudo qualquer")
        tmp_path = f.name
    yield tmp_path
    os.remove(tmp_path)



@pytest.fixture
def db() -> Generator[Session, None, None]:
    db = next(get_db())
    yield db
    db.close()

@pytest.fixture
def client() -> TestClient:
    return TestClient(app)

@pytest.fixture
def dados_client() -> dict[str, object]:
    cnpj = str(uuid.uuid4().int)
    ins = str(uuid.uuid4().int)

    cnpj_form = cnpj[0:14]
    ins_form = ins[0:9]

    return {
            "cnpj": cnpj_form,
            "inscricao_estadual": ins_form,
            "razao_social": "Empresa Teste LTDA",
            "whatsapp_dest": "11987654321",
            "erp_type": "ERP Teste",
            "db_type": "PostgreSQL",
            "document_types": ["nfce", "nfe"],
            "config_json": {"key": "value"},
    }

@pytest.fixture
def client_criado(
    client: TestClient,
    dados_client: dict[str, object],
    db: Session,
) -> Generator[dict[str, object], None, None]:
    
    res = client.post("/clients", json=dados_client)
    yield res.json()
    db.execute(text('DELETE FROM clients WHERE id = :id'),
                {'id': res.json()['id']})
    db.commit()

@pytest.fixture
def execution(
    client_criado: dict[str, object],
    client: TestClient,
    db: Session,
) -> Generator[dict[str, object], None, None]:

    json_req = {
        "client_id": client_criado["id"],
        "periodo": '2026-06'
    }

    res = client.post("/executions/start", json=json_req)
    yield res.json()

    db.execute(text('DELETE FROM executions WHERE id = :id'), 
               {'id':res.json()['id']})
    db.commit()

@pytest.fixture
def execution_diagnose(
    client: TestClient,
    execution: dict[str, object],
    db: Session,
) -> Generator[dict[str, object], None, None]:

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

    res = client.post(f"/executions/{execution['id']}/diagnose", json=req_json)
    yield res.json()

@pytest.fixture
def execution_xml(
    client: TestClient,
    execution: dict[str, object],
    db: Session,
    xml_temp:str
) -> Generator[Any, None, None]:

    req_json = {
        "total_recebidos": "1",
        "storage_path": "/path/to/storage",
    }

    req_fild = [
    ("file", ("nfe_teste.xml", open(xml_temp, "rb"), "application/xml"))
    ]

    res = client.post(
        f"/executions/{execution['id']}/xmls",
         data=req_json , 
         files=req_fild
         )
    yield res
    
    


