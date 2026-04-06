from pydantic import BaseModel
from datetime import datetime

#None = None -> Não é obrigatório colocar esse atributo no construtor. Se tiver um campo sem None e ele não tiver no constutor, a aplicação crasha
class BlogModel(BaseModel):
    title: str | None = None
    content: str | None = None
    date: datetime | None = None