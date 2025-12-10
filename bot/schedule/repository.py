from datetime import date
from typing import Dict, List, Optional

from .models import Agendamento


class InMemoryAgendaRepository:
    def __init__(self):
        self._items: Dict[int, Agendamento] = {}
        self._counter = 1

    def criar_agendamento(self, agendamento: Agendamento) -> Agendamento:
        agendamento.id = self._counter
        self._counter += 1
        self._items[agendamento.id] = agendamento
        return agendamento

    def cancelar_agendamento(self, agendamento_id: int) -> Optional[Agendamento]:
        ag = self._items.get(agendamento_id)
        if ag:
            ag.cancelado = True
        return ag

    def buscar_agendamentos_cliente(self, cliente_id: str) -> List[Agendamento]:
        return [a for a in self._items.values() if a.cliente_id == cliente_id]

    def buscar_agendamento_por_id(self, agendamento_id: int) -> Optional[Agendamento]:
        return self._items.get(agendamento_id)

    def listar_agendamentos_no_periodo(self, dia: date) -> List[Agendamento]:
        return [a for a in self._items.values() if a.data == dia and not a.cancelado]


def build_repository() -> InMemoryAgendaRepository:
    return InMemoryAgendaRepository()
