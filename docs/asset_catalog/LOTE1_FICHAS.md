# LOTE 1 — Fichas de produção de demônios e chefes

## Escopo e preservação visual

Primeira etapa do repertório maior de **30 demônios + 20 chefes**. Este documento cobre **10 demônios e 5 chefes**, em Unity 2022.3 LTS. A estética oficial **HD cartoon** é obrigatória: as mesmas técnicas de sombreamento Cairo, contornos coloridos, proporções e nível de detalhe. **Não substituir nenhum sprite aprovado.**

**Status real:** apenas **Oni Soldado** e **Grakk** já possuem folhas PNG e JSON gerados, ainda pendentes de aprovação visual no Unity. Para Grakk, a animação de segunda habilidade está *planejada*, não renderizada. As outras 13 criaturas são fichas de produção — suas imagens, VFX, IA e habilidades ainda não estão implementados.

## Contrato de animação

- Todas as criaturas: `idle`, `move`, `attack`, `cast` (primeira habilidade), `hurt`, `death`; chefes têm ainda `skill_2` (segunda habilidade).
- Cada estado em três direções: `down`, `up`, `side`; movimento para esquerda usa `side` espelhado, respeitando `SpriteAnim`.
- `event_frame` começa no **índice zero**, é usado na emissão de dano / projétil / buff no `OnHit` do Unity. Não é um sistema de colisão pronto.
- `idle` e `move` são loops. Ações, dano e morte têm término (sem loop).
- Telegrafias devem anteceder danos; efeitos, hitbox e área de habilidade usam IDs próprios e precisam de implementação em gameplay.

### Tabela geral

| ID | Papel | Sprite (px) | Estados × direções | Quadros previstos | Prioridade | Arte atual |
|---|---|---:|---:|---:|---|---|
| `imp_scout` | recon_melee | 144×144 | 6 × 3 | 150 | 1 | Falta gerar |
| `imp_raider` | aggressive_melee | 144×144 | 6 × 3 | 162 | 3 | Falta gerar |
| `imp_pyro` | ranged_fire | 144×144 | 6 × 3 | 159 | 1 | Falta gerar |
| `imp_hexer` | ranged_hex | 160×160 | 6 × 3 | 171 | 2 | Falta gerar |
| `imp_bomber` | area_denial | 160×160 | 6 × 3 | 171 | 3 | Falta gerar |
| `imp_howler` | support | 160×160 | 6 × 3 | 165 | 2 | Falta gerar |
| `oni_soldier` | armored_melee | 192×192 | 6 × 3 | 174 | 1 | Gerada, sob revisão |
| `oni_lancer` | spacing_elite | 192×192 | 6 × 3 | 180 | 2 | Falta gerar |
| `oni_shielder` | front_guard | 208×192 | 6 × 3 | 177 | 2 | Falta gerar |
| `oni_executioner` | heavy_elite | 224×224 | 6 × 3 | 198 | 3 | Falta gerar |
| `grakk` | chapter_1_boss | 192×192 | 7 × 3 | 219 | 1 | Gerada, sob revisão |
| `morgash_ironhorn` | optional_boss | 256×256 | 7 × 3 | 279 | 2 | Falta gerar |
| `velka_flamebeak` | optional_boss | 256×224 | 7 × 3 | 273 | 3 | Falta gerar |
| `krull_chainlord` | optional_boss | 256×256 | 7 × 3 | 273 | 3 | Falta gerar |
| `thornmaw_alpha` | optional_boss | 288×256 | 7 × 3 | 273 | 3 | Falta gerar |

## Fichas individuais

### Diabrete Batedor — `imp_scout`
**Função:** recon_melee · **Região candidata:** Bosque dos Chifres · **Rig:** imp.
**Silhueta:** Corpo estreito, asas finas, chifres curtos, adaga curva e olhos âmbar.
**Movimentação:** `circle_strafe`; três ângulos, espelhamento lateral. **Quadro:** 144×144; pivô (72, 16).
**Animações por direção:** `idle` 10q/12FPS · `move` 8q/16FPS · `attack` 8q/18FPS [evento 4] · `cast` 9q/17FPS [evento 5] · `hurt` 5q/14FPS · `death` 10q/12FPS.
**Ataques e habilidades:** Corte de adaga (`attack`, aviso 0.34s, recarga 1.3s, FX previsto `imp_scout_attack_fx`); Dash lateral (`cast`, aviso 0.5s, recarga 4.4s, FX previsto `imp_scout_skill1_fx`).
**Situação:** ficha aprovada para produção técnica; sprites ainda não gerados.

