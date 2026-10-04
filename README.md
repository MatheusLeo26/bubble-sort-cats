# Bubble Sort Interativo com Gatos 🐱✨

Este é um projeto educativo e visual criado em Python com a biblioteca **pygame-ce**. 
O objetivo é visualizar de forma interativa e animada como o algoritmo de ordenação **Bubble Sort** funciona, utilizando adoráveis gatinhos!

Cada gatinho representa um número em um array `[7, 4, 2, 1, 8, 3, 6, 5]`. O programa permite que você acompanhe passo a passo a ordenação, com uma animação fluida de troca de posições quando os elementos precisam ser reordenados, além de destacar a linha do código Python que está sendo executada no momento.

## ✨ Novidades da Versão Atual
- **Arquitetura Testável**: A lógica do Bubble Sort foi separada em uma função geradora pura, permitindo cobrir a orquestração e as animações com testes unitários sem abrir janelas gráficas.
- **Visual Aprimorado**: O cenário foi desenhado em detalhes com papel de parede, rodapé, piso de madeira e até uma janelinha, usando apenas as primitivas gráficas do pygame. Gatos mudam de cor, de tamanho, e têm expressões (abrem os olhos ao serem comparados, ficam felizes ao serem ordenados).
- **Painéis Translúcidos**: Novo painel mostrando o estado atual (valores de `i` e `j`, número de comparações e trocas, array atual e velocidade).
- **Controles de Velocidade e Reinício**.

## 🚀 Como instalar e rodar

1. **Pré-requisitos**: 
   Você precisa ter o Python instalado na sua máquina (versão 3.8 ou superior recomendada).

2. **Instalar a biblioteca Pygame-CE**:
   Recomendamos o `pygame-ce` (Community Edition) para melhor performance e compatibilidade:
   ```bash
   pip install pygame-ce
   ```

3. **Executar o programa**:
   Navegue até a pasta do projeto e rode o arquivo principal:
   ```bash
   python bubble_sort_gatos.py
   ```

## 🎮 Controles Interativos

* **TECLA ESPAÇO**: Avança a execução do algoritmo passo a passo manualmente. Ideal para ler o painel de código e entender o que está acontecendo linha por linha.
* **TECLA ENTER**: Inicia (ou pausa) o **Modo Automático**. O algoritmo rodará sozinho.
* **TECLA R**: Reinicia a ordenação com o array original.
* **TECLAS + e - (ou Setas para Cima/Baixo)**: Aumentam ou diminuem a velocidade das animações.
* **TECLA ESC**: Sai da aplicação.

## 🧪 Testes Unitários

O projeto possui uma suíte robusta de testes (62 testes no total) usando o módulo `unittest` nativo. Os testes verificam a exatidão do gerador do Bubble Sort, das interpolações matemáticas, e da máquina de estados do visualizador, rodando sem abrir nenhuma janela (via driver SDL dummy).

Para rodar os testes, execute na raiz do projeto:
```bash
python -m unittest discover -s tests -v
```

Divirta-se aprendendo algoritmos!
