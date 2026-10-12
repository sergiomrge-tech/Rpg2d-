# Resiliência do salvamento — Capítulo 1

O arquivo principal do jogador é `aetheria_save.json`, criado em
`Application.persistentDataPath` pela Unity. A lógica está em
`unity/Assets/Scripts/Game/Game.cs`.

## O que mudou

- O jogo primeiro escreve e valida `aetheria_save.json.tmp`.
- A partida anterior válida é mantida em `aetheria_save.json.bak`.
- Depois de concluir a gravação temporária, o jogo move os arquivos para a
  posição definitiva, evitando sobrescrever diretamente o save principal.
- Ao iniciar, se o principal estiver ausente/corrompido, tenta carregar `.bak`.
- O jogo salva após ressuscitar da morte (com a perda de ouro aplicada), ao
  suspender o aplicativo e ao sair normalmente, além dos pontos já existentes.
- O modo de screenshots `-ciShots` continua sem gravar progresso real.
- Nenhum asset, sprite, material, shader ou configuração visual foi alterado.

## Limites

O backup contém a **última partida válida anterior** à gravação mais recente;
a recuperação após falha pode perder o progresso posterior a essa partida.
Uma falha de armazenamento físico também pode danificar ambos os arquivos.
A validação em código não substitui a execução no Unity.

## Checklist de QA no Unity 2022.3 LTS

1. Inicie uma nova partida, fale com Elina, mate um diabrete, colete loot e
   pressione F5. Feche, abra novamente e confirme inventário, ouro,
   nível, rank, flags e missão.
2. Salve duas vezes, confira a existência do arquivo `.bak`.
3. Com a Unity fechada, faça cópias dos saves. Corrompa **somente o principal**,
   reinicie e confirme a recuperação do `.bak` no Console.
4. Faça um novo save após recuperar do backup, feche e reabra. Confirme
   que a partida permanece legível.
5. Morra, espere a ressuscitação, saia e reabra. Confirme que o ouro perdido
   não foi restaurado e que a posição respawn está correta.
6. Repita os testes com diálogo aberto ao pausar, e no executável final.
7. Confirme visualmente que HUD, sprites e qualidade gráfica são idênticos
   ao commit de base.

> Ainda depende de um build e playthrough reais na Unity. Não marcar
> como teste aprovado até isso acontecer.
