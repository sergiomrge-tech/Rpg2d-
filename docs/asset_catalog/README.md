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
- Status: **15 folhas de sprites PNG/JSON renderizadas** e prévias reais dos quadros; 285 trilhas/3.024 quadros **renderizados e conferidos no contrato**. Todos os 15 possuem os seis estados-base; os cinco chefes também têm a segunda habilidade `skill_2` animada. A arte aguarda aprovação visual e testes Unity. Nenhum desses 14 novos inimigos/chefes está integrado ao combate.

## Pranchas reais de arte (não screenshots do jogo)

- [10 demônios](previews/LOTE1_DEMONIOS.png)
- [5 chefes](previews/LOTE1_CHEFES.png)

A geração de 13 criaturas adicionais é feita por `tools/art_hd/build_lote1_art.py` (Python/Cairo), seguindo o mesmo pipeline e mantendo intactos os sprites originais.

## Revisão anatômica do Lote 1

Oito criaturas originalmente consideradas repetitivas receberam **rigs exclusivos desenhados do zero** com os materiais, contornos e sombras Cairo da identidade aprovada. Todos os PNGs e JSONs de animação passaram na validação automatizada; falta o gate visual com animação real na Unity.

- [Visual dos oito novos corpos](previews/LOTE1_REMODEL_OITO.png)
- [Comparação real antes e depois](previews/LOTE1_REMODEL_COMPARACAO.png)
- Geração: `tools/art_hd/lote1_remodel.py` e `tools/art_hd/lote1_creatures.py`.
- Teste: `tools/art_hd/rework_gallery.py` compara com o ref original `gpt6-lote1-all-sprites-20261012`, evitando comparar o sprite novo consigo mesmo.
- [Lote 2 — ordem de produção dos 10 insetoides e 5 chefes](LOTE2_ORDEM_PRODUCAO.md); **ainda sem sprites**.

**Nota:** os novos corpos substituem apenas versões candidatas na branch de revisão. A direção HD cartoon e os arquivos aprovados da base oficial são mantidos intactos.

## Regra permanente do diretor
**Não apresentar arte conceitual como entrega.** Toda nova criatura precisa ter assets importados **e funcionar na Unity** com animações, movimentos, ataques e habilidades reais antes de ser declarada pronta. [Leia os critérios completos de aceitação](REGRA_OBRIGATORIA_ASSETS_JOGAVEIS.md). As pranchas e PNGs existentes seguem classificados apenas como material de catálogo, nunca como inimigos integrados à jogabilidade.
