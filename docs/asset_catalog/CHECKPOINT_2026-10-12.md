# CHECKPOINT — Crônicas de Aetheria (12/10/2026)

**Este documento é o estado verificável do GitHub; não significa que a Unity foi executada com sucesso.**
Projeto: `sergiomrge-tech/Rpg2d-` · Engine: **Unity 2022.3 LTS** · Visual: **HD cartoon aprovado**, preservado sem substituição dos sprites originais. Não confundir este projeto com outros RPGs do usuário.

## Situação das branches

- **`main`**: branch padrão; **não contém as expansões abaixo**. Nenhum PR listado aqui está mesclado na `main`.
- **`ccr-f2d39ca4-hkguyt`**: base original do jogo (Capítulo 1).
- **`gpt6-demon-catalog-20261012` → `gpt6-lote1-all-sprites-20261012` → `gpt6-lote1-silhouettes-20261012`**: catálogo e folhas de sprites de 10 demônios/5 chefes do Lote 1, incluindo **oito remodelagens anatômicas** para eliminar repetição. Arte candidata; a maior parte não está ligada ao gameplay.
- **`gpt6-lote2-pilot-playable-20261012` → `gpt6-lote2-set-a-20261012` → `gpt6-lote2-set-b-20261012` → `gpt6-lote2-five-bosses-20261012`**: cadeia incremental do Lote 2 com **10 demônios + 5 chefes** e os respectivos scripts de combate, animações e mapa.
- `gpt6-hud-assets-20261012` e `gpt6-save-resilience-20261012` são melhorias em PRs **separados**; não estão automaticamente incluídas nesta cadeia. Não supor que se encontram na branch mais recente.

## Lote 2 — implementação verificável

### Dez demônios insetoides

| ID | Movimento/identidade de combate |
|---|---|
| `mantis_reaver` | Louva-a-deus, avanço com foices |
| `scarab_brute` | Escaravelho, impacto em área |
| `moth_hexer` | Mariposa, projétil de maldição/lentidão |
| `termite_burrower` | Térmita, deslocamento escavador e emergência |
| `vespa_lancer` | Vespa, mergulho com ferrão e veneno |
| `cicada_screecher` | Cigarra, onda sônica e interrupção breve |
| `ant_guard` | Formiga, defesa temporária de carapaça |
| `roach_plaguebearer` | Barata, nuvem tóxica persistente |
| `spike_beetle` | Inseto segmentado, investida rolante |
| `dragonfly_skirmisher` | Libélula, zigue-zague e agulhas luminosas |

Cada demônio possui **atlas PNG RGBA e JSON de 18 trilhas** (6 estados × 3 direções), arquivos na pasta `unity/Assets/Resources/Sprites/Demons/`, registro em `Data.Demons`, comportamento em `Enemy.cs` e **um spawn no mapa** `unity/Assets/Resources/Maps/village.json`.

### Cinco chefes insetoides

| ID | Anatomia própria e duas habilidades |
|---|---|
| `mantis_high_reaper` | Ceifador de foices múltiplas; golpes e salto de execução |
| `scarab_colossus` | Fortaleza de oito apoios; terremoto e defesa com carapaça |
| `moth_oracle` | Asas rituais; esporos e mandala |
| `queen_vespara` | Vespa-rainha; projéteis venenosos e mergulho |
| `brood_tyrant` | Colmeia móvel; invocação de prole e ruptura corrosiva |

Cada chefe possui **atlas PNG RGBA de 3840×8064, JSON com 21 trilhas (7 estados × 3 direções) e 201 quadros**: **105 trilhas e 1.005 quadros no conjunto**. Os chefes são **novos rigs**, não inimigos comuns ampliados. As duas habilidades por chefe estão **codificadas** em `InsectBossSkills.cs` e conectadas a `Enemy.cs`; o HUD, os dados, os cinco encontros opcionais e o importador de texturas foram atualizados.

**Totais do Lote 2:** 15 criaturas com arte PNG/JSON e scripts associados; **285 trilhas de animação** (10 × 18 + 5 × 21), **23 spawns** no mapa ao todo (8 diabretes originais + 10 insetoides + 5 chefes). O código implementa movimentos, eventos de impacto, habilidades, cooldowns e efeitos; **a jogabilidade real ainda não foi observada numa sessão Unity**.

## Evidências de CI — trabalhos concluídos com sucesso

