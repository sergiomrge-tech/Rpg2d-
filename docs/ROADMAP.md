# Roadmap

Legenda: ✅ feito · 🔄 em andamento · ⬜ a fazer

## Etapa 0 — Infra (migrado para Godot 4.3)
- ✅ **Motor trocado de Unity para Godot** (sem licença; roda e tira screenshots na nuvem). Port completo em GDScript; C# arquivado em `prototypes/unity`
- ✅ CI GitHub Actions (`godot.yml`): importa, roda tour e publica screenshots na `ci-shots`
- ✅ Primeiro run real validado: vila, diálogo, grimório, combate e as 10 regiões renderizam

## Etapa 1 — Capítulo 1 jogável (atual)
- ✅ Herói: 10 animações × 3 direções (idle, andar, correr, 3 ataques, magia, rolar, dano, morte)
- ✅ Diabrete: voo, ataque, magia, dano, morte (dissolve)
- ✅ NPCs: recepcionista da Guilda, ferreiro, aldeã
- ✅ Vila de Aurora + Bosque dos Chifres (chão pintado, rio, ponte, praça, 23 tipos de objeto, vento nas árvores)
- ✅ FX: cortes, garras, impactos, explosões, círculos mágicos, Centelha I/II/III, fumaça demoníaca
- ✅ Combate (stamina, combo, rolar, postura, telegrafia, hit-stop), loot, XP/nível, missão, prólogo, save
- ✅ Texturas do HUD (medalhão, arcos PV/PM/stamina, orbes, faixa de diálogo, fita de nome, pílulas, vinheta) — `tools/art_hd/ui.py`
- ✅ Ícones de itens/habilidades (`Sprites/Ui/icons`)
- ✅ Retratos (herói, Elina, Borin, Marta, Lumia)
- ✅ Chefe do capítulo: Grakk, Chefe dos Diabretes (leque de 3 bolas de fogo, banner de chefe, drop garantido do Tomo)
- ✅ Oni Soldado (clava com espinhos, golpe pesado, alta postura)
- ✅ Missão em cadeia: 5 diabretes → Grakk → Rank E
- ✅ Lote 1 refeito no rig animado (conceitos do catálogo GPT): 6 diabretes (batedor, saqueador, piromante, feiticeiro,
  bombardeiro, uivador), 3 onis (lanceiro, escudeiro, carrasco) e 4 chefes futuros (Morgash, Velka, Krull, Thornmaw)
- ✅ Assets do GPT importados como entregues (`Sprites/DemonsGpt`, resolução reduzida à metade) — Bestiário **F9**
- ✅ Grimório em livro aberto (Tab): atributos, magias, bolsa; usar poções/éter/Tomo (evolui a Centelha)
- ✅ Forja do Borin: 5 Chifres + 80 ouro → Lâmina de Chifre (+6 ATQ)
- ⬜ Quadro de missões interativo, lojas
- ✅ Música procedural por região + tema de chefe (`core/music.gd`, loops de 8 compassos com crossfade)

## Etapa 2 — Capítulos 2–3
- ✅ Floresta de Velmoor: mapa (chão sombrio, rio, ruínas élficas, cogumelos luminosos, árvores corrompidas), portal no fim do bosque
- ✅ Viagem entre mapas (portais), descarrega a região anterior da memória
- ✅ Sylra, arqueira élfica: entra no grupo, segue o herói e atira flechas nos demônios
- ✅ Espírito Corrompido, Treant-Demônio; chefe **Dríade Profanada** (fase 2: invoca espíritos a 50% de vida)
- ✅ Missões: portal (exige Rank E) → Sylra → Dríade → Rank D
- ✅ Texturas com compressão BC7 (≈ ¼ da memória)
- ✅ Cidade de Valemont (72×64): muralhas, torres, portão, catedral, fonte, Guilda, feira, casas nobres, beco sombrio
- ✅ NPCs de Valemont (mestre da Guilda, guarda, nobre, clériga, criança, lojista) com retratos; compra de poções/éter
- ✅ Chefe **Assassino Sombrio**: teleporta para as suas costas, invoca batedores a 50% de vida
- ✅ Missões: Velmoor → Valemont (exige Rank D) → Assassino → Rank C
- ✅ Evolução das habilidades: Tomo da Centelha (I→II Lança de Chamas→III Cometa Arcano que atravessa inimigos) e **Tomo do Corte Crescente** (3º golpe lança lâmina de energia)
- ✅ Equipamentos: 3 slots (arma/armadura/amuleto), 11 peças com ATQ/DEF/MAG/PV, defesa reduz dano (100/(100+3×DEF)), equipar no Grimório
- ✅ Forja do Borin com 5 receitas (chifres, couro demoníaco, brasas, pó de espírito); drops de chefes (Espada de Velmoor, Cutelo do General Oni)
- ✅ Balanceamento: vida dos chefes cortada pela metade (de ~110 para ~55 golpes), Grakk mantido; tabela de golpes-para-matar revisada

