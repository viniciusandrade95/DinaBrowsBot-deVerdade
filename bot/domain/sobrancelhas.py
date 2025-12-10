from dataclasses import dataclass
from typing import List


@dataclass
class ServicoSobrancelha:
    id: str
    nome: str
    duracao_min: int
    tipo: str
    requer_avaliacao_previa: bool = False
    requer_sessao_anterior: bool = False


def catalogo_servicos() -> List[ServicoSobrancelha]:
    return [
        ServicoSobrancelha(
            id="design",
            nome="Design de sobrancelhas",
            duracao_min=30,
            tipo="simples",
        ),
        ServicoSobrancelha(
            id="design_henna",
            nome="Design + henna",
            duracao_min=45,
            tipo="simples",
        ),
        ServicoSobrancelha(
            id="micro",
            nome="Micropigmentação de sobrancelhas",
            duracao_min=120,
            tipo="procedimento_avancado",
            requer_avaliacao_previa=True,
        ),
        ServicoSobrancelha(
            id="retoque_micro",
            nome="Retoque de micropigmentação",
            duracao_min=90,
            tipo="retoque",
            requer_sessao_anterior=True,
        ),
        ServicoSobrancelha(
            id="avaliacao_sobrancelha",
            nome="Avaliação de sobrancelhas",
            duracao_min=20,
            tipo="avaliacao",
        ),
    ]


SERVICOS = {item.id: item for item in catalogo_servicos()}
