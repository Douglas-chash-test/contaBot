from fastapi.testclient import TestClient

from app.server import app

client = TestClient(app)


class TestAPIFlow:
    """
    Testes de integração em sequência, com estado compartilhado entre etapas.
    A ordem de execução é garantida pelo prefixo numérico nos nomes dos métodos.
    """

    client_id: int | None = None
    execution_id: int | None = None
    command_id: int | None = None

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _ok(self, label: str, response) -> dict:
        print(f"\n{'=' * 50}")
        print(f"[{label}]  status={response.status_code}")
        body = response.json()
        print(f"Response: {body}")
        assert response.status_code == 200, (
            f"{label} falhou — esperado 200, obtido {response.status_code}: {response.text}"
        )
        return body

    # ------------------------------------------------------------------
    # 1. Sanidade
    # ------------------------------------------------------------------

    def test_01_root(self) -> None:
        print("\n###### 1. Testando rota raiz... ######")
        response = client.get("/")
        self._ok("GET /", response)

    # ------------------------------------------------------------------
    # 2. Clientes
    # ------------------------------------------------------------------

    def test_02_create_client(self) -> None:
        print("\n###### 2. Criando cliente... ######")
        payload = {
            "cnpj": "38742850001698",
            "inscricao_estadual": "126456789",
            "razao_social": "Empresa Teste LTDA",
            "whatsapp_dest": "11987654321",
            "erp_type": "ERP Teste",
            "db_type": "PostgreSQL",
            "document_types": ["nfce", "nfe"],
            "config_json": {"key": "value"},
        }
        body = self._ok("POST /clients", client.post("/clients", json=payload))
        TestAPIFlow.client_id = body["id"]
        print(f"client_id salvo: {self.client_id}")

    # ------------------------------------------------------------------
    # 3. Execuções
    # ------------------------------------------------------------------

    def test_03_create_execution(self) -> None:
        print("\n###### 3. Criando execução... ######")
        assert self.client_id is not None, "client_id ausente — rode test_02 primeiro"
        payload = {
            "client_id": self.client_id,
            "periodo": "2026-06",
        }
        body = self._ok("POST /executions/start", client.post("/executions/start", json=payload))
        TestAPIFlow.execution_id = body["id"]
        print(f"execution_id salvo: {self.execution_id}")

    def test_04_execution_diagnose(self) -> None:
        print("\n###### 4. Diagnosticando execução... ######")
        assert self.execution_id is not None, "execution_id ausente — rode test_03 primeiro"
        payload = {
            "periodo": "2026-05",
            "total_notas": 1,
            "status_banco": "ok",
            "notas_por_status": {
                "pendentes": 0,
                "canceladas": 0,
                "rejeitadas": 0,
                "autorizadas": 1
            }
        }
        
        self._ok(
            f"POST /executions/{self.execution_id}/diagnose",
            client.post(f"/executions/{self.execution_id}/diagnose", json=payload),
        )

    def test_05_execution_update_xmls(self) -> None:
        print("\n###### 5. Atualizando XMLs da execução... ######")
        assert self.execution_id is not None, "execution_id ausente — rode test_03 primeiro"
        payload_arq = [
            (
                "file",
                (
                    "31180821367015000162550010000000051000000058-nfe.xml",
                    open(r"C:\Users\tutol\Documents\31180821367015000162550010000000051000000058-nfe.xml", "rb"),
                    "application/xml",
                ),
            )
        ]
        self._ok(
            f"POST /executions/{self.execution_id}/xmls",
            client.post(f"/executions/{self.execution_id}/xmls", files=payload_arq),
        )

    def test_06_execution_report(self) -> None:
        print("\n###### 6. Enviando relatório de execução... ######")
        assert self.execution_id is not None, "execution_id ausente — rode test_03 primeiro"
        payload = {
            "total_recebidos": 1,
            "storage_path": "/path/to/reports",
        }
        payload_arq = [
            ("file",("teste.txt", open(r"C:\Users\tutol\Documents\teste.txt", "rb"), "text/plain"))
        ]
        self._ok(
            f"POST /executions/{self.execution_id}/reports",
            client.post(f"/executions/{self.execution_id}/reports", data=payload , files=payload_arq),
        )

    def test_07_execution_failure(self) -> None:
        print("\n###### 7. Registrando falha de execução... ######")
        assert self.execution_id is not None, "execution_id ausente — rode test_03 primeiro"
        payload = {
            "execution_id": self.execution_id,
            "message": "Erro ao processar execução",
            "details": {"error_code": "123", "info": "Detalhes do erro"},
        }
        self._ok(
            f"POST /executions/{self.execution_id}/failure",
            client.post(f"/executions/{self.execution_id}/failure", json=payload),
        )

    def test_08_execution_status(self) -> None:
        print("\n###### 8. Consultando status da execução... ######")
        assert self.execution_id is not None, "execution_id ausente — rode test_03 primeiro"
        self._ok(
            f"GET /executions/{self.execution_id}/status",
            client.get(f"/executions/{self.execution_id}/status"),
        )

    # ------------------------------------------------------------------
    # 4. Comandos
    # ------------------------------------------------------------------

    def test_09_execution_commands(self) -> None:
        print("\n###### 9. Listando comandos da execução... ######")
        assert self.execution_id is not None, "execution_id ausente — rode test_03 primeiro"
        body = self._ok(
            f"GET /executions/{self.execution_id}/commands",
            client.get(f"/executions/{self.execution_id}/commands"),
        )
        assert len(body) > 0, "Nenhum comando retornado para a execução"
        TestAPIFlow.command_id = body[0]["id"]
        print(f"command_id salvo: {self.command_id}")

    def test_10_command_result(self) -> None:
        print("\n###### 10. Registrando resultado de comando... ######")
        assert self.command_id is not None, "command_id ausente — rode test_09 primeiro"
        payload = {
            "success": True,
            "result": {"output": "Resultado do comando"},
            "error_message": None,
        }
        self._ok(
            f"POST /commands/{self.command_id}/result",
            client.post(f"/commands/{self.command_id}/result", json=payload),
        )