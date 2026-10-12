# Catálogo de criaturas HD — Crônicas de Aetheria

Referência: docs/GAME_DESIGN.md e docs/ROADMAP.md.

## Contrato de qualidade
- Manter o estilo HD cartoon original, sombras suaves, contornos coloridos e três direções.
- Os rigs de origem são reutilizados, mas os novos desenhos de armadura, clava, coroa e runa possuem detalhes próprios.
- Não alterar nenhum sprite ou cenário anteriormente aprovado.
- Prévias são composições dos frames de sprite, NÃO screenshots do jogo.
- Não integrar novos inimigos à jogabilidade até revisão de capturas REAIS no Unity.

## Candidatos
- oni_soldier — Oni Soldado de Ferro: elite melee de clava, armadura rúnica e chifres.
- grakk — Grakk, Diabrete-Chefe: boss do capítulo I com coroa, armadura e cristal.

JSON de catálogo: docs/asset_catalog/catalog.json. IDs persistentes:
Sprites/Demons/oni_soldier e Sprites/Demons/grakk.

## Gerar e testar
    python -m pip install pycairo numpy scipy pillow
    python tools/art_hd/build_extra_demons.py
    python tools/art_hd/verify_extra_demons.py

O workflow demon-art.yml executa estas etapas automaticamente e versiona os PNGs.
Status: 15 sprite sheets e seus JSONs renderizados; Unity runtime, screenshots reais, aprovação visual e integração ao combate continuam pendentes.

## Lote 1 — 10 demônios e 5 chefes

- [Fichas individuais (quadros, FPS, evento de ataque e habilidade)](LOTE1_FICHAS.md)
- [Contrato JSON versionado](lote1_spec.json)
- Validação sem licença Unity: `python tools/art_hd/verify_lote1.py`
- Status: **15 folhas de sprites PNG/JSON renderizadas** e prévias reais dos quadros; 285 trilhas/3.024 quadros **planejados** no contrato. Todos os 15 possuem os seis estados-base e 4 chefes adicionais têm `skill_2`; apenas Grakk ainda precisa da segunda habilidade animada. A arte aguarda aprovação visual e testes Unity. Nenhum desses 14 novos inimigos/chefes está integrado ao combate.

## Pranchas reais de arte (não screenshots do jogo)

- [10 demônios](previews/LOTE1_DEMONIOS.png)
- [5 chefes](previews/LOTE1_CHEFES.png)

A geração de 13 criaturas adicionais é feita por `tools/art_hd/build_lote1_art.py` (Python/Cairo), seguindo o mesmo pipeline e mantendo intactos os sprites originais.