## Etapa 3 — Capítulos 4–7
- ✅ **Deserto de Kharis** (Cap. 4): oásis, acampamento nômade, obeliscos, arena do **Demônio Escorpião** · NPC Hasim · Rank B
- ✅ **Minas de Durnhold** (Cap. 5): cavernas com cristais, forja anã, arena do **Golem de Brasa** · NPC Durnok · Couraça Anã
- ✅ **Pântano de Mirewail** (Cap. 6): brejo alagado, cabana sobre palafitas da bruxa Morgana, ilha de **Mirael, a Súcubo** · Rank A
- ✅ **Picos Gelados** (Cap. 7): nevascas, estátuas congeladas, Templo de Lumia (Monge Ilan), arena do **Demônio de Gelo**
- ✅ 13 novos demônios animados (3 vistas × 6 estados): diabretes das dunas/mineiro/bruxo/gélido, espectros de areia e do brejo, onis nômade/de rocha/de gelo + 4 chefes
- ✅ Chefes com fase 2 (invocam reforços a 50 %); drops garantidos de equipamento épico/lendário por chefe
- ✅ Portões de viagem por progresso (Rank/chefe derrotado), título de região, missões de região em tabela (`Story.Regions`)
- ✅ Iluminação 2D: tom ambiente por mapa, ciclo dia/noite nas regiões externas, brilho de tochas/lâmpadas/cristais/portais com tremulação
- ⬜ Árvores de habilidade completas (nível III de espada, escudo de luz, passos)

## Etapa 4 — Capítulos 8–10 e final
- ✅ **Castelo de Valemont** (Cap. 8): pátio pavimentado, torres, fortaleza, braseiros; cavaleiros demoníacos e o **General Vorath** (montante negra)
- ✅ **Terras Devastadas** (Cap. 9): ruínas em brasa, rios de lava, quatro arenas com os **4 Generais** (Thornmaw, Velka, Krull, Morgash) — todos precisam cair para abrir a Cidadela · Rank S
- ✅ **Cidadela de Malgrath** (Cap. 10): fortaleza de obsidiana, portão do inferno, salão do trono; Lumia dá a bênção final
- ✅ **Malgrath, o Rei Demônio — 3 fases:** F1 leque de 3 fogos · F2 (<66 %) passos sombrios + 4 reforços + leque de 5 · F3 (<33 %) fúria, leque de 7 e anéis de fogo
- ✅ Final: epílogo com Lumia e Sylra, créditos rolantes e modo de exploração livre
- ✅ Barra de vida de chefe (nome + título), save guarda mapa e posição
- ✅ **Rebalanceamento:** HP do inimigo ∝ dano do jogador (×(1+0,28·(nv−1))), dano do inimigo ∝ vida do jogador (×(1+0,14·(nv−1))); XP linear; poções curam 35 % da vida máxima
- ✅ **Cutscenes ilustradas** em tela cheia (1920×1080): prólogo (Tóquio à noite, o vazio da deusa Lumia, o despertar em Aurora) e final (queda de Malgrath, nascer do sol nos picos, vista de Aetheria) — `tools/art_hd/cutscenes.py`, exibidas pelo sistema de diálogo
- ⬜ Novo Jogo+ (dificuldade ×1,5, itens lendários extras)

