# W-Pack

### Geração de imagens Project-source-first para ChatGPT

[English](./README.md) · [한국어](./README.ko.md) · [日本語](./README.ja.md) · **Português (Brasil)**

O W-Pack v0.4 usa por padrão as referências persistentes de um Project do ChatGPT e mantém separadas as autoridades de estilo, personagem, pose, composição, proporção e item.

## Principais mudanças da v0.4

- O perfil `DEFAULT` do Project é ativado automaticamente.
- Uma única referência STYLE é promovida internamente a `STYLE_CORE`.
- Meio visual, nível de realismo, contornos, abstração, valores/sombras, cor, textura e fundo recebem proteção de fidelidade.
- O fluxo sempre começa com uma única geração FRESH.
- Somente quando a estrutura passa e o estilo falha é permitido um único `SINGLE_RESTYLE`.
- Não há restyle recursivo nem terceira geração automática.
- Imagens anexadas no chat funcionam como overrides ou complementos temporários.

Na recuperação, apenas o candidato recém-gerado (`STRUCTURE_EDIT_TARGET`) e o STYLE_CORE são usados. Identidade, pose, composição, câmera, relações espaciais, objetos e condições da cena são preservados; apenas o estilo de renderização muda.

Versão atual: `WPACK_v0.4.0-chat-native`
