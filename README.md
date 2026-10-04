# Bubble Sort Interativo com Gatos 🐱✨

Este é um projeto educativo e visual criado em Python com a biblioteca **Pygame**. 
O objetivo é visualizar de forma interativa e animada como o algoritmo de ordenação **Bubble Sort** funciona, utilizando adoráveis gatinhos!

Cada gatinho representa um número em um array `[7, 4, 2, 1, 8, 3, 6, 5]`. O programa permite que você acompanhe passo a passo a ordenação, com uma animação fluida de troca de posições quando os elementos precisam ser reordenados, além de destacar a linha do código Python que está sendo executada no momento.

## 🚀 Como instalar e rodar

1. **Pré-requisitos**: 
   Você precisa ter o Python instalado na sua máquina (versão 3.6 ou superior recomendada).

2. **Instalar a biblioteca Pygame**:
   Abra o seu terminal ou prompt de comando e execute:
   ```bash
   pip install pygame
   ```

3. **Executar o programa**:
   Navegue até a pasta do projeto e rode o arquivo principal:
   ```bash
   python main.py
   ```

## 🎮 Controles Interativos

A interface gráfica possui as seguintes opções para facilitar o aprendizado:

* **TECLA ESPAÇO**: Avança a execução do algoritmo passo a passo manualmente. Ideal para ler o painel de código e entender o que está acontecendo linha por linha.
* **TECLA ENTER**: Inicia (ou pausa) o **Modo Automático**. O algoritmo rodará sozinho com um intervalo de tempo predefinido entre os passos e as animações ocorrerão de forma contínua até o final.

## 🧠 Como Funciona

- **Interface Lúdica**: Um cenário aconchegante com os gatinhos desenhados no centro da tela.
- **Animações de Troca**: Toda vez que a condição `v[j] > v[j+1]` for verdadeira, os gatinhos trocam de lugar através de uma interpolação parabólica (um passa por cima e o outro por baixo).
- **Painel de Código em Tempo Real**: Na lateral esquerda há um painel translúcido contendo o código Python original do Bubble Sort. Uma barra amarela marca exatamente a linha correspondente ao passo atual da execução.

Divirta-se aprendendo algoritmos!
