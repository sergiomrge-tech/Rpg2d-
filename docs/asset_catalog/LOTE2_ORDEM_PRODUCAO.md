# Lote 2 — ordem de produção, demônios insetoides (10 + 5 chefes)

**Decisão do diretor:** primeiro corrigir as silhuetas repetitivas do Lote 1. Só iniciar o Lote 2 após inspecionar as oito remodelagens. Nenhuma arte do Lote 2 foi gerada ainda.

**Direção artística obrigatória:** manter o **HD cartoon do projeto**, com materiais Cairo, sombras suaves, contornos coloridos, animações em três direções e alta legibilidade em jogo. Espécies novas exigem **anatomia própria** e não podem diferir apenas por cor, textura ou arma.

## Sequência priorizada

| Ordem | Criatura | Inseto / plano corporal | Diferença anatômica principal |
|---:|---|---|---|
| 1 | `mantis_reaver` | Louva-a-deus bípede invertido | Cabeça triangular, pernas articuladas, **foices orgânicas** |
| 2 | `scarab_brute` | Besouro de seis patas | Carapaça cúpula horizontal, chifre frontal, **sem braços humanos** |
| 3 | `moth_hexer` | Mariposa alada | Antenas plumosas e **asas em manto**, corpo fino |
| 4 | `termite_burrower` | Térmita rastejante | Corpo baixo escavador, mandíbulas de broca |
| 5 | `vespa_lancer` | Vespa de voo | Cintura fina, quatro asas, abdômen em ferrão articulado |
| 6 | `cicada_screecher` | Cigarra sônica | Tórax ressonador, asas translúcidas de veias aparentes |
| 7 | `ant_guard` | Formiga soldado | Três segmentos, mandíbulas largas, marcha em seis patas |
| 8 | `roach_plaguebearer` | Barata pestilenta | Corpo achatado, antenas longas, patas nervosas |
| 9 | `spike_beetle` | Tatuzinho espinhoso | Corpo segmentado que se fecha **em esfera**, diferente do escaravelho |
| 10 | `dragonfly_skirmisher` | Libélula predadora | Quatro asas longas independentes e cauda extremamente fina |
| 11 | `mantis_high_reaper` | Boss: ceifador mantídeo | Quatro braços-facão, quatro pernas, torso-torre original |
| 12 | `scarab_colossus` | Boss: fortaleza viva | **Oito apoios**, carapaça bipartida, cristal interno |
| 13 | `moth_oracle` | Boss: oráculo alado | Roseta de asas como vitral, olhos nos padrões e corpo espectral |
| 14 | `queen_vespara` | Boss: rainha-vespa | Seis membros, quatro asas, longo abdômen real articulado |
| 15 | `brood_tyrant` | Boss: tirano da ninhada | Corpo assimétrico, dez patas, sacos de ovos e mandíbulas duplas |

## Etapas e critérios de liberação

**Piloto (1–3):** começar por três morfologias extremas — mantis, besouro e mariposa. Produzir *somente* esses três, renderizar folhas PNG + JSON e comparar máscaras pretas. Conferir poses `down/up/side`, ataque e magia, contorno, cel shading e enquadramento. Se forem parecidos, refazer o rig **antes de avançar**.

**Segunda leva (4–6):** produzir escavador, vespa e cigarra com locomotores totalmente distintos (terra, voo perfurante e vibração), além de habilidades próprias.

**Terceira leva (7–10):** criar formiga, barata, besouro rolante e libélula. O besouro rolante não reutiliza o domo do `scarab_brute`.

**Chefes A (11–13):** desenvolver novos rigs maiores para ceifador, escaravelho-colosso e mariposa-oráculo; **não** ampliar sprites de demônios comuns. Animações independentes de ataque, `cast` e `skill_2`.

**Chefes B (14–15):** rainha-vespa e tirano da ninhada, com leitura de telegraph, múltiplos apêndices e animadores de pernas/cauda próprios.

## Padrão de animação / validação

- Cada demônio: `idle`, `move`, `attack`, `cast` (habilidade), `hurt`, `death` × três direções.
- Cada chefe: estados anteriores + `skill_2` × três direções.
- Sprite sheet e JSON compatíveis com `SpriteAnim`; `hit` zero-indexado no quadro de ação.
- Verificar **silhueta em preto** sem detalhes: espécie e papel devem ser reconhecidos sem arma, cor ou legenda.
- Arquivos HD RGBA originais e scripts geradores preservados por IDs persistentes.
- Registrar VFX e telegraph de cada habilidade por ID próprio, sem efeitos genéricos reciclados como solução final.
- Prévia de atlas não é screenshot do jogo; somente capturas realmente obtidas na Unity poderão ser chamadas de prints do jogo.
- **Não declarar aprovado** até inspeção da arte, execução na Unity 2022.3 LTS e checagem de escala/colisão/desempenho.

Detalhes estruturados: [`lote2_priority.json`](lote2_priority.json).

**Status:** fila de produção definida, **sprites do Lote 2 ainda não foram criados**. A prioridade é resolver primeiro a repetição do Lote 1.

## CRITÉRIO DE ENTREGA OBRIGATÓRIO — definido pelo diretor em 12/10/2026

**[Ler a regra de assets jogáveis](REGRA_OBRIGATORIA_ASSETS_JOGAVEIS.md) antes de produzir qualquer criatura.** O usuário não aceita **arte conceitual** como entrega. Atlas isolado ou PNG de demonstração também não é criatura concluída. Cada demônio/chefe precisa estar **integrado ao jogo Unity**, com rig/sprites refinados, animações reais, IA de movimentação, ataque e habilidades ativáveis, VFX, hitboxes, eventos de dano, cooldown e testes em cena. Chefes devem ter duas habilidades independentes. Somente após funcionamento comprovado e revisão visual considerar o asset concluído.

**Piloto efetivamente jogável:** priorizar `mantis_reaver`, `scarab_brute`, `moth_hexer`; para cada um, concluir o ciclo asset → importação → movimento → combate → habilidades → testes reais de Unity antes de avançar no lote. As imagens ilustrativas/atlas geradas fora de Unity nas conversas anteriores **não constituem assets funcionais** e não autorizam marcar esses três como implementados.
