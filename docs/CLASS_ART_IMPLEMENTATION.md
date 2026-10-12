# Classes — assets reais HD e integração no Godot

**Estado em 12/10/2026: ARTES GERADAS e arquivos reais disponíveis no GitHub.** Testes nativos Godot e capturas do jogo em andamento. **Não aprovado ainda para publicação Android ou avaliação visual final.**

## Origem e identidade visual

Todo sprite foi **desenhado pelo gerador Cairo original** em `tools/art_hd/` usando o mesmo `Look`, `Pal`, materiais de cel shading, contorno e curvas de animação da versão aprovada de Ren. Não foram utilizadas artes conceituais nem folhas de sprites geradas como imagens ilustrativas. O atlas `godot/assets/Sprites/Chars/hero.png` original permanece intacto.

| Classe | PNG/JSON de produção | Mudança real de anatomia/equipamento |
|---|---|---|
| Guerreiro | `hero_warrior` | Peitoral, ombreiras segmentadas, capacete e espada física |
| Mago | `hero_mage` | Capuz, manto de mago, mãos vazias e gesto independente de conjuração |
| Arqueiro | `hero_archer` | Arco recurvo lamelar, corda, aljava e pose de disparo de arco |
| Paladino | `hero_paladin` | Elmo com crista, peitoral sagrado, ombreiras e espada |
| Assassino | `hero_assassin` | Capuz/máscara, dois punhais em mãos diferentes, postura e golpes duplos |
| Invocador | `hero_summoner` | Manto ritual, cristais flutuantes e conjuração com ambas as mãos, sem arma |

**Arquivos:** `godot/assets/Sprites/Chars/hero_<classe>.png/.json`. Cada um tem **270 quadros RGBA em 4032 × 2288 pixels, 30 trilhas (10 ações × down/up/side)**: `idle`, `walk`, `run`, `attack1/2/3`, `cast`, `roll`, `hurt`, `death`. O lado esquerdo é espelhado pelo sistema do Godot.

**Total:** seis conjuntos = **1.620 quadros reais, 180 trilhas**.

A tela de escolha de classe utiliza **seis retratos transparentes `godot/assets/Sprites/Ui/ClassPortraits/<classe>.png` recortados dos quadros reais de `idle_down`**. Isso substitui a apresentação baseada só em ícones sem mudar a identidade dos cartões do menu. Prévia de sprites extraídos em `docs/asset_catalog/previews/classes/`. Esses arquivos **não são capturas da Unity ou Godot em execução**.

## Pet original — Lince Astral

Novo familiar inédito para o Invocador, com corpo **quadrúpede**, pernas e garras articuladas, coroa de chifres ramificados, caudas etéreas bifurcadas, marcas de cristal e uma animação de conjuração.

- `godot/assets/Sprites/Pets/astral_lynx.png` / `.json`
- **240 quadros RGBA (4032 × 2112), 18 trilhas (6 ações × 3 direções)**: `idle`, `move`, `attack`, `cast`, `hurt`, `death`.
- `SpiritPet` foi atualizado para usar o novo sheet sem aplicar matizes artificiais. Seus ataques são disparados pelo evento `visual.hit` no quadro de impacto da própria animação `cast`.
- A quantidade máxima (2 pets), mana, deslocamento, seleção de inimigos, ataque automático e tempo de vida continuam geridos no código real do jogo.
- Esta criatura **substitui o uso provisório do sprite `bog_wraith`** como familiar. Esse inimigo antigo não foi modificado.

## Ligação efetiva com a jogabilidade

- `Player.spawn` carrega `HeroClasses.sheet_for(state.class_id)` para saves e personagens novos.
- **`Game.new_game` também troca o atlas imediatamente após a confirmação da classe**; caso contrário, o herói já instanciado antes do menu continuaria com visual de Guerreiro.
- `ClassSelect` usa os retratos originais derivados desses atlas e mantém seis cartões touch.
- `SpiritPet` carrega `Sprites/Pets/astral_lynx`, com movimentos e habilidades animados.
- A proibição de espada para Mago/Invocador, arco exclusivo, adagas duplas e diferenças de atributos/skills do [sistema de classes](CLASS_SYSTEM.md) permanece codificada.
- As correções de Grimório, cutscenes, trilha de flauta e ausência de fôlego continuam herdadas da branch base Godot.

## Verificação e gates

- **Render/arquivos aprovados:** [GitHub Actions #38290804310](https://github.com/sergiomrge-tech/Rpg2d-/actions/runs/38290804310).
- `tools/art_hd/verify_class_art.py` valida transparência real, trilhas completas, quadros não estáticos, direções distintas, retratos não vazios e caminhos usados pelo código.
- **Godot runtime:** `godot-class-art.yml` importa recursos e executa `-uiSmoke -touch` para seis classes, seleção e sprites carregados, pet e regressões gerais. Confirmar resultado antes do merge.
- **Screenshots verdadeiros do jogo:** `godot-class-screenshots.yml` chama `-classShots` para salvar 14 capturas PNG do **viewport real Godot** (menu + seis idle + seis skills + pet) em `docs/asset_catalog/captures/classes/`; o diretório existe somente depois do workflow concluir com sucesso.
- **Pendente:** inspeção final do refinamento, colisões e timing visual, teste Android em dispositivo real, exportação de APK e aprovação do diretor.

Os assets de classes devem continuar visualmente distintos, porém **coerentes com a arte atual**. Não substituir os gráficos aprovados por baixo detalhamento, imagens conceituais ou poses estáticas.
