from datetime import date, time

from bot.core import handle_message, agenda_repo
from bot.state import InMemoryStateStore
from bot.config import InMemoryConfigStore, TenantConfig
from bot.knowledge import get_studio_info


def make_config_store():
    info = get_studio_info()
    demo_tenant = TenantConfig(
        tenant_id="store-1",
        name=info["name"],
        tone="friendly",
        language="pt",
        currency="BRL",
        default_model="20b",
        allow_chitchat=False,
        max_reply_length=600,
        store_info=info,
    )
    return InMemoryConfigStore({"store-1": demo_tenant})


def test_agendar_design_basico():
    state_store = InMemoryStateStore()
    config_store = make_config_store()
    user_id = "user-a"

    steps = [
        "quero fazer sobrancelha",
        "só limpar e desenhar",
        "2024-05-10",
        "manha",
        "sim",
    ]

    reply = ""
    for text in steps:
        reply = handle_message(
            tenant_id="store-1",
            user_id=user_id,
            text=text,
            message_id="test",
            state_store=state_store,
            config_store=config_store,
        )
    assert "Confirmei" in reply


def test_agendar_em_horario_cheio_sugere_alternativas():
    state_store = InMemoryStateStore()
    config_store = make_config_store()
    user_id = "user-b"

    from bot.schedule.models import Agendamento

    agenda_repo.criar_agendamento(
        Agendamento(
            id=0,
            cliente_id="bulk",
            servico_id="design",
            data=date(2024, 5, 11),
            hora_inicio=time(9, 0),
            hora_fim=time(18, 0),
        )
    )

    steps = [
        "quero fazer sobrancelha",
        "design",
        "2024-05-11",
        "manha",
    ]

    reply = ""
    for text in steps:
        reply = handle_message(
            tenant_id="store-1",
            user_id=user_id,
            text=text,
            message_id="test",
            state_store=state_store,
            config_store=config_store,
        )
    assert "Não tenho horários" in reply


def test_micro_apenas_em_blocos_especificos():
    state_store = InMemoryStateStore()
    config_store = make_config_store()
    user_id = "user-c"

    steps = [
        "quero micro",
        "2024-05-12",
        "tarde",
    ]

    reply = ""
    for text in steps:
        reply = handle_message(
            tenant_id="store-1",
            user_id=user_id,
            text=text,
            message_id="test",
            state_store=state_store,
            config_store=config_store,
        )
    assert "10:00" in reply or "14:00" in reply


def test_retoque_micro_fora_da_janela():
    state_store = InMemoryStateStore()
    config_store = make_config_store()
    user_id = "user-d"

    handle_message(
        tenant_id="store-1",
        user_id=user_id,
        text="quero retoque de micro",
        message_id="test",
        state_store=state_store,
        config_store=config_store,
    )
    reply = handle_message(
        tenant_id="store-1",
        user_id=user_id,
        text="2023-01-01",
        message_id="test",
        state_store=state_store,
        config_store=config_store,
    )
    assert "avaliação" in reply.lower()


def test_cancelamento_basico():
    state_store = InMemoryStateStore()
    config_store = make_config_store()
    user_id = "user-e"

    from bot.schedule.models import Agendamento

    ag = agenda_repo.criar_agendamento(
        Agendamento(
            id=0,
            cliente_id=user_id,
            servico_id="design",
            data=date(2024, 5, 13),
            hora_inicio=time(9, 0),
            hora_fim=time(9, 30),
        )
    )

    handle_message(
        tenant_id="store-1",
        user_id=user_id,
        text="quero cancelar",
        message_id="test",
        state_store=state_store,
        config_store=config_store,
    )
    reply = handle_message(
        tenant_id="store-1",
        user_id=user_id,
        text=str(ag.id),
        message_id="test",
        state_store=state_store,
        config_store=config_store,
    )
    assert "cancel" in reply.lower()