| Gate | GitHub Actions |
|---|---|
| Piloto: três insetoides, arte | [38250595227](https://github.com/sergiomrge-tech/Rpg2d-/actions/runs/38250595227) |
| Piloto: C# e vínculos | [38250476157](https://github.com/sergiomrge-tech/Rpg2d-/actions/runs/38250476157) |
| Set A: arte | [38251352087](https://github.com/sergiomrge-tech/Rpg2d-/actions/runs/38251352087) |
| Set A: C# e vínculos | [38252014658](https://github.com/sergiomrge-tech/Rpg2d-/actions/runs/38252014658) |
| Set B: arte | [38252630731](https://github.com/sergiomrge-tech/Rpg2d-/actions/runs/38252630731) |
| Set B: C# e vínculos | [38253369537](https://github.com/sergiomrge-tech/Rpg2d-/actions/runs/38253369537) |
| Cinco chefes: C# e contratos | [38259238033](https://github.com/sergiomrge-tech/Rpg2d-/actions/runs/38259238033) |
| Cinco chefes: folhas PNG e animação | [38259382034](https://github.com/sergiomrge-tech/Rpg2d-/actions/runs/38259382034) |

Esses gates verificam arquivos, metadados, renderização, compilação C# com referências UnityEngine e contratos estáticos. **Não equivalem a build jogável, FPS medido ou screenshot real da Unity.**

## Pull requests para revisar sem perder histórico

| PR | Trabalho | Base |
|---|---|---|
| [#3](https://github.com/sergiomrge-tech/Rpg2d-/pull/3) | Base do catálogo Lote 1 | `ccr-f2d39ca4-hkguyt` |
| [#4](https://github.com/sergiomrge-tech/Rpg2d-/pull/4) | Sprite sheets Lote 1 | Branch #3 |
| [#5](https://github.com/sergiomrge-tech/Rpg2d-/pull/5) | Remodelagem 8 silhuetas | Branch #4 |
| [#7](https://github.com/sergiomrge-tech/Rpg2d-/pull/7) | Lote 2 piloto | Branch #5 |
| [#8](https://github.com/sergiomrge-tech/Rpg2d-/pull/8) | Lote 2 Set A | Branch #7 |
| [#9](https://github.com/sergiomrge-tech/Rpg2d-/pull/9) | Lote 2 Set B | Branch #8 |
| [#10](https://github.com/sergiomrge-tech/Rpg2d-/pull/10) | Lote 2: 5 chefes | Branch #9 |
| [#2](https://github.com/sergiomrge-tech/Rpg2d-/pull/2) | HUD — independente | Base original |
| [#1](https://github.com/sergiomrge-tech/Rpg2d-/pull/1) | Save resiliente — independente | Base original |

**O PR #6 é um piloto paralelo e não pertence à cadeia canônica #7 → #10.** Evitar mesclá-lo por cima da outra implementação sem revisão de conflitos/duplicações.

## Bloqueios e prioridades seguintes

1. **Obrigatório:** rodar `unity/` no **Unity 2022.3 LTS** e verificar importação, parsing real, executabilidade, animações, escalas, direções, colisões, spawn, AI, dano, movimentação, boss bars e FPS. Não declarar essas verificações concluídas até ter logs e capturas autênticas do jogo.
2. **Gate artístico:** comparar com o padrão HD cartoon aprovado; elevar refinamento de carapaças, sombra, anatomia, articulação, VFX e leitura em escala real conforme necessidade, **sem trocar estilo, recolorir o mesmo rig ou simplificar a arte**.
3. **Performance:** cinco PNGs de chefes muito grandes (3840×8064, ~119 MiB RGBA descomprimidos cada). Medir memória, importação e tempo de carregamento no Editor e considerar particionamento sem perda gráfica se necessário. Verificar `Max Texture Size` e plataforma-alvo.
4. **Conteúdo:** não misturar a implementação do Lote 2 com o Lote 1 ainda pendente de aprovação, nem com as melhorias independentes de HUD/save, sem análise dos PRs.
5. **Extensão futura:** o plano global de 30 demônios + 20 chefes ainda tem conteúdo a produzir, após validação do jogo atual.

## Regra permanente do usuário

**Sem arte conceitual como entrega de desenvolvimento.** Criar **assets utilizáveis no jogo**, com animações `idle/move/attack/cast/hurt/death` em `down/up/side`; chefes também com `skill_2`. Cada criatura precisa ter corpo e movimentos próprios, habilidades funcionais, hitbox/dano/cooldown/VFX. Prévia de quadros pode ser chamada apenas de **prévia de sprites**; `screenshot do jogo` somente se capturado em execução real da Unity.

Consultar também [regra obrigatória](REGRA_OBRIGATORIA_ASSETS_JOGAVEIS.md), [ordem de produção](LOTE2_ORDEM_PRODUCAO.md), [planejamento estruturado](lote2_priority.json) e [roadmap](../ROADMAP.md).

**Não aprovar merge dos PRs draft nem release sem gate visual e runtime Unity.**
