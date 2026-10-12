# Crônicas de Aetheria — Fragmentos da Aurora

RPG de ação 2D em **pixel art estilo anime**, feito do zero em TypeScript + Canvas 2D (sem assets externos: toda a arte e o áudio são gerados por código).

> **Estado atual:** Capítulo 1 jogável (~1–1,5 h) + motor completo. Roteiro dos 10 capítulos (~30 h) em [`docs/GAME_DESIGN.md`](docs/GAME_DESIGN.md).

## Jogar
```bash
npm install
npm run dev      # http://localhost:5173
npm run build    # produção em dist/ (hospedável em qualquer servidor estático)
```

## Controles
| Ação | Teclado | Gamepad |
|---|---|---|
| Mover | Setas / WASD | Analógico / D-pad |
| Atacar (combo ×3) | J / Z | X |
| Esquivar (i-frames) | K / X / Shift | B |
| Habilidades 1–4 | 1 2 3 4 | Y / RB / LB / RT |
| Interagir / confirmar | E / Espaço / Enter | A |
| Poção / Éter rápido | Q / R | — |
| Menu | Esc / Tab | Start |

No celular/tablet aparecem controles virtuais na tela.

## Estrutura
```
src/engine     display (pixel buffer + UI), input, áudio (WebAudio), util
src/art        geradores procedurais: personagens, retratos, monstros, tiles, ícones
src/game       state, entities, world (mapa, combate, IA), ui (HUD, menu, loja), maps, story
scripts        testes automatizados (Playwright): screenshots e playthrough do Capítulo 1
docs           design do jogo e roteiro da campanha
```

## Testes
```bash
npm run dev &
node scripts/playthrough.mjs   # percorre o Capítulo 1 inteiro e falha em qualquer erro de script
```
