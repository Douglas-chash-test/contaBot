from typing import Literal

from pydantic import BaseModel, Field, field_validator

DocumentType = Literal["nfce", "nfe", "sintegra", "cte"]


class ClientCreate(BaseModel):
    cnpj: str = Field(min_length=14, max_length=14)
    inscricao_estadual: str = Field(min_length=1, max_length=32)
    razao_social: str = Field(min_length=1, max_length=255)
    whatsapp_dest: str = Field(min_length=8, max_length=32)
    erp_type: str = Field(min_length=1, max_length=64)
    db_type: str = Field(min_length=1, max_length=64)
    document_types: list[DocumentType]
    config_json: dict[str, object] = Field(default_factory=dict)

    @field_validator("document_types")
    @classmethod
    def validate_document_types(
        cls,
        value: list[DocumentType],
    ) -> list[DocumentType]:
        if not value:
            raise ValueError("document_types must have at least one item")

        if "cte" in value and len(value) > 1:
            raise ValueError("cte cannot be combined with other document types")

        if len(value) != len(set(value)):
            raise ValueError("document_types cannot contain duplicates")

        return value


class ClientRead(ClientCreate):
    id: int