### Diabrete Saqueador — `imp_raider`
**Função:** aggressive_melee · **Região candidata:** Bosque dos Chifres · **Rig:** imp.
**Silhueta:** Pele vinho, dentes proeminentes, sucata no ombro e faca serrilhada.
**Movimentação:** `direct_chase`; três ângulos, espelhamento lateral. **Quadro:** 144×144; pivô (72, 16).
**Animações por direção:** `idle` 10q/11FPS · `move` 9q/14FPS · `attack` 10q/17FPS [evento 5] · `cast` 10q/16FPS [evento 5] · `hurt` 5q/14FPS · `death` 10q/12FPS.
**Ataques e habilidades:** Combo serrilhado (`attack`, aviso 0.34s, recarga 1.3s, FX previsto `imp_raider_attack_fx`); Investida brutal (`cast`, aviso 0.5s, recarga 4.4s, FX previsto `imp_raider_skill1_fx`).
**Situação:** ficha aprovada para produção técnica; sprites ainda não gerados.

### Diabrete Piromaníaco — `imp_pyro`
**Função:** ranged_fire · **Região candidata:** Clareiras queimadas · **Rig:** imp.
**Silhueta:** Pele de brasa, mãos incandescentes, membranas chamuscadas e cauda em chama.
**Movimentação:** `kite`; três ângulos, espelhamento lateral. **Quadro:** 144×144; pivô (72, 16).
**Animações por direção:** `idle` 10q/12FPS · `move` 8q/14FPS · `attack` 9q/16FPS [evento 4] · `cast` 11q/14FPS [evento 7] · `hurt` 5q/14FPS · `death` 10q/12FPS.
**Ataques e habilidades:** Garra flamejante (`attack`, aviso 0.34s, recarga 1.3s, FX previsto `imp_pyro_attack_fx`); Bola de fogo (`cast`, aviso 0.5s, recarga 4.4s, FX previsto `imp_pyro_skill1_fx`).
**Situação:** ficha aprovada para produção técnica; sprites ainda não gerados.

### Diabrete Ocultista — `imp_hexer`
**Função:** ranged_hex · **Região candidata:** Ruínas corrompidas · **Rig:** imp.
**Silhueta:** Marcas arcanas violetas, bastão com cristal e halo sombrio translúcido.
**Movimentação:** `ranged_cover`; três ângulos, espelhamento lateral. **Quadro:** 160×160; pivô (80, 18).
**Animações por direção:** `idle` 10q/10FPS · `move` 10q/13FPS · `attack` 9q/14FPS [evento 4] · `cast` 12q/14FPS [evento 7] · `hurt` 5q/14FPS · `death` 11q/12FPS.
**Ataques e habilidades:** Toque amaldiçoado (`attack`, aviso 0.34s, recarga 1.3s, FX previsto `imp_hexer_attack_fx`); Orbe de maldição que reduz velocidade (`cast`, aviso 0.5s, recarga 4.4s, FX previsto `imp_hexer_skill1_fx`).
**Situação:** ficha aprovada para produção técnica; sprites ainda não gerados.

### Diabrete Bombardeiro — `imp_bomber`
**Função:** area_denial · **Região candidata:** Trilhas demoníacas · **Rig:** imp.
**Silhueta:** Alforjes repletos de bombas, cintos de couro e pavios brilhantes.
**Movimentação:** `kite_cover`; três ângulos, espelhamento lateral. **Quadro:** 160×160; pivô (80, 18).
**Animações por direção:** `idle` 10q/11FPS · `move` 9q/13FPS · `attack` 9q/15FPS [evento 5] · `cast` 13q/14FPS [evento 9] · `hurt` 5q/14FPS · `death` 11q/12FPS.
**Ataques e habilidades:** Golpe de bomba curta (`attack`, aviso 0.34s, recarga 1.3s, FX previsto `imp_bomber_attack_fx`); Arremesso explosivo com área marcada (`cast`, aviso 0.5s, recarga 4.4s, FX previsto `imp_bomber_skill1_fx`).
**Situação:** ficha aprovada para produção técnica; sprites ainda não gerados.

