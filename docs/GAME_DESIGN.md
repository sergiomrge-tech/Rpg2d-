# Game Design — Crônicas de Aetheria: A Centelha

## Visão
RPG de ação 2D top-down (3/4), estilo HD cartoon (*Happy Harvest*), campanha de ~30 h.
Difícil desde o início, com combate legível (ataques telegrafados), drops importantes e habilidades que **evoluem visualmente**.
HUD sem caixas: arcos, medalhões, orbes, faixas cinematográficas.

## História (isekai)
**Ren Takamura**, funcionário de escritório em Tóquio, morre ao salvar uma criança de um caminhão.
A deusa **Lumia** o leva para **Aetheria**, mundo sendo devorado pelo Rei Demônio **Malgrath**.
Ela não pode lhe dar poder — apenas uma **centelha** de magia. Ren começa fraco, entra na **Guilda dos Aventureiros** no Rank F e cresce até enfrentar Malgrath.

### Capítulos (implementados)
| # | Região | Rank ao concluir | Chefe |
|---|---|---|---|
| 1 | Vila de Aurora + Bosque dos Chifres | E | Grakk, Chefe dos Diabretes |
| 2 | Floresta de Velmoor (companheira **Sylra**) | D | Dríade Profanada |
| 3 | Cidade de Valemont | C | Assassino Sombrio |
| 4 | Deserto de Kharis | B | Demônio Escorpião |
| 5 | Minas de Durnhold | B | Golem de Brasa |
| 6 | Pântano de Mirewail | A | Mirael, a Súcubo |
| 7 | Picos Gelados (Templo de Lumia) | A | Demônio de Gelo |
| 8 | Castelo de Valemont tomado | A | General Vorath |
| 9 | Terras Devastadas | S | Os 4 Generais (Thornmaw, Velka, Krull, Morgash) |
| 10 | Cidadela de Malgrath | — | **Malgrath, o Rei Demônio** (3 fases) |

## Combate
- **Stamina:** atacar, rolar e correr gastam; sem fôlego = vulnerável.
- **Combo de espada ×3** com avanço; o 3º golpe é pesado (onda de choque, quebra postura).
- **Rolamento** com invencibilidade (~0,36 s).
- **Postura (poise):** inimigos cambaleiam ao quebrar a postura.
- **Telegrafia:** demônios brilham em vermelho (corpo a corpo) ou laranja (magia) antes de atacar — janela para rolar.
- **Hit-stop, tremor de câmera, números de dano, críticos.**
- **Morte:** volta à vila e perde metade do ouro.

## Habilidades que evoluem (3 níveis visuais cada)
| Árvore | Nv I | Nv II | Nv III |
|---|---|---|---|
| Centelha (magia inicial) | Faísca elétrica azul | Lança de Chamas laranja | Cometa Arcano violeta |
| Espada | Combo ×3 | Corte Crescente (projétil) | Tempestade de Lâminas |
| Escudo de Luz | Barreira | Reflexo | Égide da Deusa |
| Passos | Rolamento | Passo Sombrio (teleporte curto) | Fantasmas que atacam |
| Despertar | — | Fúria (buff) | Forma da Centelha (ultimate) |
Evolução via **Tomos** (drops raros de chefes/demônios de nível alto) + nível do herói.

## Inimigos (todos demônios, todos animados)
Diabrete (voador, garra + bola de fogo) ✔ · Oni soldado (clava) · Brutamontes chifrudo · Demônio-esqueleto ·
Súcuba maga · Demônio de fogo · Demônio de gelo · Espectro sombrio · Gárgula · Cavaleiro demoníaco · Generais · Rei Demônio.
Escala de atributos ≈ **+22% por nível**; nível do inimigo visível na placa (vermelho se acima do seu).

## Loot e economia
- Raridades: Comum, Incomum, Raro, Épico, Lendário (cores no chão e no feed).
- Drops por nível: ouro, materiais (Chifre de Diabrete, Brasa Infernal…), poções, tomos, equipamentos.
- **Forja** (Borin): materiais demoníacos → armas com atributos de fogo/gelo/sombra.
- Poções escassas no início (2) — a dificuldade vem daí.

## Guilda dos Aventureiros
Ranks F → E → D → C → B → A → S. Quadro de missões (caça, coleta, escolta, chefes). Recompensa: ouro, itens, rank.

## HUD (sem caixas)
Medalhão do retrato com 3 arcos (PV, PM, stamina) · orbes de habilidade em leque · rastreador de missão sobre mancha suave ·
diálogo em faixa de cinema com retrato grande e texto digitado · banners de região · placas de vida em pílula.
