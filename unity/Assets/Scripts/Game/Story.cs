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
                    if (g.flags.Contains("rank_e"))
                        return new[] { new Line(npc, "Novas missões chegam em breve ao quadro. O Rank D exige ir à Floresta de Velmoor.") };
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