### Diabrete Uivador — `imp_howler`
**Função:** support · **Região candidata:** Bosque dos Chifres · **Rig:** imp.
**Silhueta:** Garganta e peito expandidos, espinhos cervicais com runas e olhos dourados.
**Movimentação:** `support_distance`; três ângulos, espelhamento lateral. **Quadro:** 160×160; pivô (80, 18).
**Animações por direção:** `idle` 10q/10FPS · `move` 8q/12FPS · `attack` 9q/15FPS [evento 4] · `cast` 12q/14FPS [evento 8] · `hurt` 5q/14FPS · `death` 11q/12FPS.
**Ataques e habilidades:** Arranhão de defesa (`attack`, aviso 0.34s, recarga 1.3s, FX previsto `imp_howler_attack_fx`); Uivo que fortalece aliados próximos (`cast`, aviso 0.5s, recarga 4.4s, FX previsto `imp_howler_skill1_fx`).
**Situação:** ficha aprovada para produção técnica; sprites ainda não gerados.

### Oni Soldado de Ferro — `oni_soldier`
**Função:** armored_melee · **Região candidata:** Acampamento demoníaco · **Rig:** humanoid.
**Silhueta:** Armadura de ferro, clava cravejada, chifres e runa no peito.
**Movimentação:** `slow_chase`; três ângulos, espelhamento lateral. **Quadro:** 192×192; pivô (96, 26).
**Animações por direção:** `idle` 10q/10FPS · `move` 10q/13FPS · `attack` 11q/17FPS [evento 6] · `cast` 10q/14FPS [evento 6] · `hurt` 5q/14FPS · `death` 12q/12FPS.
**Ataques e habilidades:** Pancada de clava (`attack`, aviso 0.34s, recarga 1.3s, FX previsto `oni_soldier_attack_fx`); Esmagamento com knockback (`cast`, aviso 0.5s, recarga 4.4s, FX previsto `oni_soldier_skill1_fx`).
**Situação:** sprites dos seis estados-base gerados; aguardando aprovação da qualidade em execução real.

### Oni Lanceiro — `oni_lancer`
**Função:** spacing_elite · **Região candidata:** Patrulhas demoníacas · **Rig:** humanoid.
**Silhueta:** Lança bifurcada, armadura estreita e chifres reclinados.
**Movimentação:** `spacing_strafe`; três ângulos, espelhamento lateral. **Quadro:** 192×192; pivô (96, 26).
**Animações por direção:** `idle` 10q/10FPS · `move` 10q/13FPS · `attack` 11q/17FPS [evento 6] · `cast` 12q/15FPS [evento 7] · `hurt` 5q/14FPS · `death` 12q/12FPS.
**Ataques e habilidades:** Estocada longa (`attack`, aviso 0.34s, recarga 1.3s, FX previsto `oni_lancer_attack_fx`); Investida perfurante com linha de aviso (`cast`, aviso 0.5s, recarga 4.4s, FX previsto `oni_lancer_skill1_fx`).
**Situação:** ficha aprovada para produção técnica; sprites ainda não gerados.

### Oni Escudeiro — `oni_shielder`
**Função:** front_guard · **Região candidata:** Fortificações demoníacas · **Rig:** humanoid.
**Silhueta:** Escudo infernal alto, chifre quebrado, elmo parcial e peito blindado.
**Movimentação:** `block_approach`; três ângulos, espelhamento lateral. **Quadro:** 208×192; pivô (104, 26).
**Animações por direção:** `idle` 10q/9FPS · `move` 10q/12FPS · `attack` 10q/15FPS [evento 6] · `cast` 12q/14FPS [evento 7] · `hurt` 5q/14FPS · `death` 12q/12FPS.
**Ataques e habilidades:** Golpe de escudo (`attack`, aviso 0.34s, recarga 1.3s, FX previsto `oni_shielder_attack_fx`); Escudada com postura reforçada (`cast`, aviso 0.5s, recarga 4.4s, FX previsto `oni_shielder_skill1_fx`).
**Situação:** ficha aprovada para produção técnica; sprites ainda não gerados.

