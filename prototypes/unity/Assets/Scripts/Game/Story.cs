using System.Collections.Generic;

namespace Aetheria
{
    /// <summary>Chapter 1 script: the hero (Ren Takamura, office worker in Tokyo) dies saving a child, wakes in
    /// Aetheria by the goddess Lumia's will, joins the Adventurers' Guild at rank F. Goal of the saga: the Demon King.</summary>
    public static class Story
    {
        public struct Line
        {
            public string who, text;
            public Line(string w, string t) { who = w; text = t; }
        }

        public class Region
        {
            public string map, title, npc, boss, bossName, intro, start, done, rank;
            public bool AllDead(System.Collections.Generic.HashSet<string> flags)
            {
                foreach (var b in boss.Split(',')) if (!flags.Contains(b + "_dead")) return false;
                return true;
            }
            public int gold;
            public string[] reward;
            public Line[] hello, back, thanks;
        }

        /// <summary>Chapter 4–7: each region has a guide NPC, a boss and a rank/gear reward.</summary>
        public static readonly Region[] Regions =
        {
            new Region
            {
                map = "kharis", title = "Deserto de Kharis", npc = "nomad", boss = "scorpion_demon", bossName = "o Demônio Escorpião", start = "rq_nomad", done = "kharis_done",
                rank = "B", gold = 900, reward = new[] { "ether:3", "potion:3" },
                hello = new[]
                {
                    new Line("nomad", "Forasteiro de Valemont? A areia sussurra seu nome. Sou Hasim, guia das caravanas de Kharis."),
                    new Line("nomad", "Há um Demônio Escorpião no coração das obeliscos, a leste. Ele soterrou duas caravanas e rouba o oásis."),
                    new Line("nomad", "Ele ataca com as pinças em sequência e bate com a cauda no chão. Role para o lado, nunca para trás."),
                },
                back = new[] { new Line("nomad", "O ferrão do deserto ainda vive. Siga a trilha a leste, depois do oásis, até os obeliscos.") },
                thanks = new[]
                {
                    new Line("nomad", "O Escorpião... morto! O oásis voltará a ser nosso. Tome 900 de ouro e minha gratidão."),
                    new Line("nomad", "A Guilda o promove ao Rank B. O caminho leste leva às Minas de Durnhold — os anões pedem ajuda."),
                },
            },
            new Region
            {
                map = "mines", title = "Minas de Durnhold", npc = "dwarf", boss = "ember_golem", bossName = "o Golem de Brasa", start = "rq_dwarf", done = "mines_done",
                rank = "B", gold = 1500, reward = new[] { "potion:3", "hell_ember:3" },
                hello = new[]
                {
                    new Line("dwarf", "Por Durnhold! Um humano nas minas! Sou Durnok. Os demônios acordaram o Golem de Brasa na grande forja."),
                    new Line("dwarf", "Ele é puro magma. Bate forte, e a cada golpe a rocha em volta racha. Fique longe dos cristais vermelhos."),
                    new Line("dwarf", "Se você o derrubar, eu mesmo lhe entrego a couraça que meu avô forjou."),
                },
                back = new[] { new Line("dwarf", "A forja fica ao leste, entre os cristais vermelhos. Leve poções, rapaz.") },
                thanks = new[]
                {
                    new Line("dwarf", "O Golem caiu! A forja volta a esquentar para o bem. 1500 de ouro e as brasas que sobraram são suas."),
                    new Line("dwarf", "O pântano de Mirewail fica depois da saída leste. A bruxa de lá sabe de coisas que nem os anões sabem."),
                },
            },
            new Region
            {
                map = "mirewail", title = "Pântano de Mirewail", npc = "witch", boss = "succubus_mirael", bossName = "Mirael, a Súcubo", start = "rq_witch", done = "mirewail_done",
                rank = "A", gold = 2200, reward = new[] { "ether:4", "potion:4" },
                hello = new[]
                {
                    new Line("witch", "Hehehe... um herói. Morgana, cuidadora do brejo. Cheiro de centelha de deusa em você, criança."),
                    new Line("witch", "Mirael, uma súcubo a serviço de Malgrath, encantou o pântano. Ela vive na ilha ao sul, cercada de bruma."),
                    new Line("witch", "Ela lança fogo violeta e chama espectros. Mate os espectros primeiro, ou eles o cercam."),
                },
                back = new[] { new Line("witch", "A ilha de Mirael fica ao sul das pontes. Não pise na água escura, criança.") },
                thanks = new[]
                {
                    new Line("witch", "Hehehe! A súcubo caiu. 2200 de ouro, e este conselho: nos Picos Gelados há um templo da sua deusa."),
                    new Line("witch", "Rank A, pela Guilda. Poucos chegam tão longe. Vá — o último general antes do castelo espera no gelo."),
                },
            },
            new Region
            {
                map = "peaks", title = "Picos Gelados", npc = "monk", boss = "ice_demon", bossName = "o Demônio de Gelo", start = "rq_monk", done = "peaks_done",
                rank = "A", gold = 3000, reward = new[] { "potion:5", "ether:5" },
                hello = new[]
                {
                    new Line("monk", "Que Lumia o guie, Ren. Sou Ilan, guardião deste templo. A deusa fala de você nas orações."),
                    new Line("monk", "O Demônio de Gelo congelou a nascente sagrada. Ele sopra rajadas em leque e invoca diabretes gélidos."),
                    new Line("monk", "Ao norte está o castelo de Valemont, tomado por demônios. Mas antes, liberte a nascente."),
                },
                back = new[] { new Line("monk", "A nascente congelada fica ao sul do templo, entre os espinhos de gelo.") },
                thanks = new[]
                {
                    new Line("monk", "A nascente corre de novo! Lumia sorri. Aceite 3000 de ouro e nossa bênção."),
                    new Line("monk", "O Capítulo seguinte o levará ao Castelo tomado. A Guilda o aguarda como Rank A. Que a centelha o guie."),
                },
            },
            new Region
            {
                map = "castle", title = "Castelo de Valemont", npc = "elowen", boss = "vorath", bossName = "o General Vorath", start = "rq_elowen", done = "castle_done",
                rank = "A", gold = 4000, reward = new[] { "royal_plate:1", "potion:5", "ether:3" },
                hello = new[]
                {
                    new Line("elowen", "Alto! ...Você é Ren? O herói de Velmoor? Sou a capitã Elowen, última da Guarda Real."),
                    new Line("elowen", "Malgrath mandou o General Vorath tomar o castelo. A rainha foi levada. Os cavaleiros demoníacos patrulham o pátio."),
                    new Line("elowen", "Vorath luta com uma montante negra: golpes lentos, mas devastadores, e um impacto no chão. Aguarde o brilho vermelho e role."),
                },
                back = new[] { new Line("elowen", "Vorath guarda a porta do salão do trono, ao norte do pátio. Que Lumia o proteja.") },
                thanks = new[]
                {
                    new Line("elowen", "Vorath caiu... o castelo é nosso! A rainha foi levada para as Terras Devastadas, a leste."),
                    new Line("elowen", "Esta armadura real é sua, Ren. 4000 de ouro também. Salve-a. Salve Aetheria."),
                },
            },
            new Region
            {
                map = "wastelands", title = "Terras Devastadas", npc = "cedric", boss = "thornmaw_alpha,velka_flamebeak,krull_chainlord,morgash_ironhorn",
                bossName = "os quatro Generais", start = "rq_cedric", done = "wastelands_done",
                rank = "S", gold = 6000, reward = new[] { "lumia_pendant:1", "potion:6", "ether:6" },
                hello = new[]
                {
                    new Line("cedric", "Ren! Então os boatos eram verdade. Cedric, veterano da Resistência. Estamos escondidos aqui há anos."),
                    new Line("cedric", "A Cidadela de Malgrath fica a leste, selada por quatro generais: Thornmaw ao noroeste, Velka ao nordeste, Krull ao sudoeste e Morgash ao sudeste."),
                    new Line("cedric", "Cada um guarda um selo. Derrube os quatro e o portão do inferno se abrirá. Não há outro caminho."),
                    new Line("cedric", "Cada general luta diferente: espinhos, fogo em leque, correntes e martelo. Estude o padrão antes de atacar."),
                },
                back = new[] { new Line("cedric", "Faltam selos, Ren. Os quatro generais ficam nos cantos do mapa.") },
                thanks = new[]
                {
                    new Line("cedric", "Os quatro selos caíram! O portão a leste vai abrir. Você é a lenda que esperávamos."),
                    new Line("cedric", "Rank S, o mais alto da Guilda. Leve este pingente, ele pertenceu a um sacerdote de Lumia. Boa sorte, herói."),
                },
            },
        };

