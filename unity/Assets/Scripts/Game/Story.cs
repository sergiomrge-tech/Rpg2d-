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
                case "guildmaster": return "Mestre Aldric";
                case "guard": return "Guarda do Portão";
                case "noble": return "Lady Seraphine";
                case "cleric": return "Irmã Maelis";
                case "child": return "Pip";
                case "shopkeeper": return "Dorna, a Lojista";
                default: return id;
            }
        }

        public static readonly Line[] Prologue =
        {
            new Line("", "Tóquio, 23h47. Uma buzina. Um caminhão. Uma criança no meio da rua."),
            new Line("", "Você empurrou a menina para longe... e o mundo ficou branco."),
            new Line("lumia", "Ren Takamura. Sua vida terminou cedo demais — e com coragem."),
            new Line("lumia", "Meu mundo, Aetheria, está sendo devorado pelo Rei Demônio Malgrath. Preciso de alguém assim."),
            new Line("lumia", "Não posso lhe dar força. Só uma centelha. O resto... você terá de conquistar."),
            new Line("", "Você desperta na Vila de Aurora, com uma espada velha e uma faísca de magia na palma da mão."),
        };

        public static Line[] Talk(string npc, Game g)
        {
            var gs = g.state;
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
                    if (!g.flags.Contains("sword_horn") && gs.Count("imp_horn") >= 5 && gs.gold >= 80)
                    {
                        g.flags.Add("sword_horn");
                        for (int i = 0; i < 5; i++) gs.Take("imp_horn");
                        gs.gold -= 80;
                        gs.atk += 6;
                        return new[]
                        {
                            new Line(npc, "Cinco chifres e 80 de ouro... Deixa comigo. *clang* *clang* *CLANG*"),
                            new Line(npc, "Lâmina de Chifre. Corta demônio como se fosse pão. Seu ataque subiu +6."),
                        };
                    }
                    if (g.flags.Contains("sword_horn"))
                        return new[] { new Line(npc, "Quer algo melhor? Brasas Infernais. Muitas. E um demônio de verdade pra testar.") };
                    return new[]
                    {
                        new Line(npc, $"Hm. Essa lâmina não corta nem manteiga. Traga 5 Chifres de Diabrete e 80 de ouro (você tem {gs.Count("imp_horn")})."),
                        new Line(npc, "Com material demoníaco eu forjo coisa de verdade. Demônio fraco, arma fraca. Demônio forte..."),
                    };
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
                        gs.Add("ether", 3);
                        return new[]
                        {
                            new Line(npc, "A Sombra... caiu. Valemont dorme em paz pela primeira vez em semanas."),
                            new Line(npc, "Rank C, 600 de ouro e um Tomo que ele carregava. O capuz tinha o selo do Rei Demônio."),
                            new Line(npc, "Malgrath já tem espiões na capital. O deserto de Kharis guarda a próxima pista."),
                        };
                    }
                    if (g.flags.Contains("rank_c"))
                        return new[] { new Line(npc, "Kharis fica a leste. Os Capítulos seguintes chegam em breve, Ren.") };
                    return new[] { new Line(npc, "A Sombra ainda está solta. Beco ao sul, atrás da praça.") };
                case "shopkeeper":
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
