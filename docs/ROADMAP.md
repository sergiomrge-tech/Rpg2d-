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
- ⬜ Música e ambiência por região

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
1. Assim que a licença estiver nos segredos: rodar o CI, ver screenshots e corrigir.
2. Floresta de Velmoor (Capítulo 2).