        public const string QuestImps = "q_imps";
        public const int QuestImpsGoal = 5;

        public static string NameOf(string id)
        {
            switch (id)
            {
                case "receptionist": return "Elina, da Guilda";
                case "blacksmith": return "Borin, o Ferreiro";
                case "villager": return "Tia Marta";
                case "lumia": return "Deusa Lumia";
                case "sylra": return "Sylra";
                case "elowen": return "Capitã Elowen";
                case "cedric": return "Cedric, o Veterano";
                case "nomad": return "Hasim, Guia do Deserto";
                case "dwarf": return "Durnok, Mestre Minerador";
                case "witch": return "Bruxa Morgana";
                case "monk": return "Monge Ilan";
                case "guildmaster": return "Mestre Aldric";
                case "guard": return "Guarda do Portão";
                case "noble": return "Lady Seraphine";
                case "cleric": return "Irmã Maelis";
                case "child": return "Pip";
                case "shopkeeper": return "Dorna, a Lojista";
                default: return id;
            }
        }

        public static readonly Line[] FinalBlessing =
        {
            new Line("lumia", "Ren. Você chegou ao fim da estrada. Daqui em diante, nem eu posso segui-lo."),
            new Line("lumia", "Malgrath espera no salão do trono. Ele muda a cada vez que cai um pouco — não se apresse."),
            new Line("lumia", "Leve estas poções. E lembre-se: você nunca foi fraco. Só ainda não tinha crescido."),
            new Line("lumia", "Vá. Salve o meu mundo."),
        };

