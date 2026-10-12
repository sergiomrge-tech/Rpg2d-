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


## Side quests handed out by the town services. Returns lines when the NPC offers or completes one, otherwise [].
func _side_quest_talk(npc: String) -> Array:
	var g := Game
	var gs: GameState = g.state
	match npc:
		"villager":
			if not g.flags.has("sq_horns_on"):
				g.flags["sq_horns_on"] = true
				return [_l(npc, "Ah, forasteiro! Minha sopa de chifre de diabrete é famosa... mas os caçadores sumiram."),
					_l(npc, "Traga-me 3 Chifres de Diabrete e eu lhe pago 40 de ouro e uma poção. Combinado?")]
			if not g.flags.has("sq_horns_done") and gs.count("imp_horn") >= 3:
				for i in 3:
					gs.take("imp_horn")
				gs.gold += 40
				gs.add("potion", 1)
				g.flags["sq_horns_done"] = true
				g.hud.quest_complete("Sopa da Tia Marta")
				return [_l(npc, "Três chifres lindos! Aqui, 40 de ouro e uma poção. Passe lá em casa quando quiser provar!")]
		"smith_v":
			if not g.flags.has("sq_forge_on"):
				g.flags["sq_forge_on"] = true
				return [_l(npc, "Humpf. Sou Hargrim, mestre de forja de Valemont. Minha fornalha está fria demais para o aço bom."),
					_l(npc, "Traga 4 Brasas Infernais e eu forjo um amuleto de brasa só para você. Negócio de anão: palavra e fogo.")]
			if not g.flags.has("sq_forge_done") and gs.count("hell_ember") >= 4:
				for i in 4:
					gs.take("hell_ember")
				gs.gold += 150
				gs.add("ember_charm", 1)
				g.flags["sq_forge_done"] = true
				g.hud.quest_complete("Brasas para a forja")
				return [_l(npc, "Brasas das boas! *clang* *clang*... Pronto: um Amuleto de Brasa e 150 de ouro. Equipe no Grimório.")]
		"shopkeeper":
			if not g.flags.has("sq_herbs_on"):
				g.flags["sq_herbs_on"] = true
				g.start_quest("q_insects")
				return [_l(npc, "Sou Dorna, a boticária. Os insetos gigantes soltam uma seiva rara que uso nas poções."),
					_l(npc, "Derrote 6 insetoides (mantídeos, besouros, vespas...) e eu lhe dou éteres, poções e ouro.")]
			if not g.flags.has("sq_herbs_done") and g.quest_progress("q_insects") >= 6:
				gs.gold += 120
				gs.add("ether", 3)
				gs.add("potion", 3)
				g.flags["sq_herbs_done"] = true
				g.hud.quest_complete("Seiva dos insetoides")
				return [_l(npc, "Que cheiro maravilhoso de seiva fresca! 120 de ouro, 3 éteres e 3 poções. Obrigada, herói!")]
		"tavern_keeper":
			if not g.flags.has("sq_mead_on"):
				g.flags["sq_mead_on"] = true
				return [_l(npc, "Escute, herói: o Capitão Brandt esqueceu de pagar o hidromel. De novo."),
					_l(npc, "Leve este barril ao quartel e diga que a casa cobra juros. Ele paga bem... e eu fico em paz.")]
		"guard_captain":
			if g.flags.has("sq_mead_on") and not g.flags.has("sq_mead_done"):
				gs.gold += 100
				gs.add("potion", 2)
				g.flags["sq_mead_done"] = true
				g.hud.quest_complete("Hidromel do Javali Dourado")
				return [_l(npc, "O barril da Bruna! ...Juros? Essa taverneira me conhece bem demais. Tome 100 de ouro e duas poções pelo transporte.")]
		"librarian":
			if not g.flags.has("sq_relics_on"):
				g.flags["sq_relics_on"] = true
				g.quests["q_relic_base"] = g.cache_count()
				return [_l(npc, "Silêncio... as ruínas e acampamentos esconderam relíquias em baús antigos."),
					_l(npc, "Abra 3 deles e eu lhe entrego um Tomo da Centelha da minha coleção pessoal.")]
			if not g.flags.has("sq_relics_done") and g.cache_count() - g.quest_progress("q_relic_base") >= 3:
				gs.add("spark_tome", 1)
				g.flags["sq_relics_done"] = true
				g.hud.quest_complete("Relíquias esquecidas")
				return [_l(npc, "Três relíquias! Magnífico. Tome o Tomo da Centelha: use-o no Grimório (Tab) e sua magia evoluirá.")]
	return []