### Oni Carrasco — `oni_executioner`
**Função:** heavy_elite · **Região candidata:** Clareiras de execução · **Rig:** humanoid.
**Silhueta:** Machado colossal, máscara de ferro, chifres largos e avental de batalha.
**Movimentação:** `heavy_pursuit`; três ângulos, espelhamento lateral. **Quadro:** 224×224; pivô (112, 30).
**Animações por direção:** `idle` 10q/8FPS · `move` 10q/11FPS · `attack` 13q/16FPS [evento 8] · `cast` 14q/14FPS [evento 10] · `hurt` 6q/14FPS · `death` 13q/12FPS.
**Ataques e habilidades:** Golpe amplo de machado (`attack`, aviso 0.34s, recarga 1.3s, FX previsto `oni_executioner_attack_fx`); Esmagamento carregado no solo (`cast`, aviso 0.5s, recarga 4.4s, FX previsto `oni_executioner_skill1_fx`).
**Situação:** ficha aprovada para produção técnica; sprites ainda não gerados.

### Grakk, Diabrete-Chefe — `grakk`
**Função:** chapter_1_boss · **Região candidata:** Bosque dos Chifres · **Rig:** imp_boss.
**Silhueta:** Asas violáceas, coroa irregular, armadura de bronze e runa azul no peito.
**Movimentação:** `hybrid_boss`; três ângulos, espelhamento lateral. **Quadro:** 192×192; pivô (96, 32).
**Animações por direção:** `idle` 10q/11FPS · `move` 10q/13FPS · `attack` 11q/16FPS [evento 6] · `cast` 11q/14FPS [evento 7] · `hurt` 6q/14FPS · `death` 12q/12FPS · `skill_2` 13q/16FPS [evento 8].
**Ataques e habilidades:** Combo feroz de garras (`attack`, aviso 0.48s, recarga 1.9s, FX previsto `grakk_attack_fx`); Orbe ígneo rúnico (`cast`, aviso 0.7s, recarga 6s, FX previsto `grakk_skill1_fx`); Investida alada com impacto (`skill_2`, aviso 0.85s, recarga 8.5s, FX previsto `grakk_skill2_fx`).
**Situação:** sprites dos seis estados-base gerados; aguardando aprovação da qualidade em execução real.

### Morgash Chifre de Ferro — `morgash_ironhorn`
**Função:** optional_boss · **Região candidata:** Posto fortificado demoníaco · **Rig:** humanoid_boss.
**Silhueta:** Oni colossal com chifres de metal, marreta de cerco e armadura em brasa.
**Movimentação:** `heavy_boss`; três ângulos, espelhamento lateral. **Quadro:** 256×256; pivô (128, 34).
**Animações por direção:** `idle` 12q/8FPS · `move` 12q/11FPS · `attack` 14q/16FPS [evento 8] · `cast` 16q/14FPS [evento 10] · `hurt` 7q/14FPS · `death` 16q/12FPS · `skill_2` 16q/14FPS [evento 9].
**Ataques e habilidades:** Marretada frontal (`attack`, aviso 0.48s, recarga 1.9s, FX previsto `morgash_ironhorn_attack_fx`); Salto com onda de impacto (`cast`, aviso 0.7s, recarga 6s, FX previsto `morgash_ironhorn_skill1_fx`); Rugido com fortalecimento de golpes (`skill_2`, aviso 0.85s, recarga 8.5s, FX previsto `morgash_ironhorn_skill2_fx`).
**Situação:** ficha aprovada para produção técnica; sprites ainda não gerados.