        public static readonly Line[] Ending =
        {
            new Line("@scene", "malgrath_fall"),
            new Line("", "Malgrath cai de joelhos. A coroa de chifres racha, e a escuridão que cobria Aetheria se desfaz em cinzas douradas."),
            new Line("@scene", "sunrise_peaks"),
            new Line("lumia", "Está feito. O Rei Demônio caiu. O sol voltou a nascer sobre Aetheria."),
            new Line("sylra", "Eu sempre soube que você chegaria até aqui. Velmoor já floresce de novo, Ren."),
            new Line("lumia", "Ren Takamura. Você deu a sua vida por uma criança e, em outro mundo, por todo um povo."),
            new Line("lumia", "Posso lhe oferecer um último presente: voltar para casa. Ou ficar."),
            new Line("@scene", "vista"),
            new Line("", "Ren olha o amanhecer sobre as montanhas. Pela primeira vez desde que chegou, não tem pressa."),
            new Line("", "Ele decide ficar. Há uma Guilda a visitar, uma elfa que precisa de um companheiro de aventuras, e um mundo inteiro por explorar."),
        };

        public const string Credits =
            "CRÔNICAS DE AETHERIA\nA Centelha\n\n\n" +
            "— Elenco —\n\nRen Takamura — o herói\nDeusa Lumia\nSylra, arqueira de Velmoor\nMestre Aldric\nCapitã Elowen\nCedric, o Veterano\n\n" +
            "— Os Generais —\n\nGrakk · Dríade Profanada · Assassino Sombrio\nEscorpião de Kharis · Golem de Brasa · Mirael\nDemônio de Gelo · General Vorath\n\nMalgrath, o Rei Demônio\n\n\n" +
            "— Feito com —\n\nUnity · Python + Cairo (toda a arte gerada por código)\nClaude Code\n\n\n" +
            "Obrigado por jogar.\n\n\nFIM";

