# REGRA OBRIGATÓRIA — Assets jogáveis, não arte conceitual

**Decisão expressa do usuário em 12/10/2026 — prioridade máxima para todos os lotes futuros deste RPG.**

> "Não quero arte conceitual, quero que faça os assets no jogo com cada animações, movimentos e habilidades."

## Regra de entrega (não negociável)

1. **Não entregar concept art, moodboards, pôsteres, ilustrações avulsas, folhas de apresentação ou imagens que pareçam sprites, mas não estejam implementadas** como resultado do desenvolvimento de criaturas. Pranchas/prints podem ser fornecidos apenas como evidência auxiliar **real** de assets integrados e, quando disserem "print do jogo", capturados de uma execução real da Unity.
2. **Criar o asset operacional no projeto Unity do GitHub** (sheets PNG RGBA com transparência válida, atlas com quadros cortáveis, metadados JSON/importação compatíveis com `Sprites/Demons/<id>` e `SpriteAnim`, pivô, dimensões e FPS). Arquivos de imagem *por si só* não concluem a tarefa.
3. **Animação completa e verificável** por criatura, nas direções `down`, `up`, `side`, com espelhamento lateral quando aplicável:
   - Demônios comuns: `idle`, `move`, `attack`, `cast` (habilidade), `hurt`, `death`.
   - Chefes: todos os anteriores mais `skill_2`; fases/ultimate quando projetadas no catálogo.
   - Cada estado deve variar visivelmente entre quadros; não vale duplicar a pose ou aplicar apenas VFX estático. Garantir `hit` no quadro zero-indexado correto e transições de estados funcionais.
4. **Movimento real no jogo:** prefab/componente de criatura conectado às ações de IA, locomoção diferenciada por espécie (rastejar, andar, saltar, voar, escavar etc.), velocidade, orientação/facing, colisões, hitbox/hurtbox e resposta a danos.
5. **Ataque e habilidades funcionais:** não basta desenhar a animação. Sincronizar o frame de impacto com dano/área/projétil/telegraph/VFX, cooldown, alcance, comportamento da IA, reação, interrupção e morte. Chefes exigem duas habilidades distintas realmente acionáveis. Projetar e testar gameplay com efeitos próprios por espécie.
6. **Integrar ao jogo de verdade:** assets importados e referenciados pela Unity, registros de inimigos e dados de combate, spawn controlado em cena/região de teste real, sem alterar ou excluir assets previamente aprovados. Antes de colocar no mundo principal, usar área de teste integrada à build, depois liberar por gate visual.
7. **Acabamento superior e anatomias próprias:** preservar o padrão gráfico HD cartoon atual (sombras, contornos, cores, qualidade e escala), com modelagem/desenho muito mais detalhados que o Lote 1 inicial. Nenhum inimigo pode ser apenas o mesmo corpo com arma/cor diferente. Lote 2: 10 demônios insetoides e 5 chefes, cada qual com silhueta, rig, anatomia e gestos próprios.
8. **Validação e comunicação transparentes:** testar geração e integridade de atlas, animações, estados de IA, dano, cooldown, hitboxes, desempenho e build Unity 2022.3 LTS. Capturas do jogo só podem ser imagens de execução real. Se a Unity não estiver acessível, declarar exatamente o que foi implementado e o que ainda falta; **não** chamar sprites isolados, concept art, mockups ou animações só no papel de "integrados" ou "jogáveis".

## Critério de pronto obrigatório (Definition of Done)

Uma criatura **não está pronta** até que todos os pontos estejam comprovados:

- [ ] Arte final HD cartoon com anatomia inédita, PNG/JSON/rig corretamente importados.
- [ ] Todos os estados de animação e todas as direções funcionam no runtime Unity.
- [ ] Movimentação autônoma, orientação e navegação correspondem à espécie.
- [ ] Ataque básico e habilidade(s) funcionam, com VFX, telegraph, hitbox, hit-frame e cooldown.
- [ ] Dano, `hurt` e `death` funcionam; encontros de chefes com `skill_1` e `skill_2`.
- [ ] Spawn em cena real de teste e interface legível em escala de gameplay.
- [ ] Testes no Unity com evidências reais da execução, sem regressão no estilo existente.
- [ ] Revisão e aprovação visual do diretor; só depois integrar a fauna aos mapas de campanha.

**Estados permitidos:** `specification_only` → `generated_assets` → `unity_imported` → `movement_integrated` → `combat_integrated` → `runtime_tested` → `visual_approved` → `game_ready`. Nunca pular etapas ou reportar status acima do verificado.

## Como aplicar ao Lote 2

Seguir a ordem de `LOTE2_ORDEM_PRODUCAO.md`, produzindo inicialmente **três criaturas-piloto** (`mantis_reaver`, `scarab_brute`, `moth_hexer`), mas **não parar nos seus desenhos**. Cada piloto deverá ser testável como inimigo real na Unity, com movimentação, ataque, habilidades e animações antes de expandir para os outros 12. A qualidade será revisada ao longo da implementação, nunca apenas em pôsteres ou ilustrações.

**Esta regra prevalece sobre orientações anteriores do projeto que aceitavam meros catálogos, concept art ou sprites não integrados como entrega final.**
