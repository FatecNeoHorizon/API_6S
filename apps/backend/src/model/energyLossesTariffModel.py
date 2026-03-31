from pydantic import BaseModel

#None = None -> Não é obrigatório colocar esse atributo no construtor. Se tiver um campo sem None e ele não tiver no constutor, a aplicação crasha
class EnergyLossesTariff(BaseModel):
    _id: str | None = None
    distributor: str | None = None
    distributor_slug: str | None = None
    state: str | None = None
    uf: str | None = None
    process_date: str | None = None
    tme_brl_mwh: float | None = None
    basic_network_loss_mwh: float | None = None
    technical_loss_mwh: float | None = None
    non_technical_loss_mwh: float | None = None
    basic_network_loss_cost_brl: float | None = None
    technical_loss_cost_brl: float | None = None
    non_technical_loss_cost_brl: float | None = None
    parcel_b_brl: float | None = None
    required_revenue_brl : float | None = None