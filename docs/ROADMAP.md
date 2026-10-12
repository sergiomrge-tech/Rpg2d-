# Roadmap

Legenda: ✅ feito · 🔄 em andamento · ⬜ a fazer

## Etapa 0 — Infra
- ✅ Projeto Unity 2022.3 (cena criada por código, `Boot.cs`)
- ✅ CI GitHub Actions (GameCI) com build Linux + screenshots na branch `ci-shots`
- ⬜ **Usuário:** cadastrar segredos `UNITY_LICENSE`, `UNITY_EMAIL`, `UNITY_PASSWORD` ([guia](UNITY_CI.md))
- ✅ Checagem de compilação local (`tools/unity_check.sh`)
- ⬜ Validar primeiro build real e corrigir o que aparecer nos screenshots

## Etapa 1 — Capítulo 1 jogável (atual)
- ✅ Herói: 10 animações × 3 direções (idle, andar, correr, 3 ataques, magia, rolar, dano, morte)
- ✅ Diabrete: voo, ataque, magia, dano, morte (dissolve)
- ✅ NPCs: recepcionista da Guilda, ferreiro, aldeã
- ✅ Vila de Aurora + Bosque dos Chifres (chão pintado, rio, ponte, praça, 23 tipos de objeto, vento nas árvores)
- ✅ FX: cortes, garras, impactos, explosões, círculos mágicos, Centelha I/II/III, fumaça demoníaca
- ✅ Combate (stamina, combo, rolar, postura, telegrafia, hit-stop), loot, XP/nível, missão, prólogo, save
- 🔄 **Texturas do HUD** (medalhão, arcos, orbes, faixa de diálogo, fitas, pílulas, vinheta) — código pronto, falta gerar `Sprites/Ui/*`
- ⬜ Ícones de itens/habilidades (`Sprites/Ui/icons`)
- ⬜ Retratos (herói, Elina, Borin, Marta, Lumia)
- 🔄 Chefe do capítulo: Diabrete-Chefe Grakk — sprite HD novo com 21 trilhas de animação e prévia gerados no catálogo; **não foi integrado ao combate** e precisa de gate visual/Unity.
- 🔄 Oni soldado (2º demônio) — sprite HD novo com clava, armadura e 18 trilhas de animação; **não foi registrado nos spawns** e precisa de gate visual/Unity.
- ⬜ Menus: inventário/grimório (livro aberto), forja, quadro de missões
- ⬜ Música e ambiência por região

## Etapa 2 — Capítulos 2–3
- ⬜ Floresta de Velmoor (mapa, Dríade Profanada, companheira Sylra)
- ⬜ Cidade de Valemont (mapa grande, Guilda principal, lojas)
- ⬜ Sistema de companheiro (IA aliada)
- ⬜ Evolução Centelha II + Corte Crescente
- ⬜ Equipamentos com atributos e forja

## Etapa 3 — Capítulos 4–7
- ⬜ Deserto, Minas, Pântano, Picos Gelados (+ demônios temáticos e chefes)
- ⬜ Árvores de habilidade completas (níveis III)
- ⬜ Iluminação 2D (dia/noite, tochas, cavernas)

## Etapa 4 — Capítulos 8–10 e final
- ⬜ Castelo sitiado, Terras Devastadas, Cidadela
- ⬜ 4 Generais + Rei Demônio Malgrath (3 fases)
- ⬜ Finais, créditos, Novo Jogo+

## Etapa 5 — Polimento e lançamento
- ⬜ Gamepad, opções, legendas/idiomas
- ⬜ Balanceamento (alvo ~30 h)
- ⬜ Builds Windows/Mac, página do jogo

## Próximo passo imediato
1. Gerar texturas do HUD + ícones + retratos (`tools/art_hd/ui.py`).
2. Assim que a licença estiver nos segredos: rodar o CI, ver screenshots e corrigir.
3. Chefe Grakk + Oni soldado para fechar o Capítulo 1.

## Catálogo expandido — Lote 1 (especificação técnica)
- ✅ Fichas técnicas de **10 demônios + 5 chefes** em `docs/asset_catalog/LOTE1_FICHAS.md`, com 285 trilhas e 3.024 quadros **especificados e agora renderizados**, FPS, quadro de evento, rig, região e habilidades individuais.
- ✅ Validador estático `tools/art_hd/verify_lote1.py` compara o contrato com os JSONs reais das 15 criaturas sem depender da licença Unity.
- ✅ 13 novas folhas de sprites produzidas (todos os 10 demônios e 5 chefes do Lote 1 possuem PNG/JSON e prévia); gerador em `tools/art_hd/build_lote1_art.py` e QA automática. **Ainda requer aprovação visual e testes reais Unity.**
- ✅ `skill_2` de Grakk renderizada nas três direções, assim como as duas habilidades animadas dos outros quatro chefes.
- ⬜ Criar VFX específicos das habilidades; implementar AI, hitboxes, loot e spawns. Nenhum novo inimigo do Lote 1 foi integrado ao combate.
- ⬜ Aprovar fidelidade HD cartoon de todos os 15 via capturas **reais** do Unity, corrigir clipping/escala e só então integrar IA, spawns e chefes opcionais, preservando os chefes narrativos do GDD.

## Direção de qualidade — revisão visual dos Lotes 1 e 2 (12/10/2026)
- 🔄 **Lote 1: oito silhuetas redesenhadas** após avaliação de repetição: batedor alado, saqueador de quatro braços, salamandra de brasas, sapo ressonador, naga lanceiro, tartaruga blindada, ceifador ósseo e Morgash bovino de seis patas. Arte candidata, aguardando aprovação visual.
- ✅ Renderização completa em `gpt6-lote1-silhouettes-20261012`: os 15 atlas PNG/JSON continuam verificáveis e a Action de revisão **38246798620** passou; máscaras de silhueta e corte de bordas foram verificadas sem alterar personagem/cenário aprovado.
- 🔄 Pranchas de comparação de sprites originais versus remodelados: `docs/asset_catalog/previews/LOTE1_REMODEL_COMPARACAO.png` e `LOTE1_REMODEL_OITO.png`; imagens do pipeline, **não capturas do jogo**.
- ✅ **Ordem de produção do Lote 2 definida:** `docs/asset_catalog/LOTE2_ORDEM_PRODUCAO.md` (10 insetoides e 5 bosses de anatomias próprias). Nenhum sprite do Lote 2 gerado ainda.
- ⬜ Inspecionar a fidelidade ao estilo HD cartoon em escala real na Unity; obter aprovação do diretor antes de incorporar os remodelados. VFX únicos, IA, spawns e gameplays dos novos inimigos seguem pendentes.

## Regra permanente — entrega obrigatoriamente jogável (12/10/2026)
**Exigência do usuário:** parar de entregar arte conceitual ou pranchas avulsas como se fossem conclusão de produção. Para cada novo inimigo, criar os assets **no projeto Unity**, com sprites importados, animações de caminhada, ataque e habilidades em três direções, movimentação/IA, hitbox, VFX, dano e cooldown realmente funcionais. Chefes têm duas habilidades. Validar em runtime Unity antes de declarar pronto. **Detalhes:** [Regra obrigatória de assets jogáveis](asset_catalog/REGRA_OBRIGATORIA_ASSETS_JOGAVEIS.md).
- ⬜ Lote 2 — piloto jogável de `mantis_reaver`, `scarab_brute` e `moth_hexer` com modelagem 2D refinada e rigs próprios; status ainda não implementado.
- ⬜ Integrar em Unity movimentos, ataques, habilidades e testes reais; só então avançar nas demais 12 criaturas.
