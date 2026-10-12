# Sistema de Classes — Crônicas de Aetheria

**Status em 12/10/2026:** sistema das seis classes implementado e validado em Godot 4.3 via CI, com assets HD animados originais e prerelease APK de teste compilada. A aprovação final ainda depende de teste visual e jogabilidade em aparelho Android. [Arte real e validação](CLASS_ART_IMPLEMENTATION.md) · [APK de teste](https://github.com/sergiomrge-tech/Rpg2d-/releases/tag/aetheria-6-classes-preview).

## Seis classes, com vantagens e fraquezas obrigatórias

| Classe | Só pode usar | Forte | Fraco | PV | PM | ATQ | MAG | Movimento | Defesa de classe | Crítico |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| Guerreiro | Espadas/armas físicas | Vida, defesa, combos e finalização física | Alcance curto, lento e sem magia | 135 | 45 | 16 | 9 | 0,91× | +8 | 8% |
| Mago | Magias, sem arma | Alto dano mágico e mana | Muito frágil, depende de PM | 78 | 105 | 7 | 23 | 0,97× | +0 | 6% |
| Arqueiro | Somente arco | Alcance, velocidade, rajadas e precisão | Defesa baixa, vulnerável de perto | 96 | 60 | 14 | 10 | 1,12× | +1 | 13% |
| Paladino | Espada e poderes sagrados | Defesa, vida e cura | Lento, crítico e dano ofensivo menores | 151 | 77 | 12 | 17 | 0,85× | +11 | 4% |
| Assassino | Somente duas adagas | Velocidade, crítico e golpes duplos | Defesa mínima e alcance curto | 90 | 64 | 18 | 10 | 1,19× | +0 | 28% |
| Invocador | Somente pets aliados | Até dois familiares autônomos que atacam por ele | Vida/defesa baixas; sem ataque próprio | 84 | 108 | 8 | 22 | 0,95× | +0 | 0% |

Os valores são parâmetros iniciais de **balanceamento**, sujeitos a ajustes após testes reais e não substituem a identidade do personagem.

### Comandos do combate

| Classe | Ação principal (J/toque) | Especial (K/toque) |
|---|---|---|
| Guerreiro | Combo de arma até três golpes | Finalização de arma pesada, sem conjuração |
| Mago | Projétil mágico básico que consome mana | Explosão arcana potente, maior custo de mana |
| Arqueiro | Disparo de uma flecha pelo arco | Rajada de três flechas, sem uso de magia |
| Paladino | Golpe físico com espada | Cura sagrada consumindo mana |
| Assassino | Combos de duas adagas e crítico elevado | Finalização dupla com adagas, sem magia |
| Invocador | Ordena aos pets que ataquem; não causa dano direto | Invoca um familiar com mana, até dois simultâneos |

**Todas as classes mantêm esquiva e corrida sem consumo de fôlego.** A mana continua limitando os feitiços e invocações, quando aplicável.

### Equipamento inicial e compatibilidade

- Guerreiro e Paladino: espada original `rusty_sword`.
- Arqueiro: `hunter_bow`; não pode equipar espadas nem adagas.
- Assassino: `twin_daggers`; não pode equipar arcos nem espadas.
- Mago e Invocador: sem arma equipada, não podem equipar armas físicas.
- Armaduras e acessórios mantêm suas regras normais.
- Um equipamento incompatível é **rejeitado antes de consumir o item do inventário**.
- A classe escolhida fica no campo `class_id` do save. Save anterior sem classe recebe **Guerreiro** como padrão, sem perda das demais estatísticas.
- Progressão por nível depende da classe (`hp_gain`, `mp_gain`, `atk_gain`, `mag_gain`).

### Invocador: pets efetivos no mundo

`SpiritPet` é uma unidade aliada separada do jogador. Ela segue Ren, seleciona inimigos, anima `idle/move/cast` e dispara projéteis **no quadro de conjuração**, sem atribuir o ataque ao herói. A arte provisória `bog_wraith` foi **substituída** pelo **Lince Astral**, personagem 2D quadrúpede de rig original com **240 quadros, 18 trilhas animadas** em `godot/assets/Sprites/Pets/astral_lynx.png/.json`. O familiar usa animações de movimento e conjuração com hit frame. Essa modelagem está disponível na branch de arte, mas ainda aguarda aprovação visual e testes Android. [Detalhes dos assets](CLASS_ART_IMPLEMENTATION.md).

### Gates ainda obrigatórios

1. ✅ **Godot 4.3**: compilação/import e smoke test de sprites reais, seleção por toque, combate e familiar aprovados em [CI #38292474839](https://github.com/sergiomrge-tech/Rpg2d-/actions/runs/38292474839). **Pendente:** testar instalação e comandos em dispositivo Android real.
2. ✅ Seis atlases HD já estão integrados **ao projeto Godot** (não à Unity): arco, duas adagas, magias sem espada, guerreiro, paladino, invocador e 6 retratos. ✅ [14 screenshots reais do motor](asset_catalog/captures/classes/) já produzidos; **pendente** a aprovação artística e inspeção no aparelho.
3. Confirmar IA, duração, quantidade e alvo dos pets em combate; equilibrar dano, proteção e mobilidade.
4. Garantir que não exista regressão no Grimório (X), nas cutscenes, na música de flauta ou na remoção do fôlego.
5. ✅ APK de teste gerado em [CI #38293183086](https://github.com/sergiomrge-tech/Rpg2d-/actions/runs/38293183086) e disponível na [prerelease](https://github.com/sergiomrge-tech/Rpg2d-/releases/tag/aetheria-6-classes-preview). **Pendente:** testar APK no celular, aprovar arte e balanceamento; PR permanece isolado da branch principal.

**Regra permanente:** classe não pode ser apenas cor, nome, conceito ou ícone. Restrições, ataque, equipamento, status e animação devem funcionar no jogo; screenshots somente se forem capturas reais do motor Godot.
