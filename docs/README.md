# Documentação do Mod de Legendas (Life is Strange Remastered)

Bem-vindo à documentação técnica do **LiS Remastered Universal Subtitle Fix**.

Este mod foi criado para corrigir um bug grave na versão Remastered do jogo, onde as legendas desapareciam aleatoriamente (exibindo textos quebrados como `Cue_E2_1A_KateRoom_CHKate_Phase01_Max_036`) durante transições de cena e encerramentos de episódios.

## Índice

1. [Explicação Técnica do Bug e da Solução Base](./EXPLICACAO_TECNICA.md)
   - Detalha como a Unreal Engine perde o mapa de strings da memória.
   - Explica a técnica de **DLL Proxying** (XINPUT1_3.dll).
   - Mostra como interceptamos o `FMemory::Malloc` para evitar o crash de alocação (Aviso de Epilepsia).
   - Explica o hook na função `GetLocalizedText`.

2. [Suporte a Traduções de Fãs (.pak)](./FAN_TRANSLATIONS.md)
   - Explica como o mod detecta e carrega traduções não oficiais de fãs feitas em pacotes Unreal Engine (V3).
   - Detalha a extração em tempo real e descompressão `zlib` dos blocos de dados.