func talk(npc: String) -> Array:
	var g := Game
	var gs: GameState = g.state
	var sq := _side_quest_talk(npc)
	if not sq.is_empty():
		return sq
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
		"blacksmith", "smith_v":
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
			return [
				_l(npc, "Bem-vindo ao meu boticário! Poções de vida, éteres azuis, um colete de couro se quiser..."),
				_l(npc, "Olhe as prateleiras com calma — e me vendendo suas sobras de demônio eu também pago bem."),
			]
		"tavern_keeper":
			var rumor := "O beco ao sul da cidade anda quieto demais. Quieto demais é pior que barulho."
			if g.flags.has("assassin_shadow_dead"):
				rumor = "Dizem que há ninhos de insetos gigantes nas florestas e no deserto. Quem os caça volta rico... ou não volta."
			if g.flags.has("kharis_done"):
				rumor = "Um forasteiro passou aqui falando de anões nas minas de Durnhold. Pediam ajuda contra um golem de brasa."
			return [
				_l(npc, "Bem-vindo ao Javali Dourado! Quartos lá atrás, comida quente aqui na frente."),
				_l(npc, rumor),
			]
		"inn_aurora":
			return [
				_l(npc, "Bem-vindo à Lanterna, forasteiro! Sou Hilda. Quarto limpo, cama macia e sopa fumegante."),
				_l(npc, "Durma o quanto precisar: de manhã você acorda novo em folha."),
			]
		"baker":
			return [
				_l(npc, "Pão fresquinho saindo do forno! Experimente o pão de mel — dizem que dá fôlego para a luta."),
				_l(npc, "E a torta de frutas silvestres? Mana de graça... bem, quase de graça."),
			]
		"stable_master":
			return [
				_l(npc, "Os cavalos da guarda não saem sem ordem do Capitão. Mas posso lhe dizer o caminho."),
				_l(npc, "Pelo portão norte você volta à floresta de Velmoor. Pelo leste, a estrada leva ao deserto de Kharis."),
				_l(npc, "Leve poções. O deserto não perdoa quem confia só na espada."),
			]
		"armorer":
			return [
				_l(npc, "Armaria Real de Valemont. Aço bom, couro curtido e peças com requisitos... nem todo braço aguenta uma couraça pesada."),
				_l(npc, "Suba sua Constituição e Força no Grimório (P), e volte. Veja o que tenho."),
			]
		"librarian":
			return [
				_l(npc, "Silêncio, por favor... ah, o herói da Centelha. Li sobre você nos relatos da Guilda."),
				_l(npc, "Os tomos de habilidade caem dos chefes mais poderosos. Cada Tomo da Centelha evolui sua magia."),
				_l(npc, "E guarde isto: os demônios insetoides das ruínas protegem tesouros. Mate-os com cuidado."),
			]
		"guard_captain":
			if g.flags.has("game_complete") or gs.ng_plus > 0:
				if Abyss.active:
					return [_l(npc, "Aguente firme, herói! A onda ainda não acabou!")]
				return [
					_l(npc, "Herói de Aetheria! Os pergaminhos falam de um Abismo sob Valemont, onde a escuridão nunca morreu."),
					_l(npc, "Cinco ondas de demônios, cada uma pior que a anterior. A última traz um general. Quem sobrevive leva tesouros lendários."),
					_l(npc, "Se cair, o Abismo se fecha e nada se perde — só o orgulho. Prepare-se: começa agora!"),
				]
			return [
				_l(npc, "Capitão Brandt, guarda de Valemont. As muralhas aguentam exércitos, mas não uma lâmina na escuridão."),
				_l(npc, "Se for caçar a Sombra, vá preparado. Ela ataca por trás."),
			]
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
