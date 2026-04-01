from pydantic import BaseModel

#None = None -> Não é obrigatório colocar esse atributo no construtor. Se tiver um campo sem None e ele não tiver no constutor, a aplicação crasha
class DistributionIndices(BaseModel):
    _id: str | None = None
    agent_acronym: str | None = None
    cnpj_number: str | None = None
    consumer_unit_set_id: str | None = None
    consumer_unit_set_description: str | None = None
    indicator_type_code: str | None = None
    year: int | None = None
    period: int | None = None
    value: float | None = None
    generation_date: str | None = None