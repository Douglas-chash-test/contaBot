import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.db.dependencies import get_db
from app.server import app


@pytest.fixture
def db():
    db = next(get_db())
    yield db
    db.close()

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def dados_client():
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
def client_criado(client, dados_client , db):
        
    res = client.post("/clients" , json=dados_client)
    yield res.json()
    db.execute(text('DELETE FROM clients WHERE id = :id'),
                {'id': res.json()['id']})
    db.commit()

@pytest.fixture
def execution(client_criado, client, db):

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
def execution_diagnose(client, execution, db):

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
def execution_xml(client, execution, db):

    req_json = {
        "total_recebidos": 1,
        "storage_path": "/path/to/storage",
    }

    req_fild = [
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
    yield res
    
    


