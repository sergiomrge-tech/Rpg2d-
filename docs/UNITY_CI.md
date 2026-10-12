# Unity na nuvem (GitHub Actions)

O workflow `.github/workflows/unity.yml` compila o projeto `unity/`, roda o jogo em modo automático
e publica screenshots + log no branch `ci-shots`. Para funcionar, ele precisa de uma licença Unity
**Personal (gratuita)** configurada como secret do repositório:

1. Instale o **Unity Hub** num PC (Windows/Mac/Linux), entre com sua conta Unity (grátis) e ative a licença
   *Personal* (Hub → Preferências → Licenças → Adicionar → Personal).
2. Abra o arquivo de licença gerado:
   - Windows: `C:\ProgramData\Unity\Unity_lic.ulf`
   - macOS: `/Library/Application Support/Unity/Unity_lic.ulf`
   - Linux: `~/.local/share/unity3d/Unity/Unity_lic.ulf`
3. No GitHub: repositório → **Settings → Secrets and variables → Actions → New repository secret**:
   - `UNITY_LICENSE` = conteúdo inteiro do arquivo `.ulf`
   - `UNITY_EMAIL` = e-mail da conta Unity
   - `UNITY_PASSWORD` = senha da conta Unity

Pronto: a cada push na pasta `unity/`, o build roda sozinho.

Para jogar no seu PC: abra a pasta `unity/` no Unity Hub (Unity 2022.3 LTS), abra a cena `Assets/Scenes/Main`
(ou qualquer cena vazia) e aperte Play. O jogo se monta sozinho via código.