        public static readonly Line[] Prologue =
        {
            new Line("@scene", "tokyo"),
            new Line("", "Tóquio, 23h47. Uma buzina. Um caminhão. Uma criança no meio da rua."),
            new Line("", "Você empurrou a menina para longe... e o mundo ficou branco."),
            new Line("@scene", "void"),
            new Line("lumia", "Ren Takamura. Sua vida terminou cedo demais — e com coragem."),
            new Line("lumia", "Meu mundo, Aetheria, está sendo devorado pelo Rei Demônio Malgrath. Preciso de alguém assim."),
            new Line("lumia", "Não posso lhe dar força. Só uma centelha. O resto... você terá de conquistar."),
            new Line("@scene", "aurora_dawn"),
            new Line("", "Você desperta na Vila de Aurora, com uma espada velha e uma faísca de magia na palma da mão."),
        };

        public static Line[] Talk(string npc, Game g)
        {
            var gs = g.state;
            foreach (var r in Regions)
            {
                if (r.npc != npc) continue;
                if (g.flags.Contains(r.done)) return new[] { new Line(npc, "Vá em frente, Ren. A próxima luta é sua.") };
                if (r.AllDead(g.flags))
                {
                    g.flags.Add(r.done);
                    gs.gold += r.gold;
                    gs.guildRank = r.rank;
                    foreach (var rw in r.reward) { var kv = rw.Split(':'); gs.Add(kv[0], int.Parse(kv[1])); }
                    return r.thanks;
                }
                if (!g.flags.Contains(r.start)) { g.flags.Add(r.start); return r.hello; }
                return r.back;
            }
            switch (npc)
            {
                case "receptionist":
                    if (!g.flags.Contains("guild_joined"))
                    {
                        g.flags.Add("guild_joined");
                        g.StartQuest(QuestImps);
                        return new[]
                        {
                            new Line(npc, "Bem-vindo à Guilda dos Aventureiros de Aurora! Novo por aqui? Dá pra ver pela espada enferrujada."),
                            new Line(npc, "Registrei você no Rank F. Todo mundo começa do fundo — até os heróis das lendas."),
                            new Line(npc, "Diabretes estão saindo do Bosque dos Chifres, ao sul. Elimine 5 e traga os chifres."),
                            new Line(npc, "Cuidado: eles brilham em vermelho antes de atacar. Role [Espaço] nessa hora. Sério."),
                        };
                    }
                    if (g.QuestProgress(QuestImps) >= QuestImpsGoal && !g.flags.Contains("q_imps_done"))
                    {
                        g.flags.Add("q_imps_done");
                        gs.gold += 60;
                        gs.Add("potion", 2);
                        return new[]
                        {
                            new Line(npc, "Cinco diabretes?! E voltou inteiro! Aqui estão 60 de ouro e duas poções."),
                            new Line(npc, "Mas há algo pior: um diabrete ancião, Grakk, comanda os outros no fundo do bosque."),
                            new Line(npc, "Derrote Grakk e a Guilda o promove ao Rank E. Ele cospe fogo em leque — não fique parado."),
                        };
                    }
                    if (g.flags.Contains("grakk_dead") && !g.flags.Contains("rank_e"))
                    {
                        g.flags.Add("rank_e");
                        gs.gold += 200;
                        gs.guildRank = "E";
                        return new[]
                        {
                            new Line(npc, "Grakk... morto? Por um novato de Rank F? A Guilda inteira está falando de você!"),
                            new Line(npc, "Rank E, oficialmente. E 200 de ouro. Aquele Tomo que ele deixou... leve ao ferreiro um dia."),
                            new Line(npc, "Os relatórios dizem que os demônios vêm da Floresta de Velmoor. É para lá que o Rank D vai."),
                        };
                    }
                    if (g.flags.Contains("dryad_profane_dead") && !g.flags.Contains("rank_d"))
                    {
                        g.flags.Add("rank_d");
                        gs.gold += 350;
                        gs.guildRank = "D";
                        gs.Add("ether", 2);
                        return new[]
                        {
                            new Line(npc, "A Dríade de Velmoor... purificada? E você trouxe uma elfa junto?!"),
                            new Line(npc, "Rank D. 350 de ouro. Valemont, a capital, vai querer conhecer você."),
                        };
                    }
                    if (g.flags.Contains("rank_e"))
                        return new[] { new Line(npc, "Velmoor fica além do portal élfico, no fim do Bosque dos Chifres. Leve poções.") };
                    if (g.flags.Contains("q_imps_done"))
                        return new[] { new Line(npc, "Grakk se esconde no sul do bosque, perto do lago. Cuidado com o leque de fogo.") };
                    return new[] { new Line(npc, $"Diabretes abatidos: {g.QuestProgress(QuestImps)}/{QuestImpsGoal}. O bosque fica ao sul da praça.") };
                case "blacksmith":
                {
                    // Forge: crafts the first affordable recipe; otherwise says what the next one needs.
                    foreach (var r in Data.Recipes)
                    {
                        if (g.flags.Contains("forged_" + r.result)) continue;
                        if (gs.CanCraft(r))
                        {
                            g.flags.Add("forged_" + r.result);
                            gs.Craft(r);
                            var it = Data.Items[r.result];
                            return new[]
                            {
                                new Line(npc, "Material e ouro na mesa... Deixa comigo. *clang* *clang* *CLANG*"),
                                new Line(npc, $"Pronto: {it.name}. Está na sua bolsa — equipe no Grimório (Tab)."),
                            };
                        }
                    }
                    foreach (var r in Data.Recipes)
                    {
                        if (g.flags.Contains("forged_" + r.result)) continue;
                        string need = $"{r.gold} de ouro";
                        foreach (var (item, n) in r.needs) need += $", {n}× {Data.Items[item].name} (você tem {gs.Count(item)})";
                        return new[]
                        {
                            new Line(npc, $"Próxima peça: {Data.Items[r.result].name}."),
                            new Line(npc, "Preciso de " + need + "."),
                            new Line(npc, "Demônio fraco, arma fraca. Demônio forte... aí sim."),
                        };
                    }
                    return new[] { new Line(npc, "Já forjei tudo que sei. Os mestres de Valemont e Kharis têm mais segredos.") };
                }
                case "lumia":
                    if (g.flags.Contains("game_complete")) return new[] { new Line(npc, "Aetheria está em paz graças a você, Ren. Descanse. Explore. Viva.") };
                    if (!g.flags.Contains("lumia_blessed"))
                    {
                        g.flags.Add("lumia_blessed");
                        gs.Add("potion", 5);
                        gs.Add("ether", 3);
                        return FinalBlessing;
                    }
                    return new[] { new Line(npc, "A porta do salão do trono fica ao norte. Eu acredito em você.") };
                case "sylra":
                    if (!g.flags.Contains("sylra_joined"))
                    {
                        g.flags.Add("sylra_joined");
                        return new[]
                        {
                            new Line(npc, "Um humano... com a centelha da deusa? Então a profecia era verdade."),
                            new Line(npc, "Sou Sylra, guardiã deste santuário. A Dríade do bosque sagrado foi corrompida pelos demônios."),
                            new Line(npc, "Sozinha não consigo chegar até ela. Meu arco é seu, Ren. Vamos purificar Velmoor."),
                        };
                    }
                    return new[] { new Line(npc, "Fique perto. Eu cuido dos que vierem pelos flancos.") };
                case "guildmaster":
                    if (!g.flags.Contains("val_started"))
                    {
                        g.flags.Add("val_started");
                        return new[]
                        {
                            new Line(npc, "Então você é o novato que purificou Velmoor. Aldric, Mestre da Guilda de Valemont."),
                            new Line(npc, "Há três noites, um assassino encapuzado mata nobres e some em fumaça. Chamam-no de Sombra."),
                            new Line(npc, "Ele se esconde no beco ao sul da cidade, atrás da praça. Cuidado: ele aparece nas suas costas."),
                            new Line(npc, "Role no instante em que ele surgir. E leve poções — a lojista Dorna vende perto da fonte."),
                        };
                    }
                    if (g.flags.Contains("assassin_shadow_dead") && !g.flags.Contains("rank_c"))
                    {
                        g.flags.Add("rank_c");
                        gs.gold += 600;
                        gs.guildRank = "C";
                        gs.Add("spark_tome", 1);
                        gs.Add("sword_tome", 1);
                        gs.Add("ether", 3);
                        return new[]
                        {
                            new Line(npc, "A Sombra... caiu. Valemont dorme em paz pela primeira vez em semanas."),
                            new Line(npc, "Rank C, 600 de ouro e dois Tomos que ele carregava (Centelha e Corte Crescente — use no Grimório). O capuz tinha o selo do Rei Demônio."),
                            new Line(npc, "Malgrath já tem espiões na capital. O deserto de Kharis guarda a próxima pista."),
                        };
                    }
                    if (g.flags.Contains("rank_c"))
                        return new[] { new Line(npc, "Kharis fica a leste. Os Capítulos seguintes chegam em breve, Ren.") };
                    return new[] { new Line(npc, "A Sombra ainda está solta. Beco ao sul, atrás da praça.") };
                case "shopkeeper":
                    if (!g.flags.Contains("bought_vest") && gs.gold >= 90)
                    {
                        g.flags.Add("bought_vest");
                        gs.gold -= 90;
                        gs.Add("leather_vest", 1);
                        return new[] { new Line(npc, "Um Colete de Couro, 90 de ouro: +5 DEF. Equipe no Grimório (Tab). Fale de novo para poções.") };
                    }
                    if (gs.gold >= 25)
                    {
                        bool eth = gs.Count("potion") >= 5 && gs.gold >= 30;
                        gs.gold -= eth ? 30 : 25;
                        gs.Add(eth ? "ether" : "potion", 1);
                        return new[] { new Line(npc, eth ? "Já tem poções de sobra. Leve um Éter Azul: 30 de ouro." : "Uma Poção de Vida, 25 de ouro. Fale de novo para comprar mais.") };
                    }
                    return new[] { new Line(npc, "Poção custa 25 de ouro. Volte quando tiver moedas dos demônios.") };
                case "guard":
                    return new[] { new Line(npc, "Cuidado depois do anoitecer. A Sombra ataca quem anda sozinho perto do beco sul.") };
                case "noble":
                    return new[]
                    {
                        new Line(npc, "Três condes assassinados em uma semana. E a Guilda manda um garoto de espada velha?"),
                        new Line(npc, "...Perdão. Dizem que você derrotou Grakk e a Dríade. Talvez haja esperança."),
                    };
                case "cleric":
                    return new[] { new Line(npc, "A deusa Lumia abençoa quem enfrenta as trevas. Sinta a centelha em suas mãos, filho.") };
                case "child":
                    return new[] { new Line(npc, "Moço! Eu vi o homem de capuz entrar no beco! Ele sumiu na fumaça roxa!") };
                case "villager":
                    return new[]
                    {
                        new Line(npc, "Você é o forasteiro que caiu do céu? Dizem que a deusa ainda olha por nós."),
                        new Line(npc, "Desde que o Rei Demônio acordou, até o vento do sul cheira a enxofre."),
                    };
            }
            return new[] { new Line(npc, "...") };
        }
    }
}
