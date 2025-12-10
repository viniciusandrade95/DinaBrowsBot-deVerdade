from dataclasses import dataclass, field
from datetime import date, time
from typing import Optional


@dataclass
class Agendamento:
    id: int
    cliente_id: str
    servico_id: str
    data: date
    hora_inicio: time
    hora_fim: time
    profissional: str = "Equipe"
    observacoes: Optional[str] = None
    origem: str = "chatbot"
    cancelado: bool = False
    criado_em: str = field(default_factory=lambda: "")
