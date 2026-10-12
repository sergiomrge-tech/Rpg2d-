# Lote 2 — piloto integrado ao código Unity

**Este pacote contém assets animados e lógica real do jogo. Não contém arte conceitual.**

## Conteúdo entregue nesta branch

| Inimigo (ID) | Rig/silhueta | Movimento real (Enemy AI) | Ataque no quadro de impacto | Habilidade no quadro de cast |
|---|---|---|---|---|
| `mantis_reaver` | Mantídeo estreito com braços-foices orgânicos, pernas invertidas e abdomen segmentado | Aproximação rápida com strafe e perseguição | Corte frontal largo de foices | Dash cortante com alcance em cone |
| `scarab_brute` | Besouro blindado com seis pernas articuladas, dome quitinoso e chifre bifurcado | Avanço pesado com mínima evasão | Chifrada que empurra | Onda sísmica circular de curto alcance |
| `moth_hexer` | Mariposa de quatro grandes painéis alares, antenas plumosas e abdome fino | Voo com distância de segurança e recuo ao ser pressionada | Golpe de asa | Maldição em cone: dano, gasto de mana e stamina |

As habilidades já têm seleção pela IA, telegraph, cooldown, quadro de acionamento e checagem de dano/esquiva. Os efeitos reutilizam efeitos disponíveis na Unity; os VFX exclusivos por monstro ainda não foram modelados.

## Assets Unity fisicamente presentes

Cada inimigo tem `unity/Assets/Resources/Sprites/Demons/<id>.png` e `<id>.json`, **18 faixas direcionais** (`idle`, `move`, `attack`, `cast`, `hurt`, `death` × `down/up/side`), **192 quadros renderizados** por criatura e pivô para colocação no mundo. Total do piloto: **576 quadros**.

Gerador oficial reproduzível: `python tools/art_hd/lote2_pilot.py`. Ele reutiliza `tools/art_hd/core.py` e `sheet.py` com sombras suaves, `Pal/paint`, contornos e transparência. **Não utiliza arquivos gerados por prompts de imagem**.

O código C# implementado está em:
- `unity/Assets/Scripts/Game/Data.cs` — três fichas jogáveis com atributos, drops, escalas e perfis.
- `unity/Assets/Scripts/Game/Enemy.cs` — movimento individual, cooldown, aviso e eventos de animação.
- `unity/Assets/Scripts/Game/InsectCombat.cs` — ataque e habilidade distintos para cada espécie.
- `unity/Assets/Resources/Maps/village.json` — três spawns na parte florestal do mapa, em tiles não bloqueados.

A versão original dos personagens, cenários, shaders e estilo visual permanece sem modificações.

## Validação executada

- [x] Renderização Cairo de três sheets PNG e três JSONs.
- [x] Teste Python de metadados de animação, 54 tracks, movimento efetivo entre frames e contornos de silhueta não idênticos.
- [x] Os três arquivos `Resources` existem na branch; o teste confere que o mapa carrega spawns não bloqueados.
- [x] C# compilado estaticamente via `tools/unity_check.sh` (UnityEngine.Modules + stubs; independe da licença Unity).
- [x] GitHub Actions **38250016285** passou e publicou assets na branch.
- [ ] Executar o projeto no editor Unity 2022.3 LTS, sem crashes de runtime, e inspecionar imagens reais.
- [ ] Validar escala do collider, CPU/FPS, hit timing, obstáculos, equilíbrio de combate, HUD e integração narrativa.
- [ ] Aprovação visual do usuário para nível de refinamento antes de renderizar os próximos 12 insetoides/bosses.

**Limitação principal:** compilação estática não é build jogável. Os sprites e comportamentos foram colocados no projeto, mas a execução real no Unity ainda não foi validada.

## Para produzir os arquivos novamente

```bash
python -m pip install pillow numpy scipy pycairo
python tools/art_hd/lote2_pilot.py
python tools/art_hd/verify_lote2_pilot.py
bash tools/unity_check.sh
```

Próxima fase após a avaliação deste piloto: os outros **7 demônios insetoides e 5 chefes com rigs inéditos**, sem reutilizar o mesmo corpo nem trocar apenas armas.
