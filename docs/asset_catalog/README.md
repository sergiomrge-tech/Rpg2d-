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
Status: arte candidata; Unity runtime, screenshots reais e integração estão pendentes.