## Etapa 5 — Polimento e lançamento
- ✅ **Ruas com vida:** 16 aldeões patrulham Valemont (5 em Aurora), param para olhar o herói e cumprimentam; ferraria com marteladas e faíscas, murmúrio posicional na taverna e nas bancas, água da fonte, fumaça nas chaminés (`Citizen`, `AmbientEmitter`)
- ✅ **Mago com magia em área:** R = Chuva de Meteoros (38 MP, 11 s), F = Tempestade de Raios (30 MP, 9 s); círculo de alvo, dano em área, orbes no HUD e botões no toque (`AreaSpell`)
- ✅ **Ambiência regional** (pássaros, grilos, gotas, sapos…) por mapa em `Sfx.region_ambience`
- ✅ **Ciclo dia/noite com rotina:** relógio no HUD; aldeões e lojistas recolhem à noite (guardas e taverneiro ficam)
- ✅ **5 missões secundárias** em Valemont (chifres, forja, ervas, hidromel, relíquias) com rastreador no HUD
- ✅ **Equipamentos por raridade:** Comum, Incomum, Raro, Épico e Lendário para espada, arco, adagas, armadura e amuleto (`tools/gen_gear.py`); drops aleatórios por nível (chefes sempre soltam Raro ou melhor), baús melhores dão mais; bolsa com rolagem, raridade colorida, botões Usar/Equipar e Vender (Q)
- ✅ **Legibilidade no celular:** textos 30% maiores no modo toque e caixa de diálogo maior
- ✅ **Área inicial mais calma:** sem monstros num raio de 16 tiles do herói e metade dos monstros de Aurora
- ✅ **Cajados** (Comum→Lendário) para Mago e Invocador; os dois agora equipam cajados (magia +)
- ✅ **Forja:** no ferreiro (Aurora/Valemont), botão "Forjar" sob cada slot do livro: +12% dos atributos por nível até +5 (ouro; Brasa Infernal a partir do +4)
- ✅ **Conjuntos:** 2 peças da mesma família = +PV; 3 peças = +ATQ/MAG/DEF (cinco conjuntos, Aventureiro → Lendário)
- ✅ **Drops Épicos/Lendários** com feixe de luz e som próprio
- ✅ **Comparação na bolsa** (▲ verde / ▼ vermelho contra a peça equipada)
- ✅ **Novo Jogo+** (após o final): mantém nível, equipamentos e forja; monstros +6 níveis por ciclo; chefes dropam mais e melhor
- ✅ **Cajado inicial** (Carvalho) para Mago e Invocador
- ✅ **Poderes de conjunto (3 peças):** Aventureiro +10% EXP · Veterano +15% ouro · Rúnico raio ao acertar · Alvorecer cura ao abater · Lendário meteoro ao acertar
- ✅ **Loja do ferreiro** (Aurora: peças comuns/incomuns; Valemont: até Épico + Brasa Infernal) abre após falar com o ferreiro (`ShopMenu`)
- ✅ **Ferreiro na bússola:** botão de forja longe do ferreiro marca o caminho por 40 s
- ✅ **Desafio do Abismo** (após o final / Novo Jogo+): fale com o Capitão Brandt; 5 ondas com general na última, recompensa em ouro e 3 drops de chefe (`Abyss`)
- ✅ **Atributos e árvore de habilidades:** cada nível dá 3 pontos de atributo (Força, Constituição, Mana, Inteligência, Agilidade, Sorte) e 1 de habilidade; árvore de 3 ramos × 4 camadas por classe (camadas liberam nos níveis 2/5/9/14), habilidades ativas R/F desbloqueadas na árvore; tela `P`; redefinir por ouro (`SkillTree`, `SkillsMenu`, `SkillActions`)
- ✅ **Requisitos de atributo** em armas e armaduras especiais (ex.: Excalibur exige FOR 28)
- ✅ **Valemont urbanizada:** taverna (descanso 40 ouro: cura + salva), ferraria (forja), estábulo, boticário, armaria, padaria, quartel, biblioteca, 4 tipos novos de casa, estátuas do herói, bancos, vasos, carroça de feno, bebedouro, bancas coloridas e postes ornamentais com brilho noturno; NPCs e diálogos para cada serviço; prédios ficam translúcidos quando o herói passa atrás
- ✅ **Vegetação:** 13 novas plantas (bétula, cerejeira, salgueiro, cerca-viva, topiaria, samambaia, canteiro de flores, arbusto de frutas, capim alto, tronco caído, arbusto seco, arbusto de gelo, samambaia luminosa), plantio em bosques por região, junco à beira d'água, alamedas e jardins na capital
- ✅ **Mapas ampliados (~2× a área):** anel de terra nova ao redor de cada região (`tools/art_hd/expand_maps.py`), estradas e rios prolongados até as novas bordas, mesma densidade de objetos e inimigos, pontos de interesse (acampamentos com elite, círculos de pedra, ruínas, bosques) ligados por trilhas e **baús de tesouro** (`TreasureCache`) que só abrem uma vez
- ✅ **Valemont circular** (100×100): muralha em anel com torres, três portões e comportas do rio, ruas radiais e concêntricas, praça com fonte, catedral e Guilda, mercado, bairro nobre, dois bosques e o beco do Assassino sem saída
- ✅ Menu inicial (Continuar / Novo Jogo / Opções / Sair), teclado, mouse e toque; novo jogo acorda num campo além do rio, longe de Aurora, guiado pela bússola até a Guilda
- ✅ Correção do toque no celular: o analógico e os botões usavam a transformada da câmera por engano; agora usam as coordenadas da tela (testado com toques simulados no CI)
- ✅ Passos por superfície: grama (Aurora/Velmoor), pedra (Valemont/Minas/Castelo/Cidadela), areia (Kharis), lama (Mirewail), neve (Picos), cascalho (Terras Devastadas) — sintetizados, 3 variações cada
- ✅ Menu de opções (Esc): volumes de Música/Efeitos/Vozes em barramentos separados (salvos em `user://settings.json`), salvar e continuar
- ✅ Rugido/chiado sintetizado na entrada dos chefes; fala da Lumia mais lenta, com peso
- ✅ Falas em sussurro: cada letra revelada dispara uma sílaba soprada (ruído filtrado por formantes de vogal), com timbre por personagem e voz mais baixa na narração (`Sfx.whisper`)
- ✅ **Missão principal animada:** marcador dourado flutuante sobre o alvo (NPC/chefe/inimigo) ou chevron na saída do mapa que leva até ele, seta de bússola na borda da tela com distância, painel de missão que desliza/brilha com "NOVA MISSÃO"/"PROGRESSO", banner animado "MISSÃO CONCLUÍDA" nas promoções e chefes
- ✅ Save resiliente (arquivo temporário validado + `.bak` + recuperação automática; salva ao morrer/fechar) — ideia do PR #1
- ✅ Tour automático longo no CI: todos os 10 chefes (com Sylra), fases, final e créditos
- ✅ **Insetoides do GPT portados** (PRs #6–#10): 10 insetos comuns + 5 chefes opcionais com IA e habilidades próprias em GDScript (`insect.gd`): investida, onda sísmica, maldição, veneno, onda sonora, carapaça, nuvem tóxica, agulhas, invocação de formigas; status Veneno/Lentidão/Atordoado no herói; encontros opcionais em `data/insect_spawns.json`
- ⬜ Gamepad, opções, legendas/idiomas
- ⬜ Balanceamento (alvo ~30 h)
- ⬜ Builds Windows/Mac, página do jogo

## Próximo passo imediato
1. Jogar de verdade (clique/teclado) e anotar o que está estranho: combate, balanceamento, câmera.
2. Novo Jogo+, árvores de habilidade, insetoides do GPT.
3. Exportar builds (Windows/Linux/Web) pelo Godot.
