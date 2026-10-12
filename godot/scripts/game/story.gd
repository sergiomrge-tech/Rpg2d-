extends Node
## Script of the campaign: texts live in res://data/story.json, branching dialogue logic lives here.
## A "line" is [who, text]; who == "@scene" switches the cutscene illustration, who == "" is narration.

const QUEST_IMPS := "q_imps"
const QUEST_IMPS_GOAL := 5

var regions: Array = []
var names := {}
var prologue: Array = []
var ending: Array = []
var final_blessing: Array = []
var credits := ""


func _ready() -> void:
	var f := FileAccess.open("res://data/story.json", FileAccess.READ)
	var d: Dictionary = JSON.parse_string(f.get_as_text())
	regions = d["regions"]
	names = d["names"]
	prologue = d["prologue"]
	ending = d["ending"]
	final_blessing = d["final_blessing"]
	credits = d["credits"]


func name_of(id: String) -> String:
	return names.get(id, id)


func region_all_dead(r: Dictionary) -> bool:
	for b in String(r["boss"]).split(","):
		if not Game.flags.has(b + "_dead"):
			return false
	return true


func _l(npc: String, text: String) -> Array:
	return [npc, text]


func talk(npc: String) -> Array:
	var g := Game
	var gs: GameState = g.state
	for r in regions:
		if r["npc"] != npc:
			continue
		if g.flags.has(r["done"]):
			return [_l(npc, "Vá em frente, Ren. A próxima luta é sua.")]
		if region_all_dead(r):
			g.flags[r["done"]] = true
			gs.gold += int(r["gold"])
			gs.guild_rank = r["rank"]
			for rw in r["reward"]:
				var kv: PackedStringArray = String(rw).split(":")
				gs.add(kv[0], int(kv[1]))
			return r["thanks"]
		if not g.flags.has(r["start"]):
			g.flags[r["start"]] = true
			return r["hello"]
		return r["back"]
	match npc:
		"receptionist":
			if not g.flags.has("guild_joined"):
				g.flags["guild_joined"] = true
				g.start_quest(QUEST_IMPS)
				return [
					_l(npc, "Bem-vindo à Guilda dos Aventureiros de Aurora! Novo por aqui? Dá pra ver pela espada enferrujada."),
					_l(npc, "Registrei você no Rank F. Todo mundo começa do fundo — até os heróis das lendas."),
					_l(npc, "Diabretes estão saindo do Bosque dos Chifres, ao sul. Elimine 5 e traga os chifres."),
					_l(npc, "Cuidado: eles brilham em vermelho antes de atacar. Role [Espaço] nessa hora. Sério."),
				]
			if g.quest_progress(QUEST_IMPS) >= QUEST_IMPS_GOAL and not g.flags.has("q_imps_done"):
				g.flags["q_imps_done"] = true
				gs.gold += 60
				gs.add("potion", 2)
				return [
					_l(npc, "Cinco diabretes?! E voltou inteiro! Aqui estão 60 de ouro e duas poções."),
					_l(npc, "Mas há algo pior: um diabrete ancião, Grakk, comanda os outros no fundo do bosque."),
					_l(npc, "Derrote Grakk e a Guilda o promove ao Rank E. Ele cospe fogo em leque — não fique parado."),
				]
			if g.flags.has("grakk_dead") and not g.flags.has("rank_e"):
				g.flags["rank_e"] = true
				gs.gold += 200
				gs.guild_rank = "E"
				return [
					_l(npc, "Grakk... morto? Por um novato de Rank F? A Guilda inteira está falando de você!"),
					_l(npc, "Rank E, oficialmente. E 200 de ouro. Aquele Tomo que ele deixou... leve ao ferreiro um dia."),
					_l(npc, "Os relatórios dizem que os demônios vêm da Floresta de Velmoor. É para lá que o Rank D vai."),
				]
			if g.flags.has("dryad_profane_dead") and not g.flags.has("rank_d"):
				g.flags["rank_d"] = true
				gs.gold += 350
				gs.guild_rank = "D"
				gs.add("ether", 2)
				return [
					_l(npc, "A Dríade de Velmoor... purificada? E você trouxe uma elfa junto?!"),
					_l(npc, "Rank D. 350 de ouro. Valemont, a capital, vai querer conhecer você."),
				]
			if g.flags.has("rank_e"):
				return [_l(npc, "Velmoor fica além do portal élfico, no fim do Bosque dos Chifres. Leve poções.")]
			if g.flags.has("q_imps_done"):
				return [_l(npc, "Grakk se esconde no sul do bosque, perto do lago. Cuidado com o leque de fogo.")]
			return [_l(npc, "Diabretes abatidos: %d/%d. O bosque fica ao sul da praça." % [g.quest_progress(QUEST_IMPS), QUEST_IMPS_GOAL])]
		"blacksmith":
			# Forge: crafts the first affordable recipe; otherwise says what the next one needs.
			for r in Data.recipes:
				if g.flags.has("forged_" + r["result"]):
					continue
				if gs.can_craft(r):
					g.flags["forged_" + r["result"]] = true
					gs.craft(r)
					return [
						_l(npc, "Material e ouro na mesa... Deixa comigo. *clang* *clang* *CLANG*"),
						_l(npc, "Pronto: %s. Está na sua bolsa — equipe no Grimório (Tab)." % Data.items[r["result"]]["name"]),
					]
			for r in Data.recipes:
				if g.flags.has("forged_" + r["result"]):
					continue
				var need := "%d de ouro" % int(r["gold"])
				for it in r["needs"]:
					need += ", %d× %s (você tem %d)" % [int(it[1]), Data.items[it[0]]["name"], gs.count(it[0])]
				return [
					_l(npc, "Próxima peça: %s." % Data.items[r["result"]]["name"]),
					_l(npc, "Preciso de " + need + "."),
					_l(npc, "Demônio fraco, arma fraca. Demônio forte... aí sim."),
				]
			return [_l(npc, "Já forjei tudo que sei. Os mestres de Valemont e Kharis têm mais segredos.")]
		"lumia":
			if g.flags.has("game_complete"):
				return [_l(npc, "Aetheria está em paz graças a você, Ren. Descanse. Explore. Viva.")]
			if not g.flags.has("lumia_blessed"):
				g.flags["lumia_blessed"] = true
				gs.add("potion", 5)
				gs.add("ether", 3)
				return final_blessing
			return [_l(npc, "A porta do salão do trono fica ao norte. Eu acredito em você.")]
		"sylra":
			if not g.flags.has("sylra_joined"):
				g.flags["sylra_joined"] = true
				return [
					_l(npc, "Um humano... com a centelha da deusa? Então a profecia era verdade."),
					_l(npc, "Sou Sylra, guardiã deste santuário. A Dríade do bosque sagrado foi corrompida pelos demônios."),
					_l(npc, "Sozinha não consigo chegar até ela. Meu arco é seu, Ren. Vamos purificar Velmoor."),
				]
			return [_l(npc, "Fique perto. Eu cuido dos que vierem pelos flancos.")]
		"guildmaster":
			if not g.flags.has("val_started"):
				g.flags["val_started"] = true
				return [
					_l(npc, "Então você é o novato que purificou Velmoor. Aldric, Mestre da Guilda de Valemont."),
					_l(npc, "Há três noites, um assassino encapuzado mata nobres e some em fumaça. Chamam-no de Sombra."),
					_l(npc, "Ele se esconde no beco ao sul da cidade, atrás da praça. Cuidado: ele aparece nas suas costas."),
					_l(npc, "Role no instante em que ele surgir. E leve poções — a lojista Dorna vende perto da fonte."),
				]
			if g.flags.has("assassin_shadow_dead") and not g.flags.has("rank_c"):
				g.flags["rank_c"] = true
				gs.gold += 600
				gs.guild_rank = "C"
				gs.add("spark_tome", 1)
				gs.add("sword_tome", 1)
				gs.add("ether", 3)
				return [
					_l(npc, "A Sombra... caiu. Valemont dorme em paz pela primeira vez em semanas."),
					_l(npc, "Rank C, 600 de ouro e dois Tomos que ele carregava (Centelha e Corte Crescente — use no Grimório). O capuz tinha o selo do Rei Demônio."),
					_l(npc, "Malgrath já tem espiões na capital. O deserto de Kharis guarda a próxima pista."),
				]
			if g.flags.has("rank_c"):
				return [_l(npc, "Kharis fica a leste, Ren. Siga a estrada além do portão da cidade.")]
			return [_l(npc, "A Sombra ainda está solta. Beco ao sul, atrás da praça.")]
		"shopkeeper":
			if not g.flags.has("bought_vest") and gs.gold >= 90:
				g.flags["bought_vest"] = true
				gs.gold -= 90
				gs.add("leather_vest", 1)
				return [_l(npc, "Um Colete de Couro, 90 de ouro: +5 DEF. Equipe no Grimório (Tab). Fale de novo para poções.")]
			if gs.gold >= 25:
				var eth := gs.count("potion") >= 5 and gs.gold >= 30
				gs.gold -= 30 if eth else 25
				gs.add("ether" if eth else "potion", 1)
				return [_l(npc, "Já tem poções de sobra. Leve um Éter Azul: 30 de ouro." if eth else "Uma Poção de Vida, 25 de ouro. Fale de novo para comprar mais.")]
			return [_l(npc, "Poção custa 25 de ouro. Volte quando tiver moedas dos demônios.")]
		"guard":
			return [_l(npc, "Cuidado depois do anoitecer. A Sombra ataca quem anda sozinho perto do beco sul.")]
		"noble":
			return [
				_l(npc, "Três condes assassinados em uma semana. E a Guilda manda um garoto de espada velha?"),
				_l(npc, "...Perdão. Dizem que você derrotou Grakk e a Dríade. Talvez haja esperança."),
			]
		"cleric":
			return [_l(npc, "A deusa Lumia abençoa quem enfrenta as trevas. Sinta a centelha em suas mãos, filho.")]
		"child":
			return [_l(npc, "Moço! Eu vi o homem de capuz entrar no beco! Ele sumiu na fumaça roxa!")]
		"villager":
			return [
				_l(npc, "Você é o forasteiro que caiu do céu? Dizem que a deusa ainda olha por nós."),
				_l(npc, "Desde que o Rei Demônio acordou, até o vento do sul cheira a enxofre."),
			]
	return [_l(npc, "...")]
