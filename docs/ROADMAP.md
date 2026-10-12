# Roadmap

Legenda: ✅ feito · 🔄 em andamento · ⬜ a fazer

## Etapa 0 — Infra
- ✅ Projeto Unity 2022.3 (cena criada por código, `Boot.cs`)
- ✅ CI GitHub Actions (GameCI) com build Linux + screenshots na branch `ci-shots`
- ⬜ **Usuário:** cadastrar segredos `UNITY_LICENSE`, `UNITY_EMAIL`, `UNITY_PASSWORD` ([guia](UNITY_CI.md))
- ✅ Checagem de compilação local (`tools/unity_check.sh`)
- ⬜ Validar primeiro build real e corrigir o que aparecer nos screenshots

## Etapa 1 — Capítulo 1 jogável (atual)
- ✅ Herói: 10 animações × 3 direções (idle, andar, correr, 3 ataques, magia, rolar, dano, morte)
- ✅ Diabrete: voo, ataque, magia, dano, morte (dissolve)
- ✅ NPCs: recepcionista da Guilda, ferreiro, aldeã
- ✅ Vila de Aurora + Bosque dos Chifres (chão pintado, rio, ponte, praça, 23 tipos de objeto, vento nas árvores)
- ✅ FX: cortes, garras, impactos, explosões, círculos mágicos, Centelha I/II/III, fumaça demoníaca
- ✅ Combate (stamina, combo, rolar, postura, telegrafia, hit-stop), loot, XP/nível, missão, prólogo, save
- 🔄 **Texturas do HUD** — 22 PNGs gerados no GitHub Actions por `tools/art_hd/ui.py`, incluindo medalhão, arcos, orbes, faixa de diálogo, ornamentos, pílulas e vinheta. Teste de integração e aprovação visual na Unity pendentes.
- 🔄 **Ícones de itens/habilidades** — atlas com 9 ícones e JSON gerados e verificados; avaliar legibilidade em 1920×1080 no jogo.
- 🔄 **Retratos** — gerados com recortes dos sprites HD originais do herói, Elina, Borin e Marta; retrato próprio de Lumia pendente, sem redefinir sua aparência antes da aprovação.
- ⬜ Chefe do capítulo: Diabrete-Chefe Grakk
- ⬜ Oni soldado (2º demônio)
- ⬜ Menus: inventário/grimório (livro aberto), forja, quadro de missões
- ⬜ Música e ambiência por região

## Etapa 2 — Capítulos 2–3
- ⬜ Floresta de Velmoor (mapa, Dríade Profanada, companheira Sylra)
- ⬜ Cidade de Valemont (mapa grande, Guilda principal, lojas)
- ⬜ Sistema de companheiro (IA aliada)
- ⬜ Evolução Centelha II + Corte Crescente
- ⬜ Equipamentos com atributos e forja

## Etapa 3 — Capítulos 4–7
- ⬜ Deserto, Minas, Pântano, Picos Gelados (+ demônios temáticos e chefes)
- ⬜ Árvores de habilidade completas (níveis III)
- ⬜ Iluminação 2D (dia/noite, tochas, cavernas)

## Etapa 4 — Capítulos 8–10 e final
- ⬜ Castelo sitiado, Terras Devastadas, Cidadela
- ⬜ 4 Generais + Rei Demônio Malgrath (3 fases)
- ⬜ Finais, créditos, Novo Jogo+

## Etapa 5 — Polimento e lançamento
- ⬜ Gamepad, opções, legendas/idiomas
- ⬜ Balanceamento (alvo ~30 h)
- ⬜ Builds Windows/Mac, página do jogo

## Próximo passo imediato
1. Revisar os PNGs gerados por `tools/art_hd/ui.py` no jogo; a geração e integridade passaram no GitHub Actions **sem licença Unity**, mas a qualidade integrada ainda não foi validada.
2. Assim que a licença estiver nos segredos: rodar o build Unity, inspecionar screenshots **reais** e corrigir.
3. Finalizar o retrato de Lumia seguindo a identidade aprovada, depois implementar chefe Grakk e Oni soldado sem alterar o padrão HD cartoon.
