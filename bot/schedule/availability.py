from datetime import datetime, timedelta, time, date
from typing import List, Optional

from .repository import InMemoryAgendaRepository
from ..domain.sobrancelhas import SERVICOS

FUNCIONAMENTO_INICIO = time(9, 0)
FUNCIONAMENTO_FIM = time(18, 0)
MICRO_BLOCOS = [time(10, 0), time(14, 0)]


def calcular_duracao_total(servicos: List[str]) -> int:
    total = 0
    for servico_id in servicos:
        servico = SERVICOS.get(servico_id)
        if servico:
            total += servico.duracao_min
    return total


def _gerar_slots(dia: date, duracao_min: int) -> List[str]:
    slots = []
    current = datetime.combine(dia, FUNCIONAMENTO_INICIO)
    end_day = datetime.combine(dia, FUNCIONAMENTO_FIM)
    delta = timedelta(minutes=30)
    while current + timedelta(minutes=duracao_min) <= end_day:
        slots.append(current.strftime("%H:%M"))
        current += delta
    return slots


def _ocupado(repo: InMemoryAgendaRepository, dia: date, inicio: time, fim: time) -> bool:
    for ag in repo.listar_agendamentos_no_periodo(dia):
        if not ag.cancelado:
            if ag.hora_inicio < fim and inicio < ag.hora_fim:
                return True
    return False


def buscar_horarios_livres(
    repo: InMemoryAgendaRepository,
    data: date,
    duracao_min: int,
    profissional: Optional[str] = None,
    janela: Optional[List[time]] = None,
) -> List[str]:
    horarios_disponiveis: List[str] = []
    possible_slots = _gerar_slots(data, duracao_min)
    for slot in possible_slots:
        h, m = slot.split(":")
        inicio = time(int(h), int(m))
        fim_dt = datetime.combine(data, inicio) + timedelta(minutes=duracao_min)
        fim = fim_dt.time()
        if janela and inicio not in janela:
            continue
        if _ocupado(repo, data, inicio, fim):
            continue
        horarios_disponiveis.append(slot)
    return horarios_disponiveis
