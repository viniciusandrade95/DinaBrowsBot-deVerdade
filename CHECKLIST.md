# CHECKLIST

- [x] Fluxo de agendamento de sobrancelha implementado
  - Testes: test_agendar_design_basico, test_agendar_em_horario_cheio_sugere_alternativas, test_micro_apenas_em_blocos_especificos
- [x] FlowEngine com estados principais funcionando
  - Testes: test_agendar_design_basico
- [x] Módulo de agenda (models, repository, availability)
  - Testes: test_agendar_em_horario_cheio_sugere_alternativas, test_micro_apenas_em_blocos_especificos
- [x] Integração com LLM customizado (analyse_message + generate_reply)
  - Testes: test_sobrancelha_flow
- [x] Integração com /chat e /webhook
  - Testes: test_contact_forwarding
- [x] Testes automatizados principais criados e passando
  - Testes: pytest
- [ ] Lint/format (se houver) está OK
