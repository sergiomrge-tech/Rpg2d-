# Lote 2 — cinco chefes insetoides no Unity

**Diretriz:** esta entrega é código, sprites de verdade e integração de habilidades no RPG. **Não** é arte conceitual. A fidelidade ao estilo HD cartoon é preservada via `core.py`/`Pal`/Cairo, sem modificar cenários/personagens já aprovados.

## Rigs e habilidades independentes

| ID | Morfologia exclusiva | Habilidade 1 (`cast`) | Habilidade 2 (`skill_2`) |
| --- | --- | --- | --- |
| `mantis_high_reaper` | Torso alto, quatro pernas e quatro foices orgânicas | Leque cortante com verificação de cone e alcance | Mergulho de execução com dano em área e interrupção breve |
| `scarab_colossus` | Oito patas-pilares, carapaça dupla separável e núcleo rúnico | Pisoteio sísmico com telegraph e onda radial | Abre carapaça, recebe defesa temporária e lança oito projéteis |
| `moth_oracle` | Asas em rosetas com múltiplos olhos, antenas em ramificações e corpo espectral | Três esporos amaldiçoados que causam lentidão | Mandala ritual de área que causa dano, lentidão e interrupção |
| `queen_vespara` | Quatro asas longas, seis patas, abdômen em anéis e ferrão triplo | Rajada orgânica de três projéteis venenosos | Mergulho do ferrão com dano, veneno e poça tóxica |
| `brood_tyrant` | Colmeia assimétrica móvel de dez patas, ovos e duas cabeças mandibulares | Invoca até quatro formigas guardiãs vivas ao redor | Ruptura corrosiva radial e quatro poças tóxicas temporizadas |

## Integração funcional

- Sprites gerados em `unity/Assets/Resources/Sprites/Demons/<id>.png` e JSONs adjacentes, pelo `tools/art_hd/build_lote2_bosses.py`; cada um contém 7 estados × 3 direções (21 trilhas), com `hit` no momento do impacto em `attack`, `cast` e `skill_2`.
- `Enemy.cs` possui estado `Cast2`, telegraph específico, cooldown secundário, seleção de habilidade, movimento diferente por chefe e eventos sincronizados de dano.
- `InsectBossSkills.cs` implementa dez habilidades mecânicas distintas, com dano real, projéteis, controle de grupo, invocação e zonas persistentes no mundo Unity.
- Os cinco spawns ficam na floresta, afastados da vila inicial. Os oito diabretes da quest e os dez demônios comuns do Lote 2 não foram substituídos.
- O HUD existente mostra o nome e uma barra de vida ampliada apenas para bosses, reaproveitando a identidade gráfica dos painéis atuais.
- `InsectBossAtlasImporter.cs` desativa mipmaps e impede redução automática dos novos atlas para 2048 pixels, com alta qualidade de compressão. Não interfere nos sprites originais.

## Validação honesta

1. `bash tools/unity_check.sh` — valida os scripts C# contra referências de API (não é build executável da Unity).
2. `python tools/art_hd/verify_lote2_boss_gameplay.py` — verifica IDs, spawns, skills, projéteis e ausência de regressão do mapa.
3. `python tools/art_hd/build_lote2_bosses.py` — renderiza as **verdadeiras** folhas PNG e JSON.
4. `python tools/art_hd/verify_lote2_bosses.py` — rejeita quadros estáticos, recortes nas bordas, frames vazios e direções idênticas.
5. **Ainda necessário:** executar o Editor Unity 2022.3 LTS, percorrer os cinco encontros, conferir colisões, FPS, escala, hitbox, loot e a qualidade artística na tela. Somente prints reais do Editor podem ser chamados de screenshots do jogo.

**Status:** cinco folhas PNG/JSON e 105 trilhas direcionais renderizadas, verificadas e versionadas no GitHub. O compile check do C# e a QA de gameplay passaram. **A execução real no Editor Unity e a aprovação artística do diretor continuam pendentes**, portanto o PR permanece em rascunho.