### Velka Bico de Chama — `velka_flamebeak`
**Função:** optional_boss · **Região candidata:** Penhascos corrompidos · **Rig:** harpy_custom.
**Silhueta:** Harpia de asas largas em forma de leque, bico incandescente e penas de fogo.
**Movimentação:** `flight_orbit`; três ângulos, espelhamento lateral. **Quadro:** 256×224; pivô (128, 32).
**Animações por direção:** `idle` 12q/12FPS · `move` 12q/15FPS · `attack` 14q/19FPS [evento 7] · `cast` 16q/15FPS [evento 10] · `hurt` 7q/14FPS · `death` 15q/12FPS · `skill_2` 15q/15FPS [evento 9].
**Ataques e habilidades:** Rasante com garras (`attack`, aviso 0.48s, recarga 1.9s, FX previsto `velka_flamebeak_attack_fx`); Chuva de chamas com círculos de aviso (`cast`, aviso 0.7s, recarga 6s, FX previsto `velka_flamebeak_skill1_fx`); Grito flamejante em cone (`skill_2`, aviso 0.85s, recarga 8.5s, FX previsto `velka_flamebeak_skill2_fx`).
**Situação:** ficha aprovada para produção técnica; sprites ainda não gerados.

### Krull Senhor das Correntes — `krull_chainlord`
**Função:** optional_boss · **Região candidata:** Prisão demoníaca · **Rig:** humanoid_boss.
**Silhueta:** Correntes encantadas articuladas, máscara fraturada e brilho azul-esverdeado.
**Movimentação:** `control_spacing`; três ângulos, espelhamento lateral. **Quadro:** 256×256; pivô (128, 32).
**Animações por direção:** `idle` 12q/10FPS · `move` 12q/12FPS · `attack` 14q/16FPS [evento 8] · `cast` 15q/14FPS [evento 9] · `hurt` 6q/14FPS · `death` 15q/12FPS · `skill_2` 17q/16FPS [evento 10].
**Ataques e habilidades:** Chicote de corrente (`attack`, aviso 0.48s, recarga 1.9s, FX previsto `krull_chainlord_attack_fx`); Laço puxador com aviso de trajetória (`cast`, aviso 0.7s, recarga 6s, FX previsto `krull_chainlord_skill1_fx`); Giro circular de correntes (`skill_2`, aviso 0.85s, recarga 8.5s, FX previsto `krull_chainlord_skill2_fx`).
**Situação:** ficha aprovada para produção técnica; sprites ainda não gerados.

### Alfa Espinhagorja — `thornmaw_alpha`
**Função:** optional_boss · **Região candidata:** Clareiras corrompidas · **Rig:** quadruped_custom.
**Silhueta:** Quadrúpede volumoso, espinhos dorsais, placas ósseas e mandíbula pesada.
**Movimentação:** `predator_ambush`; três ângulos, espelhamento lateral. **Quadro:** 288×256; pivô (144, 42).
**Animações por direção:** `idle` 12q/9FPS · `move` 12q/14FPS · `attack` 13q/16FPS [evento 7] · `cast` 15q/14FPS [evento 9] · `hurt` 7q/14FPS · `death` 17q/12FPS · `skill_2` 15q/16FPS [evento 10].
**Ataques e habilidades:** Mordida brutal (`attack`, aviso 0.48s, recarga 1.9s, FX previsto `thornmaw_alpha_attack_fx`); Rajada de espinhos (`cast`, aviso 0.7s, recarga 6s, FX previsto `thornmaw_alpha_skill1_fx`); Carga bestial em linha (`skill_2`, aviso 0.85s, recarga 8.5s, FX previsto `thornmaw_alpha_skill2_fx`).
**Situação:** ficha aprovada para produção técnica; sprites ainda não gerados.

## QA antes da integração

1. Validar JSON e coerência das duas folhas existentes com `python tools/art_hd/verify_lote1.py`.
2. Produzir assets isolados, registrar os PNG/JSON no catálogo por ID persistente e validar quadros/contornos e animações.
3. Capturar sprites animados no **Unity em execução real**, com proporção, hitbox, colisão e ordem de desenho; não usar mockup como screenshot.
4. Implementar estados e mecânicas de cada habilidade e os efeitos com seus IDs originais; rodar testes reais de impacto, aviso, cooldown, loot e progressão.
5. Solicitar aprovação visual antes de distribuir criaturas pelo mapa ou elevar status a integrado.

**Importante:** os chefes opcionais não substituem os chefes narrativos dos dez capítulos em `docs/GAME_DESIGN.md`.
