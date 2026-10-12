# Classes — assets reais HD e integração no Godot

**Estado em 12/10/2026: assets reais criados, carregados e verificados no Godot 4.3.** Render/contratos, testes nativos de UI/combate e **14 capturas reais do jogo** foram concluídos com sucesso. Foi compilado um APK **experimental separado**, que ainda requer instalação, desempenho e avaliação visual no aparelho. A expansão **não foi mesclada ao ramo principal**.

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
- **Godot runtime aprovado:** [GitHub Actions #38291966997](https://github.com/sergiomrge-tech/Rpg2d-/actions/runs/38291966997) e [validação mais recente #38292474839](https://github.com/sergiomrge-tech/Rpg2d-/actions/runs/38292474839) importam no Godot 4.3 e executam `-uiSmoke -touch`, validando seis classes, o carregamento dos sprites originais, o pet, a seleção, habilidades e regressões.
- **Screenshots autênticos aprovados pelo CI:** [GitHub Actions #38292498437](https://github.com/sergiomrge-tech/Rpg2d-/actions/runs/38292498437) executou `-classShots` em Godot 4.3 e publicou **14 capturas** do **viewport real**, em [`docs/asset_catalog/captures/classes/`](asset_catalog/captures/classes/). A primeira inspeção levou a duas melhorias verificáveis: textos curtos para não escapar dos cartões e câmera de QA afastada do poço do centro da vila; as capturas mais recentes refletem ambas.
- **APK de teste Android pronto:** [build final #38293183086](https://github.com/sergiomrge-tech/Rpg2d-/actions/runs/38293183086) **aprovado**, exportado no Godot 4.3 e publicado como [prerelease `aetheria-6-classes-preview`](https://github.com/sergiomrge-tech/Rpg2d-/releases/tag/aetheria-6-classes-preview). **[APK direto (518.240.926 bytes)](https://github.com/sergiomrge-tech/Rpg2d-/releases/download/aetheria-6-classes-preview/Aetheria_Seis_Classes_Teste.apk)**. O GitHub confirmou que o arquivo e a tag são do commit `cb089d56cfd49e277f9341af7a931bbc5dd31dbe`, pertencente à branch de arte, e não da `main`. Arte/código documentados após esse build não alteram o APK já publicado. Teste de instalação, desempenho, jogabilidade e estabilidade em Android físico **ainda pendente**. A release principal `apk-latest` não foi alterada.
- **Pendente:** aprovação artística do diretor das capturas reais, hitboxes em combate num dispositivo, FPS/memória em Android, instalação/update do APK e balanceamento. **O APK foi exportado, não instalado/testado por nós.**

Os assets de classes devem continuar visualmente distintos, porém **coerentes com a arte atual**. Não substituir os gráficos aprovados por baixo detalhamento, imagens conceituais ou poses estáticas.
