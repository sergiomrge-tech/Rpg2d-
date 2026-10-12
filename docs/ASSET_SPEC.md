# Especificação de Assets (para qualquer colaborador, humano ou IA)

Siga isto para que o asset entre no jogo **sem retrabalho**. Base: branch `ccr-f2d39ca4-hkguyt`.

## Estilo
- HD cartoon (referência: *Happy Harvest*): contorno colorido escuro (~1 px), cor base chapada, sombra em crescente para baixo-direita,
  brilho fino para cima-esquerda (luz vindo do alto-esquerda). Nada de pixel art, nada de low poly.
- Inimigos são **demônios** (não animais/insetos comuns). Silhueta legível a 100 % de zoom.
- Use o pipeline existente: `tools/art_hd/core.py` (`paint`, `Pal`, `outline_rgba`), rigs `humanoid.py` / `demons.py`.

## Personagens e inimigos (sprite sheet)
- Arquivos: `unity/Assets/Resources/Sprites/Demons/<id>.png` + `<id>.json` (formato de `tools/art_hd/sheet.py`).
- JSON: `frameW, frameH, pivotX, pivotY (de baixo), cols, anims[{name,start,count,fps,loop,hit}]`.
- **Animações obrigatórias** × **3 vistas** (`_down`, `_up`, `_side` virado para a direita):
  `idle` (≥8 q.), `move` (≥8), `attack` (≥8, `hit` = quadro do impacto), `cast` (≥8), `hurt` (≥4), `death` (≥10).
- **Cada vista precisa ser desenhada de verdade**: costas sem rosto, perfil de lado. Cada estado precisa de pose diferente
  (preparação → golpe → recuperação no ataque). Quadros quase iguais = reprovado.
- Tamanho do quadro: comuns ≤ 192 px, chefes ≤ 256 px. **Recorte espaço vazio.** Pivô nos pés.

## Orçamento de memória (por folha, descompactada)
- Inimigo comum ≤ 16 MB · chefe ≤ 32 MB · região inteira ≤ 400 MB (PC). Folha > 4096 × 4096 = reprovada.

## Cenário (props)
- `Sprites/Env/<nome>.png`, ponto base = pé do objeto; registrar em `props.json` (pivô + caixa de colisão).
- Vista 3/4 de cima, sombra suave embutida, mesma paleta da vila.

## Mapas
- Gerados em `tools/art_hd/maps.py` (formas vetoriais → chão pintado + JSON com props, spawns, NPCs, saídas).

## Etapa 2 — o que é necessário
| Item | Tipo | Notas |
|---|---|---|
| Floresta de Velmoor | mapa + props | árvores retorcidas/corrompidas, cogumelos brilhantes, raízes, névoa, ruínas élficas |
| Sylra (companheira elfa) | humanoide | arqueira; todas as anims do herói + `shoot` |
| Dríade Profanada | chefe | árvore-demônio; 2 fases; `skill_2` = raízes do chão |
| Espíritos corrompidos, Treant-demônio, Lobo-sombra demoníaco | inimigos | 6 anims × 3 vistas |
| Cidade de Valemont | mapa + props | muralhas, mercado, Guilda principal, catedral, casas de 2 andares |
| NPCs de Valemont (8+) | humanoides | guarda, mercador, nobre, clérigo, crianças |
| Assassino Sombrio | chefe | teleporte + clones |
| Corte Crescente / Centelha II | FX | já existe base em `fx.py` |

## Entrega
- Um PR por pacote, **contra `ccr-f2d39ca4-hkguyt`**, sem mexer em `Scripts/` (o código de integração é feito aqui).
- Incluir prévia `docs/previews/<pacote>.png` com idle/move/attack nas 3 vistas.
