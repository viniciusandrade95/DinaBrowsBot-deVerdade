"""Centralized knowledge for DinaBrows."""
from __future__ import annotations

from typing import Dict, List, Optional

STUDIO_INFO: Dict[str, str] = {
    "name": "DinaBrows",
    "address": "Rua Guilherme Maxwell, perto do Museu da Maré, Rio de Janeiro – RJ, Brasil",
    "openingHours": (
        "Terça a Sexta: 10:00 – 19:00; Sábado: 09:00 – 17:00; Domingo e Segunda: fechado"
    ),
    "description": "Estúdio especializado em sobrancelhas com atendimento acolhedor no Rio de Janeiro.",
}

SERVICES: List[Dict[str, object]] = [
    {
        "id": "brow_lamination_simples",
        "name": "Brow Lamination Simples",
        "description": "Alinhamento e fixação dos fios de sobrancelha para um efeito mais cheio e organizado.",
        "duration_minutes": 45,
        "price_brl": 120,
    },
    {
        "id": "brow_lamination_tintura",
        "name": "Brow Lamination + Tintura",
        "description": "Brow lamination com aplicação de tintura suave para realçar o desenho e preencher falhas visuais.",
        "duration_minutes": 60,
        "price_brl": 160,
    },
    {
        "id": "design_sobrancelhas",
        "name": "Design de Sobrancelhas",
        "description": "Limpeza, desenho e alinhamento das sobrancelhas de acordo com o formato do rosto.",
        "duration_minutes": 30,
        "price_brl": 80,
    },
    {
        "id": "manutencao_sobrancelhas",
        "name": "Manutenção de Sobrancelhas",
        "description": "Retoque do desenho já feito recentemente, removendo apenas os fios crescidos fora da linha.",
        "duration_minutes": 20,
        "price_brl": 60,
    },
    {
        "id": "brow_lamination_completa",
        "name": "Brow Lamination Completa",
        "description": "Combinação de design, brow lamination e finalização com produto para um resultado mais estruturado e duradouro.",
        "duration_minutes": 75,
        "price_brl": 190,
    },
]


def get_studio_info() -> Dict[str, str]:
    return STUDIO_INFO.copy()


def list_services() -> List[Dict[str, object]]:
    return [service.copy() for service in SERVICES]


def find_service_by_name_or_keyword(query: str) -> Optional[Dict[str, object]]:
    if not query:
        return None
    q = query.lower()
    for service in SERVICES:
        name = service.get("name", "").lower()
        if q in name or any(token in name for token in q.split()):
            return service
    return None
