================================================================================
EXPLICAÇÃO TÉCNICA - Life is Strange Remastered Subtitle Fix
================================================================================

Este arquivo documenta as razões técnicas por trás dos bugs de desaparecimento 
de legendas no Life is Strange Remastered e como o nosso Mod (a DLL XINPUT1_3) 
os soluciona, bem como o bypass do Aviso de Epilepsia.

--------------------------------------------------------------------------------
1. O BUG DAS LEGENDAS DESAPARECENDO
--------------------------------------------------------------------------------
No motor da Unreal Engine 4 (UE4), os textos localizados são tipicamente 
acessados por uma Chave (Key). A estrutura do Life is Strange Remastered mapeia 
cada fala para uma Key do tipo:
"Cue_E5_3B_ArtGallery_PhotoLook_Admirer1_050"

O problema:
Quando um episódio é carregado (por exemplo, ao pular cenas, transição de níveis, 
ou cutscenes dinâmicas), a Unreal Engine 4 precisa instanciar os "Atores" que 
falam as legendas. Em vez de usar os nomes exatos pré-cozidos (cooked) da 
Blueprint, o jogo invoca `MakeUniqueObjectName()`, que gera nomes únicos para as 
instâncias criadas em tempo de execução adicionando o sufixo "_C_<Número>" 
(ex: Cue_E5_..._Admirer1_050_C_129).

Como a função interna do jogo (`ULiSLocalizationManager::GetLocalizedText`) 
busca os textos estritamente pela Chave, o sufixo "_C_129" corrompe a Chave.
O jogo procura por "Cue_..._Admirer1_050_C_129", não encontra no dicionário, 
e as legendas desaparecem ou exibem placeholders do tipo "?Cue_..._C_129?".

A Solução (Nosso Mod):
Nós criamos um "Hook" (Interceptador) na memória da função original 
`GetLocalizedText` usando a biblioteca MinHook.
1. Nós deixamos o jogo tentar buscar a chave primeiro.
2. Se ele falhar (retornar string vazia ou placeholder), o nosso código entra 
   em ação.
3. Nós analisamos a Chave. Se ela tiver o sufixo "_C_<números>", nós removemos 
   o sufixo, voltando à Chave original limpa ("Cue_..._Admirer1_050").
4. Então, buscamos essa chave limpa em nossos dicionários (lidos dos `.cue` ou 
   `.pak`) e injetamos o texto diretamente no motor do jogo!

--------------------------------------------------------------------------------
2. POR QUE XINPUT1_3.DLL FUNCIONA (DLL PROXYING)
--------------------------------------------------------------------------------
O método que usamos para fazer o jogo carregar nosso código se chama "DLL Proxying" 
(ou DLL Hijacking).

Por padrão, quando o arquivo "LiS-Win64-Shipping.exe" inicia, o Windows carrega 
várias bibliotecas do sistema essenciais para o funcionamento do motor gráfico 
e controles (DirectX, bibliotecas de áudio, e o XInput para controles de Xbox).

A Unreal Engine 4, nativamente, solicita à API do Windows o carregamento do 
`XINPUT1_3.dll` localizado na pasta do sistema `C:\Windows\System32`.
O segredo é a Ordem de Busca do Windows (DLL Search Order): o Windows SEMPRE 
procura primeiro na pasta local onde o `.exe` do jogo está rodando, ANTES de 
procurar na pasta do sistema!

Então, nós criamos uma biblioteca falsa chamada `XINPUT1_3.dll` e a colocamos 
na pasta `Binaries\Win64` do jogo.
O jogo, inocentemente, carrega a NOSSA biblioteca achando que é a da Microsoft.
Nossa biblioteca "Mente" para o jogo: nós exportamos todas as funções reais de 
controle (como `XInputGetState`), mas passamos as requisições para a DLL 
verdadeira do sistema (que carregamos invisivelmente em segundo plano).
Enquanto atuamos como um "intermediário" invisível para os controles de Xbox, 
aproveitamos que agora estamos DENTRO da memória do jogo para rodar a nossa 
própria thread (SubtitleModThread), iniciar o MinHook, e sequestrar a função 
das legendas!

--------------------------------------------------------------------------------
3. BYPASS DA TELA DE EPILEPSIA (FMalloc Hijack)
--------------------------------------------------------------------------------
O Life is Strange Remastered possui um aviso de Epilepsia longo e inpulável 
quando você abre o jogo, programado para esperar o vídeo terminar antes de 
carregar o menu. Modders costumavam "deletar" o vídeo, mas ao deletar, o jogo 
caía num loop infinito ou "Crashava" porque o ponteiro de arquivo apontava para 
um endereço nulo.

A técnica avançada de bypass que os modders usam envolve mexer no `FMalloc`, 
o alocador de memória base da Unreal Engine.
Quando o jogo tenta alocar a string de carregamento do vídeo do aviso de Epilepsia, 
os bytes que configuram o ponteiro ou o tamanho dessa interface (UI) são interceptados 
e alterados na inicialização da Unreal (`FMemory::Malloc`). 
Ao pular a checagem da Flag ou forçar o tempo de execução do vídeo para 0 (zero) 
modificando as diretivas de montagem do executável logo após o `FMalloc`, o 
motor assume que a tela já terminou e imediatamente dispara o gatilho para carregar 
o Main Menu. É um pulo forçado no State Machine do jogo, bypassando os asserts 
(erros de checagem) que ocorreriam se o arquivo do vídeo fosse simplesmente deletado.

--------------------------------------------------------------------------------
4. ENGENHARIA REVERSA DAS TRADUÇÕES DE FÃS (Suporte a Mods Húngaros)
--------------------------------------------------------------------------------
Os fãs húngaros traduziram o jogo modificando os textos em Inglês ("INT"). 
Eles empacotam essas modificações num arquivo `pakchunk0-WindowsNoEditor_HU.pak`.
A Unreal Engine 4 monta (montagem virtual) esses arquivos `.pak` e os funde 
com os dados nativos do jogo.

O problema de compatibilidade ocorria porque o nosso Mod procurava os arquivos 
originais soltos `.cue` (AltData) caso as legendas falhassem. Como a tradução de 
fãs estava empacotada e não em arquivos soltos, o nosso Mod falhava em achar o 
texto Húngaro e devolvia o Inglês padrão da pasta AltData, sobrescrevendo a 
tradução.

A Solução C++ Pura (Sem dependências externas):
- Construímos um leitor nativo de Index da Unreal Engine V3 dentro do nosso 
  `xinput_proxy.cpp`.
- Ao abrir o jogo, nossa DLL vasculha a pasta `Paks` do jogo buscando arquivos 
  `.pak` externos (traduções de fãs).
- Nós fazemos a descompressão ZLIB em tempo real do conteúdo `.ini` da tradução.
- Analisamos (Parse) os textos diretamente do buffer de memória descompactado.
- Atualizamos nossos dicionários internos (`g_AltDataDicts`).
Dessa forma, caso a Chave falhe, nosso mod buscará o texto já em Húngaro, e não 
o texto em Inglês! Tudo isso feito de forma imperceptível, sem atrasar o 
carregamento do jogo.
