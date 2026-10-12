# Crônicas de Aetheria — Fragmentos da Aurora
RPG de ação 2D em pixel art estilo anime · campanha planejada de ~30 horas · 10 capítulos

## Pilares
1. **Combate de ação fluido**: combo de 3 golpes, esquiva com i-frames, 15 habilidades em 3 escolas (Lâmina / Arcano / Espírito), cada uma com 5 níveis. Inimigos com telegrafia clara, fraquezas elementais e chefes com fases.
2. **Mundo vivo e denso**: cada região tem identidade visual própria (paleta, props, música, clima), NPCs com missões, segredos e baús escondidos.
3. **História com coração**: dois irmãos gêmeos — um escolhido pela Aurora, outro pela Noite — e o preço de salvar o mundo. Companheiros com arcos pessoais.
4. **Progressão profunda**: níveis até 60, equipamentos por capítulo, árvore de habilidades, aliados que lutam ao seu lado.

## Mundo
O **Cristal da Aurora** mantém **Nyxar**, o Deus da Noite Eterna, selado há mil anos pelos **Sete Guardiões** (Lâmina, Arcano, Espírito, Fera, Tempo, Tormenta e Sombra). O Cristal está rachando. Fragmentos menores ("Cristais Menores") estão espalhados pelo mundo. O herói carrega o **Pingente da Aurora**, que ressoa com eles.

## Elenco
| Personagem | Papel | Combate (aliado) |
|---|---|---|
| **Kai / Aiko** (jogador) | Órfão criado por Mira, herdeiro da Aurora | Espada + todas as escolas |
| **Mira** | Anciã, mentora | — |
| **Lyra Valenne** | Maga prodígio de Celestia, orgulhosa e leal | Bolas de fogo / lanças de gelo |
| **Torren** | Cavaleiro-lobo, protetor de sua tribo | Golpes em área corpo-a-corpo |
| **Sylphie** | Espírito-raposa, curandeira jovem | Cura o grupo |
| **Rhea** | Ex-assassina do Culto da Noite | Adagas sombrias rápidas |
| **Velkan** | Irmão gêmeo, "Príncipe do Eclipse", receptáculo de Nyxar | Antagonista / rival |

## Campanha (10 capítulos × ~3 h)
| # | Capítulo | Regiões / Masmorra | Chefe | Novidades |
|---|---|---|---|---|
| **1** ✅ | **O Despertar** | Vila Alvorada · Floresta Sussurrante · Caverna de Cristal | Fenrisa (Alfa), Rei Slime (opcional), Cristalion | Tutorial, Lyra entra, revelação do irmão. **Implementado** |
| 2 | **A Estrada Dourada** | Planícies de Trigo · Porto Luz (cidade-mercado, tipo deserto/oásis) · Mina Abandonada | Capataz Colossal / Rei Goblin | Loja de classes, pesca, mercado, 2ª escola de habilidades expandida |
| 3 | **Névoa no Pântano** | Pântano de Névoa · Aldeia Beastkin · Templo Submerso | Hidra Venenosa | **Torren** entra, status envenenamento, plataformas na água |
| 4 | **O Pico Silente** | Montanhas Cinzentas · Cidadela de Gelo | Dragão de Gelo Skaldur | Neve/gelo escorregadio, puzzles de espelhos |
| 5 | **Sol de Cristal** | Deserto de Cristais · Cidade Oásis · Ruínas Solares | Faraó Eclipse | **Rhea** entra, tempestades de areia, bioma deserto |
| 6 | **Academia de Celestia** | Cidade flutuante · Torre dos Arquimagos | Reitor Corrompido | Torneio de duelos, Lyra: arco pessoal, magia de Tempo |
| 7 | **Raízes do Mundo** | Floresta Espiritual · Árvore-Mundo | Guardiã Corrompida | **Sylphie** entra, puzzle de luz e sombra |
| 8 | **A Forja do Vulcão** | Vulcão Ignis · Forjas dos Anões | Gigante de Magma | Forja da **Lâmina Aurora** (arma lendária) |
| 9 | **Abismo Submerso** | Reino Afundado · Corredor das Marés | Leviatã | Verdade sobre os Guardiões; Mira revela tudo |
| 10 | **O Eclipse** | Cidadela do Culto · Coração de Nyxar | Velkan + Nyxar (3 fases) | Múltiplos finais · Pós-jogo: **Torre Infinita** |

### Estrutura de cada capítulo
- 1 hub (cidade/vila) com lojas, estalagem e 4–6 missões secundárias
- 1–2 áreas abertas com segredos e chefe opcional
- 1 masmorra com puzzle, mini-chefe, chefe e cutscene
- 1 novo companheiro **ou** nova mecânica
- Equipamento novo e +3 níveis de habilidade desbloqueáveis

## Sistemas implementados
- Motor próprio TypeScript + Canvas 2D (384×216, escala inteira, HUD em resolução nativa)
- Arte 100% procedural: personagens chibi (4 direções, 6+ animações), retratos, monstros, tiles, objetos, ícones
- Música chiptune e SFX sintetizados via WebAudio (8 temas)
- Combate: combo, esquiva, 15 habilidades, status (queimar/congelar/lentidão/atordoar), fraquezas, críticos, hit-stop, screenshake
- IA: 12 comportamentos + 3 chefes com fases e padrões telegrafados; pathfinding por campo de fluxo
- Diálogos com retratos e emoções, escolhas, cutscenes com scripts assíncronos
- Missões principais/secundárias, lojas, inventário, equipamentos, árvore de habilidades
- Iluminação dinâmica em cavernas, partículas ambientais, minimapa circular com neblina de exploração
- Save em 3 slots + autosave · suporte a teclado, gamepad e toque
