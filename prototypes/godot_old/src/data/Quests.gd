class_name Quests
extends RefCounted

const QUESTS := {
	"m1_call": {"name": "O Chamado do Cristal", "main": true, "desc": "O Cristal da Aurora, que protege Alvorada, começou a rachar. Mira pediu sua ajuda.",
		"steps": ["Fale com a Mestra Selene na praça.", "Derrote as Sombras na praça.", "Fale com a Anciã Mira.", "Atravesse a Floresta Sussurrante."]},
	"m1_forest": {"name": "Uivos na Floresta", "main": true, "desc": "Lobos corrompidos pelas sombras dominam a Floresta Sussurrante.",
		"steps": ["Procure a origem dos uivos.", "Derrote Fenrisa, a Alfa Cinzenta.", "Entre na Caverna de Cristal."], "reward": {"xp": 160, "gold": 80}},
	"m1_cave": {"name": "O Coração da Caverna", "main": true, "desc": "O Cristal Menor da Aurora repousa na Câmara Profunda, protegido por um Guardião.",
		"steps": ["Encontre a Chave de Cristal.", "Abra o selo da Câmara Profunda.", "Derrote Cristalion e recupere o Cristal Menor.", "Volte a Alvorada e fale com Mira."], "reward": {"xp": 400, "gold": 180}},
	"s_slimes": {"name": "Praga de Gosma", "main": false, "desc": "Pipo perdeu o soldadinho de madeira para os slimes da floresta.",
		"steps": ["Derrote 5 slimes.", "Volte a falar com Pipo."], "reward": {"xp": 70, "gold": 40, "items": {"potion": 2}}},
	"s_herbs": {"name": "Ervas para a Estalagem", "main": false, "desc": "Dona Rosa precisa de 3 Ervas Curativas.",
		"steps": ["Colete 3 Ervas Curativas.", "Entregue as ervas a Dona Rosa."], "reward": {"xp": 60, "gold": 30, "items": {"ether": 2}}},
	"s_fisher": {"name": "A Isca Perfeita", "main": false, "desc": "Tio Zé jura que Gel de Slime é a melhor isca.",
		"steps": ["Traga 3 Géis de Slime para Tio Zé."], "reward": {"xp": 50, "gold": 25}},
}
