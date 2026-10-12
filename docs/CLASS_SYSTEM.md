# Sistema de Classes — Crônicas de Aetheria

**Status:** protótipo funcional em código GDScript, seleção entre **Novo Jogo** e o prólogo. As regras de combate estão programadas, mas a aprovação final depende de execução, equilíbrio e visual dos equipamentos reais no Godot/Android.

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

`SpiritPet` é uma unidade aliada separada do jogador. Ela segue Ren, seleciona inimigos, anima `idle/move/cast` e dispara projéteis **no quadro de conjuração**, sem atribuir o ataque ao herói. Sua arte usa temporariamente a folha HD existente de um espírito (`bog_wraith`) com cor etérea; uma **arte final exclusiva do pet permanece pendente**. Não representar essa reutilização provisória como modelagem inédita aprovada.

### Gates ainda obrigatórios

1. Compilar e executar a branch `gpt6-class-selection-20261012` no **Godot 4.3+** com testes de seleção por toque e teclado.
2. Verificar visualmente cada classe e seu equipamento em animações reais. **Sprites de Ren para arco, duas adagas e ausência de espada nos conjuradores ainda precisam de tratamento visual específico** antes de considerar a entrega artística final.
3. Confirmar IA, duração, quantidade e alvo dos pets em combate; equilibrar dano, proteção e mobilidade.
4. Garantir que não exista regressão no Grimório (X), nas cutscenes, na música de flauta ou na remoção do fôlego.
5. Gerar APK somente após a validação. O PR permanece isolado da branch principal até aprovação.

**Regra permanente:** classe não pode ser apenas cor, nome, conceito ou ícone. Restrições, ataque, equipamento, status e animação devem funcionar no jogo; screenshots somente se forem capturas reais do motor Godot.
