"""
Bubble Sort com Gatos
=====================

Visualizador interativo e animado do algoritmo Bubble Sort feito com pygame.
Cada número do array é um gato desenhado apenas com formas geométricas
(círculos, elipses, triângulos e linhas), com o número na barriga.

Arquitetura (pensada para ser testável):
    * ``gerar_passos_bubble_sort`` -> função PURA (sem pygame) que executa o
      Bubble Sort e devolve, um a um, os "passos" do algoritmo (qual linha do
      código está rodando, valores de i/j, estado do array...).
    * ``GatoElemento``            -> guarda posição, número e animação de um gato.
    * ``VisualizadorBubbleSort``  -> consome os passos, anima os gatos,
      desenha a tela e trata o teclado.

Controles:
    ESPAÇO  -> avança um passo (pausa o modo automático, se estiver ligado)
    ENTER   -> liga/desliga o modo automático (recomeça se já terminou)
    R       -> reinicia a ordenação
    + / -   -> aumenta / diminui a velocidade (setas cima/baixo também)
    ESC     -> sai
"""

from __future__ import annotations

import math
import os
from dataclasses import dataclass
from typing import Iterator, List, Optional, Sequence, Tuple

# Esconde a mensagem de boas-vindas que o pygame imprime no terminal
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import pygame  # noqa: E402  (precisa vir depois da variável de ambiente)

Cor = Tuple[int, int, int]

# =============================================================================
# Configurações gerais
# =============================================================================
LARGURA_TELA = 1100
ALTURA_TELA = 650
FPS = 60
ARRAY_INICIAL: Tuple[int, ...] = (7, 4, 2, 1, 8, 3, 6, 5)

ESPACAMENTO_GATOS = 110      # distância horizontal entre os gatos (px)
Y_HORIZONTE = 445            # onde a parede encontra o chão
Y_PES = 485                  # linha onde ficam as patinhas dos gatos
ALTURA_ARCO = 90             # altura do pulo do gato que passa por cima (px)
DURACAO_TROCA = 0.8          # duração da troca em segundos (velocidade 1x)
INTERVALO_AUTO = 0.4         # pausa entre passos no modo automático (s)
VELOCIDADE_MIN = 0.25
VELOCIDADE_MAX = 4.0
RAIO_CORPO_BASE = 34
RAIO_CABECA_BASE = 24

# =============================================================================
# Paleta de cores (sala aconchegante)
# =============================================================================
COR_PAREDE: Cor = (250, 235, 215)
COR_PAREDE_LISTRA: Cor = (244, 224, 200)
COR_RODAPE: Cor = (120, 80, 50)
COR_PISO: Cor = (205, 150, 100)
COR_PISO_JUNTA: Cor = (180, 125, 80)
COR_TAPETE: Cor = (176, 72, 86)
COR_TAPETE_BORDA: Cor = (230, 190, 120)
COR_SOMBRA: Cor = (130, 45, 60)
COR_CEU: Cor = (160, 210, 245)
COR_SOL: Cor = (255, 222, 90)
COR_NUVEM: Cor = (255, 255, 255)
COR_MOLDURA: Cor = (255, 252, 245)

COR_PELO_CLARO: Cor = (255, 214, 150)   # gatos com números pequenos
COR_PELO_ESCURO: Cor = (214, 112, 40)   # gatos com números grandes
COR_CONTORNO: Cor = (90, 50, 25)
COR_BARRIGA: Cor = (255, 243, 225)
COR_ORELHA_INTERNA: Cor = (255, 170, 185)
COR_NARIZ: Cor = (240, 110, 140)
COR_OLHO: Cor = (30, 30, 35)
COR_COLEIRA: Cor = (200, 60, 70)
COR_COLEIRA_ORDENADO: Cor = (60, 170, 90)
COR_SINO: Cor = (250, 205, 60)
COR_DESTAQUE: Cor = (255, 220, 40)

COR_TEXTO: Cor = (35, 30, 30)
COR_TEXTO_CLARO: Cor = (240, 240, 245)
COR_TEXTO_SUAVE: Cor = (150, 156, 180)
COR_PAINEL = (22, 26, 40, 215)          # RGBA -> translúcido
COR_LINHA_ATIVA: Cor = (255, 214, 10)
COR_MENSAGEM = (255, 255, 255, 215)

# Estados visuais possíveis de um gato
ESTADO_NORMAL = "normal"
ESTADO_COMPARANDO = "comparando"
ESTADO_ORDENADO = "ordenado"

# =============================================================================
# Código exibido no painel e mapeamento das linhas
# =============================================================================
CODIGO_BUBBLE_SORT: Tuple[str, ...] = (
    "def bubble_sort(arr):",
    "    n = len(arr)",
    "    for i in range(n):",
    "        for j in range(0, n - i - 1):",
    "            if arr[j] > arr[j + 1]:",
    "                arr[j], arr[j + 1] = arr[j + 1], arr[j]",
    "    return arr",
)
LINHA_N = 1
LINHA_FOR_I = 2
LINHA_FOR_J = 3
LINHA_IF = 4
LINHA_TROCA = 5
LINHA_RETURN = 6

# Tipos de passo gerados pelo algoritmo
ACAO_INICIO = "inicio"
ACAO_LOOP_EXTERNO = "loop_externo"
ACAO_LOOP_INTERNO = "loop_interno"
ACAO_COMPARACAO = "comparacao"
ACAO_TROCA = "troca"
ACAO_FIM = "fim"


# =============================================================================
# Funções auxiliares puras (não dependem de pygame -> fáceis de testar)
# =============================================================================
def limitar(valor: float, minimo: float, maximo: float) -> float:
    """Restringe ``valor`` ao intervalo [minimo, maximo]."""
    return max(minimo, min(maximo, valor))


def suavizar(t: float) -> float:
    """Curva de easing "smoothstep": começa e termina devagar.

    Recebe o progresso linear (0..1) e devolve o progresso suavizado (0..1).
    Valores fora do intervalo são limitados.
    """
    t = limitar(t, 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def interpolar_cor(cor_a: Cor, cor_b: Cor, t: float) -> Cor:
    """Mistura linearmente duas cores RGB (t=0 -> cor_a, t=1 -> cor_b)."""
    t = limitar(t, 0.0, 1.0)
    return tuple(int(round(a + (b - a) * t)) for a, b in zip(cor_a, cor_b))  # type: ignore[return-value]


def calcular_posicoes_x(total: int, largura: float, espacamento: float) -> List[float]:
    """Calcula o X de cada posição do array, centralizando a fileira na tela."""
    if total <= 0:
        return []
    inicio = (largura - espacamento * (total - 1)) / 2
    return [inicio + indice * espacamento for indice in range(total)]


def calcular_fracao(valor: float, minimo: float, maximo: float) -> float:
    """Posição relativa de ``valor`` entre ``minimo`` e ``maximo`` (0..1).

    Usada para que gatos com números maiores sejam maiores e mais escuros.
    Se todos os valores forem iguais, devolve 0.5.
    """
    if maximo == minimo:
        return 0.5
    return limitar((valor - minimo) / (maximo - minimo), 0.0, 1.0)


# =============================================================================
# O algoritmo: Bubble Sort "instrumentado", passo a passo
# =============================================================================
@dataclass(frozen=True)
class Passo:
    """Um instante da execução do Bubble Sort.

    Atributos:
        acao:      tipo do passo (ACAO_*).
        linha:     índice da linha de ``CODIGO_BUBBLE_SORT`` sendo executada.
        i, j:      valores das variáveis de laço (None quando não existem).
        estado:    array APÓS a execução deste passo.
        resultado: resultado da comparação ``arr[j] > arr[j + 1]`` (só em
                   passos de comparação).
    """

    acao: str
    linha: int
    i: Optional[int]
    j: Optional[int]
    estado: Tuple[int, ...]
    resultado: Optional[bool] = None


def gerar_passos_bubble_sort(valores: Sequence[int]) -> Iterator[Passo]:
    """Executa o Bubble Sort em uma CÓPIA de ``valores``, gerando cada passo.

    É exatamente o código mostrado no painel, só que "pausando" (yield)
    em cada linha para que a interface possa animar o que aconteceu.
    """
    arr = list(valores)  # cópia: nunca altera a sequência original
    n = len(arr)
    yield Passo(ACAO_INICIO, LINHA_N, None, None, tuple(arr))

    for i in range(n):
        yield Passo(ACAO_LOOP_EXTERNO, LINHA_FOR_I, i, None, tuple(arr))

        for j in range(0, n - i - 1):
            yield Passo(ACAO_LOOP_INTERNO, LINHA_FOR_J, i, j, tuple(arr))

            precisa_trocar = arr[j] > arr[j + 1]
            yield Passo(ACAO_COMPARACAO, LINHA_IF, i, j, tuple(arr), precisa_trocar)

            if precisa_trocar:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                yield Passo(ACAO_TROCA, LINHA_TROCA, i, j, tuple(arr))

    yield Passo(ACAO_FIM, LINHA_RETURN, None, None, tuple(arr))


# =============================================================================
# Um gato = um elemento do array
# =============================================================================
class GatoElemento:
    """Representa um número do array como um gato animável.

    O gato guarda sua posição atual (x, y) e, quando está trocando de lugar,
    interpola de ``x_origem`` até ``x_destino``. O eixo Y segue uma curva
    senoidal (um arco), permitindo que um gato pule por cima do outro.
    """

    def __init__(
        self,
        numero: int,
        x: float,
        escala: float = 1.0,
        cor_pelo: Cor = COR_PELO_ESCURO,
        y_pes: float = Y_PES,
    ) -> None:
        self.numero = numero
        self.escala = escala
        self.cor_pelo = cor_pelo
        self.cor_contorno = interpolar_cor(cor_pelo, COR_CONTORNO, 0.55)
        self.raio_corpo = RAIO_CORPO_BASE * escala
        self.raio_cabeca = RAIO_CABECA_BASE * escala

        # O gato "pisa" em y_pes; y_base é o centro do corpo quando parado
        self.y_pes = y_pes
        self.y_base = y_pes - self.raio_corpo
        self.x = float(x)
        self.y = self.y_base

        # Estado da animação
        self.x_origem = self.x
        self.x_destino = self.x
        self.altura_arco = 0.0
        self.duracao = 0.0
        self.progresso = 1.0
        self.em_animacao = False

    # ------------------------------------------------------------------ lógica
    @property
    def altura_atual(self) -> float:
        """Quantos pixels o gato está acima da sua posição de repouso."""
        return self.y_base - self.y

    def iniciar_movimento(
        self, x_destino: float, altura_arco: float = 0.0, duracao: float = DURACAO_TROCA
    ) -> None:
        """Começa a mover o gato até ``x_destino``.

        ``altura_arco`` > 0 faz o gato pular em arco; 0 faz ele deslizar.
        ``duracao`` <= 0 move o gato instantaneamente.
        """
        self.x_origem = self.x
        self.x_destino = float(x_destino)
        self.altura_arco = float(altura_arco)
        self.duracao = float(duracao)
        self.progresso = 0.0
        self.em_animacao = True
        if self.duracao <= 0:
            self.concluir_movimento()

    def atualizar(self, dt: float) -> None:
        """Avança a animação em ``dt`` segundos (independe do FPS)."""
        if not self.em_animacao:
            return
        self.progresso = min(1.0, self.progresso + dt / self.duracao)
        t = suavizar(self.progresso)
        # Interpolação do X + arco senoidal no Y (sin(0) = sin(pi) = 0)
        self.x = self.x_origem + (self.x_destino - self.x_origem) * t
        self.y = self.y_base - math.sin(math.pi * t) * self.altura_arco
        if self.progresso >= 1.0:
            self.concluir_movimento()

    def concluir_movimento(self) -> None:
        """Coloca o gato imediatamente no destino e encerra a animação."""
        self.x = self.x_destino
        self.y = self.y_base
        self.progresso = 1.0
        self.em_animacao = False

    # ---------------------------------------------------------------- desenho
    def desenhar(
        self, superficie: pygame.Surface, fonte: pygame.font.Font, estado: str = ESTADO_NORMAL
    ) -> None:
        """Desenha o gato usando apenas primitivas do pygame."""
        x, y = self.x, self.y
        rc, rh = self.raio_corpo, self.raio_cabeca
        hx, hy = x, y - rc * 0.85 - rh * 0.6  # centro da cabeça
        espessura = max(1, round(2 * self.escala))

        # Sombra no tapete: diminui conforme o gato sobe
        fator = limitar(1 - self.altura_atual / 160, 0.35, 1.0)
        largura_sombra = rc * 2.1 * fator
        pygame.draw.ellipse(
            superficie,
            COR_SOMBRA,
            pygame.Rect(x - largura_sombra / 2, self.y_pes - rc * 0.16, largura_sombra, rc * 0.32),
        )

        # Brilho amarelo atrás dos gatos que estão sendo comparados
        if estado == ESTADO_COMPARANDO:
            pygame.draw.circle(superficie, COR_DESTAQUE, (x, y), rc + 7)
            pygame.draw.circle(superficie, COR_DESTAQUE, (hx, hy), rh + 7)

        # Rabo: curva de Bézier quadrática saindo da lateral do corpo
        inicio = (x + rc * 0.75, y + rc * 0.45)
        controle = (x + rc * 1.7, y + rc * 0.3)
        fim = (x + rc * 1.35, y - rc * 0.75)
        pontos_rabo = [
            (
                (1 - t) ** 2 * inicio[0] + 2 * (1 - t) * t * controle[0] + t ** 2 * fim[0],
                (1 - t) ** 2 * inicio[1] + 2 * (1 - t) * t * controle[1] + t ** 2 * fim[1],
            )
            for t in (k / 12 for k in range(13))
        ]
        grossura_rabo = max(4, round(9 * self.escala))
        pygame.draw.lines(superficie, self.cor_contorno, False, pontos_rabo, grossura_rabo + 2)
        pygame.draw.lines(superficie, self.cor_pelo, False, pontos_rabo, grossura_rabo)

        # Corpo
        pygame.draw.circle(superficie, self.cor_pelo, (x, y), rc)
        pygame.draw.circle(superficie, self.cor_contorno, (x, y), rc, espessura)

        # Patinhas
        for deslocamento in (-0.45, 0.45):
            pata = pygame.Rect(0, 0, rc * 0.55, rc * 0.32)
            pata.center = (round(x + rc * deslocamento), round(y + rc * 0.88))
            pygame.draw.ellipse(superficie, self.cor_pelo, pata)
            pygame.draw.ellipse(superficie, self.cor_contorno, pata, espessura)

        # Barriga com o número centralizado
        centro_barriga = (x, y + rc * 0.1)
        pygame.draw.circle(superficie, COR_BARRIGA, centro_barriga, rc * 0.62)
        texto = fonte.render(str(self.numero), True, COR_TEXTO)
        superficie.blit(texto, texto.get_rect(center=(round(centro_barriga[0]), round(centro_barriga[1]))))

        # Orelhas (triângulos) com parte interna rosada
        for lado in (-1, 1):
            orelha = [
                (hx + lado * rh * 0.88, hy - rh * 0.2),
                (hx + lado * rh * 0.72, hy - rh * 1.35),
                (hx + lado * rh * 0.12, hy - rh * 0.82),
            ]
            cx = sum(p[0] for p in orelha) / 3
            cy = sum(p[1] for p in orelha) / 3
            interna = [(cx + (px - cx) * 0.5, cy + (py - cy) * 0.5) for px, py in orelha]
            pygame.draw.polygon(superficie, self.cor_pelo, orelha)
            pygame.draw.polygon(superficie, self.cor_contorno, orelha, espessura)
            pygame.draw.polygon(superficie, COR_ORELHA_INTERNA, interna)

        # Cabeça
        pygame.draw.circle(superficie, self.cor_pelo, (hx, hy), rh)
        pygame.draw.circle(superficie, self.cor_contorno, (hx, hy), rh, espessura)

        # Coleira: vermelha normalmente, verde quando o gato já está no lugar certo
        cor_coleira = COR_COLEIRA_ORDENADO if estado == ESTADO_ORDENADO else COR_COLEIRA
        coleira = pygame.Rect(0, 0, rh * 1.3, max(4, rh * 0.22))
        coleira.center = (round(hx), round(hy + rh * 0.98))
        pygame.draw.rect(superficie, cor_coleira, coleira, border_radius=3)
        pygame.draw.circle(superficie, COR_SINO, (hx, hy + rh * 1.15), max(2, rh * 0.13))

        # Olhos: fechadinhos (felizes) quando ordenado, arregalados ao comparar
        for lado in (-1, 1):
            ox, oy = hx + lado * rh * 0.38, hy - rh * 0.05
            if estado == ESTADO_ORDENADO:
                arco = pygame.Rect(0, 0, rh * 0.36, rh * 0.3)
                arco.center = (round(ox), round(oy + rh * 0.05))
                pygame.draw.arc(superficie, COR_OLHO, arco, 0, math.pi, max(2, espessura))
            else:
                raio_olho = rh * (0.17 if estado == ESTADO_COMPARANDO else 0.13)
                pygame.draw.circle(superficie, COR_OLHO, (ox, oy), raio_olho)
                pygame.draw.circle(superficie, (255, 255, 255), (ox + raio_olho * 0.35, oy - raio_olho * 0.35), raio_olho * 0.35)

        # Nariz, boca e bigodes
        nx, ny = hx, hy + rh * 0.22
        pygame.draw.polygon(
            superficie, COR_NARIZ,
            [(nx - rh * 0.1, ny - rh * 0.06), (nx + rh * 0.1, ny - rh * 0.06), (nx, ny + rh * 0.08)],
        )
        pygame.draw.line(superficie, COR_OLHO, (nx, ny + rh * 0.08), (nx - rh * 0.12, ny + rh * 0.22), 1)
        pygame.draw.line(superficie, COR_OLHO, (nx, ny + rh * 0.08), (nx + rh * 0.12, ny + rh * 0.22), 1)
        for lado in (-1, 1):
            for inclinacao in (-0.08, 0.08):
                pygame.draw.line(
                    superficie, self.cor_contorno,
                    (nx + lado * rh * 0.3, ny + rh * 0.05),
                    (nx + lado * rh * 1.05, ny + rh * (0.05 + inclinacao * 2)),
                    1,
                )


# =============================================================================
# Aplicação: loop do jogo + orquestração do algoritmo
# =============================================================================
class VisualizadorBubbleSort:
    """Gerencia a janela, o loop principal, os eventos e a ordenação animada."""

    def __init__(
        self,
        valores: Sequence[int] = ARRAY_INICIAL,
        largura: int = LARGURA_TELA,
        altura: int = ALTURA_TELA,
    ) -> None:
        if len(valores) == 0:
            raise ValueError("O array precisa ter pelo menos um elemento.")

        pygame.init()
        self.largura = largura
        self.altura = altura
        self.tela = pygame.display.set_mode((largura, altura))
        pygame.display.set_caption("Bubble Sort com Gatos")
        self.relogio = pygame.time.Clock()

        # Fontes: listas com alternativas para funcionar em Windows/Linux/macOS
        sans = "segoeui,arial,helvetica,dejavusans,freesans"
        self.fonte_gato = pygame.font.SysFont("arial,helvetica,dejavusans,freesans", 22, bold=True)
        self.fonte_codigo = pygame.font.SysFont("consolas,menlo,dejavusansmono,couriernew,monospace", 16)
        self.fonte_titulo = pygame.font.SysFont(sans, 18, bold=True)
        self.fonte_texto = pygame.font.SysFont(sans, 16)
        self.fonte_mensagem = pygame.font.SysFont(sans, 19, bold=True)

        self.valores_iniciais: Tuple[int, ...] = tuple(valores)
        self.posicoes_x = calcular_posicoes_x(len(valores), largura, ESPACAMENTO_GATOS)
        self.velocidade = 1.0
        self.rodando = True

        # Geometria dos painéis (calculada uma vez a partir das fontes)
        self.altura_linha_codigo = 24
        largura_numero = self.fonte_codigo.size("00  ")[0]
        largura_codigo = max(self.fonte_codigo.size(linha)[0] for linha in CODIGO_BUBBLE_SORT)
        self.rect_painel_codigo = pygame.Rect(
            20, 20, largura_numero + largura_codigo + 36,
            46 + self.altura_linha_codigo * len(CODIGO_BUBBLE_SORT) + 12,
        )
        self.rect_painel_info = pygame.Rect(0, 20, 300, self.rect_painel_codigo.height)
        self.rect_painel_info.right = largura - 20

        self.fundo = self._criar_fundo()
        self.reiniciar()

    # =================================================================== estado
    def reiniciar(self) -> None:
        """Volta tudo ao estado inicial (gatos embaralhados, sem passos)."""
        menor, maior = min(self.valores_iniciais), max(self.valores_iniciais)
        self.gatos: List[GatoElemento] = []
        for indice, numero in enumerate(self.valores_iniciais):
            fracao = calcular_fracao(numero, menor, maior)
            self.gatos.append(
                GatoElemento(
                    numero,
                    self.posicoes_x[indice],
                    escala=0.8 + 0.35 * fracao,  # números maiores -> gatos maiores
                    cor_pelo=interpolar_cor(COR_PELO_CLARO, COR_PELO_ESCURO, fracao),
                )
            )

        self._passos = gerar_passos_bubble_sort(self.valores_iniciais)
        self.passo_atual: Optional[Passo] = None
        self.linha_atual: Optional[int] = None
        self.destacados: Tuple[int, ...] = ()
        self.ordenados: set = set()
        self.comparacoes = 0
        self.trocas = 0
        self.concluido = False
        self.modo_automatico = False
        self.tempo_acumulado = 0.0
        self.mensagem = "Aperte ESPAÇO para avançar passo a passo ou ENTER para o modo automático."

    @property
    def numeros(self) -> List[int]:
        """Números dos gatos na ordem em que estão no array."""
        return [gato.numero for gato in self.gatos]

    def animacoes_em_andamento(self) -> bool:
        return any(gato.em_animacao for gato in self.gatos)

    def concluir_animacoes(self) -> None:
        for gato in self.gatos:
            gato.concluir_movimento()

    def alterar_velocidade(self, fator: float) -> None:
        """Multiplica a velocidade por ``fator``, respeitando os limites."""
        self.velocidade = limitar(self.velocidade * fator, VELOCIDADE_MIN, VELOCIDADE_MAX)

    # ================================================================ algoritmo
    def avancar_passo(self) -> bool:
        """Executa o próximo passo do algoritmo. Retorna False se já acabou.

        Se uma troca ainda estiver sendo animada, ela é finalizada na hora,
        assim o usuário nunca "perde" um aperto de tecla.
        """
        if self.concluido:
            return False
        self.concluir_animacoes()
        try:
            passo = next(self._passos)
        except StopIteration:  # salvaguarda: o passo FIM já marca concluido
            self.concluido = True
            self.modo_automatico = False
            return False
        self.aplicar_passo(passo)
        return True

    def aplicar_passo(self, passo: Passo) -> None:
        """Atualiza a interface de acordo com o passo recebido."""
        self.passo_atual = passo
        self.linha_atual = passo.linha
        n = len(self.gatos)
        j = passo.j

        if passo.acao == ACAO_INICIO:
            self.destacados = ()
            self.mensagem = f"n = len(arr) = {n}. Vamos ordenar os gatos do menor para o maior!"

        elif passo.acao == ACAO_LOOP_EXTERNO:
            self.destacados = ()
            # Depois de i passadas, as últimas i posições já estão definitivas
            self.ordenados = set(range(n - passo.i, n))
            ultima = n - passo.i - 1
            if ultima > 0:
                self.mensagem = (
                    f"Passada i = {passo.i}: o maior gato restante vai 'borbulhar' até a posição {ultima}."
                )
            else:
                self.mensagem = f"Passada i = {passo.i}: não sobrou nenhum par para comparar."

        elif passo.acao == ACAO_LOOP_INTERNO:
            self.destacados = (j, j + 1)
            self.mensagem = f"j = {j}: olhando os gatos das posições {j} e {j + 1}."

        elif passo.acao == ACAO_COMPARACAO:
            self.destacados = (j, j + 1)
            self.comparacoes += 1
            a, b = passo.estado[j], passo.estado[j + 1]
            if passo.resultado:
                self.mensagem = f"{a} > {b}? Sim! Eles precisam trocar de lugar."
            else:
                self.mensagem = f"{a} > {b}? Não. Os dois ficam onde estão."

        elif passo.acao == ACAO_TROCA:
            self.destacados = (j, j + 1)
            self.trocas += 1
            self._animar_troca(j)
            maior, menor = passo.estado[j + 1], passo.estado[j]
            self.mensagem = f"Trocando: o gato {maior} pula por cima do gato {menor}."

        elif passo.acao == ACAO_FIM:
            self.destacados = ()
            self.ordenados = set(range(n))
            self.concluido = True
            self.modo_automatico = False
            self.mensagem = f"Pronto! arr = {list(passo.estado)} está ordenado. (R reinicia)"

    def _animar_troca(self, j: int) -> None:
        """Troca os gatos j e j+1: o maior pula em arco, o menor desliza."""
        gato_esquerda, gato_direita = self.gatos[j], self.gatos[j + 1]
        duracao = DURACAO_TROCA / self.velocidade
        gato_esquerda.iniciar_movimento(self.posicoes_x[j + 1], ALTURA_ARCO, duracao)
        gato_direita.iniciar_movimento(self.posicoes_x[j], 0.0, duracao)
        # A lista sempre reflete a ordem lógica do array
        self.gatos[j], self.gatos[j + 1] = gato_direita, gato_esquerda

    # ================================================================== eventos
    def processar_evento(self, evento: pygame.event.Event) -> None:
        """Trata um evento do pygame (teclado / fechar janela)."""
        if evento.type == pygame.QUIT:
            self.rodando = False
            return
        if evento.type != pygame.KEYDOWN:
            return

        tecla = evento.key
        if tecla == pygame.K_ESCAPE:
            self.rodando = False
        elif tecla == pygame.K_SPACE:
            # Modo didático: pausa o automático e anda exatamente um passo
            self.modo_automatico = False
            self.avancar_passo()
        elif tecla in (pygame.K_RETURN, pygame.K_KP_ENTER):
            if self.concluido:
                self.reiniciar()
                self.modo_automatico = True
            else:
                self.modo_automatico = not self.modo_automatico
            self.tempo_acumulado = 0.0
        elif tecla == pygame.K_r:
            self.reiniciar()
        elif tecla in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS, pygame.K_UP):
            self.alterar_velocidade(2.0)
        elif tecla in (pygame.K_MINUS, pygame.K_KP_MINUS, pygame.K_DOWN):
            self.alterar_velocidade(0.5)

    def atualizar(self, dt: float) -> None:
        """Avança animações e, no modo automático, o algoritmo."""
        for gato in self.gatos:
            gato.atualizar(dt)

        if self.modo_automatico and not self.animacoes_em_andamento():
            self.tempo_acumulado += dt
            if self.tempo_acumulado >= INTERVALO_AUTO / self.velocidade:
                self.tempo_acumulado = 0.0
                self.avancar_passo()

    # ================================================================== desenho
    def estado_do_gato(self, indice: int) -> str:
        if indice in self.ordenados:
            return ESTADO_ORDENADO
        if indice in self.destacados:
            return ESTADO_COMPARANDO
        return ESTADO_NORMAL

    def _criar_fundo(self) -> pygame.Surface:
        """Desenha o cenário estático (sala com janela, piso e tapete) uma vez só."""
        fundo = pygame.Surface((self.largura, self.altura))
        fundo.fill(COR_PAREDE)

        # Papel de parede listrado
        for x in range(0, self.largura, 40):
            pygame.draw.rect(fundo, COR_PAREDE_LISTRA, (x, 0, 20, Y_HORIZONTE))

        # Janela entre os dois painéis (só se couber)
        espaco_esq = self.rect_painel_codigo.right
        espaco_dir = self.rect_painel_info.left
        if espaco_dir - espaco_esq >= 170:
            janela = pygame.Rect(0, 45, 130, 150)
            janela.centerx = (espaco_esq + espaco_dir) // 2
            pygame.draw.rect(fundo, COR_CEU, janela)
            pygame.draw.circle(fundo, COR_SOL, (janela.right - 32, janela.top + 34), 18)
            for dx, dy, r in ((-22, 0, 12), (-8, -6, 15), (8, 0, 12)):
                pygame.draw.circle(fundo, COR_NUVEM, (janela.left + 50 + dx, janela.top + 95 + dy), r)
            pygame.draw.rect(fundo, COR_MOLDURA, janela, 7)
            pygame.draw.line(fundo, COR_MOLDURA, (janela.centerx, janela.top), (janela.centerx, janela.bottom), 5)
            pygame.draw.line(fundo, COR_MOLDURA, (janela.left, janela.centery), (janela.right, janela.centery), 5)
            pygame.draw.rect(fundo, COR_RODAPE, (janela.left - 10, janela.bottom, janela.width + 20, 8), border_radius=3)

        # Piso de tábuas
        pygame.draw.rect(fundo, COR_PISO, (0, Y_HORIZONTE, self.largura, self.altura - Y_HORIZONTE))
        for fileira, y in enumerate(range(Y_HORIZONTE, self.altura, 28)):
            pygame.draw.line(fundo, COR_PISO_JUNTA, (0, y), (self.largura, y), 2)
            deslocamento = 0 if fileira % 2 == 0 else 90
            for x in range(deslocamento, self.largura, 180):
                pygame.draw.line(fundo, COR_PISO_JUNTA, (x, y), (x, y + 28), 2)
        pygame.draw.rect(fundo, COR_RODAPE, (0, Y_HORIZONTE - 10, self.largura, 10))

        # Tapete onde os gatos ficam
        largura_tapete = ESPACAMENTO_GATOS * (len(self.valores_iniciais) - 1) + 190
        tapete = pygame.Rect(0, 0, largura_tapete, 74)
        tapete.center = (self.largura // 2, Y_PES)
        pygame.draw.ellipse(fundo, COR_TAPETE_BORDA, tapete.inflate(16, 10))
        pygame.draw.ellipse(fundo, COR_TAPETE, tapete)
        return fundo

    def _desenhar_painel(self, rect: pygame.Rect, titulo: str) -> pygame.Surface:
        """Cria uma superfície translúcida com cantos arredondados e título."""
        painel = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(painel, COR_PAINEL, painel.get_rect(), border_radius=14)
        for k, cor in enumerate(((255, 95, 86), (255, 189, 46), (39, 201, 63))):
            pygame.draw.circle(painel, cor, (22 + k * 18, 22), 6)
        texto = self.fonte_titulo.render(titulo, True, COR_TEXTO_CLARO)
        painel.blit(texto, (82, 22 - texto.get_height() // 2))
        return painel

    def desenhar_painel_codigo(self) -> None:
        painel = self._desenhar_painel(self.rect_painel_codigo, "bubble_sort.py")
        largura_numero = self.fonte_codigo.size("00  ")[0]
        y = 46
        for indice, linha in enumerate(CODIGO_BUBBLE_SORT):
            ativa = indice == self.linha_atual
            if ativa:  # fundo amarelo + texto preto na linha em execução
                faixa = pygame.Rect(10, y, self.rect_painel_codigo.width - 20, self.altura_linha_codigo)
                pygame.draw.rect(painel, COR_LINHA_ATIVA, faixa, border_radius=5)
            cor_numero = COR_TEXTO if ativa else COR_TEXTO_SUAVE
            cor_codigo = COR_TEXTO if ativa else COR_TEXTO_CLARO
            numero = self.fonte_codigo.render(f"{indice + 1:>2}", True, cor_numero)
            codigo = self.fonte_codigo.render(linha, True, cor_codigo)
            centro_y = y + self.altura_linha_codigo // 2
            painel.blit(numero, (18, centro_y - numero.get_height() // 2))
            painel.blit(codigo, (18 + largura_numero, centro_y - codigo.get_height() // 2))
            y += self.altura_linha_codigo
        self.tela.blit(painel, self.rect_painel_codigo.topleft)

    def desenhar_painel_info(self) -> None:
        painel = self._desenhar_painel(self.rect_painel_info, "Estado")
        passo = self.passo_atual
        i = "-" if passo is None or passo.i is None else str(passo.i)
        j = "-" if passo is None or passo.j is None else str(passo.j)
        modo = "Automático" if self.modo_automatico else "Passo a passo"
        if self.concluido:
            modo = "Concluído"
        linhas = [
            (f"i = {i}    j = {j}    n = {len(self.gatos)}", COR_LINHA_ATIVA),
            (f"arr = {self.numeros}", COR_TEXTO_CLARO),
            (f"Comparações: {self.comparacoes}", COR_TEXTO_CLARO),
            (f"Trocas: {self.trocas}", COR_TEXTO_CLARO),
            (f"Modo: {modo}", (120, 220, 140) if self.modo_automatico else COR_TEXTO_CLARO),
            (f"Velocidade: {self.velocidade:g}x", COR_TEXTO_CLARO),
        ]
        y = 48
        for texto, cor in linhas:
            superficie = self.fonte_texto.render(texto, True, cor)
            painel.blit(superficie, (20, y))
            y += 27
        self.tela.blit(painel, self.rect_painel_info.topleft)

    def desenhar_mensagem(self) -> None:
        """Balão com a explicação do passo atual + barra de controles."""
        texto = self.fonte_mensagem.render(self.mensagem, True, COR_TEXTO)
        caixa = texto.get_rect().inflate(36, 18)
        caixa.center = (self.largura // 2, Y_PES + 72)
        balao = pygame.Surface(caixa.size, pygame.SRCALPHA)
        pygame.draw.rect(balao, COR_MENSAGEM, balao.get_rect(), border_radius=12)
        self.tela.blit(balao, caixa.topleft)
        self.tela.blit(texto, texto.get_rect(center=caixa.center))

        ajuda = "ESPAÇO: passo   |   ENTER: automático   |   R: reiniciar   |   + / - : velocidade   |   ESC: sair"
        texto_ajuda = self.fonte_texto.render(ajuda, True, COR_TEXTO_CLARO)
        faixa = pygame.Surface((self.largura, 34), pygame.SRCALPHA)
        faixa.fill((22, 26, 40, 190))
        self.tela.blit(faixa, (0, self.altura - 34))
        self.tela.blit(texto_ajuda, texto_ajuda.get_rect(center=(self.largura // 2, self.altura - 17)))

    def desenhar(self) -> None:
        """Desenha um quadro completo."""
        self.tela.blit(self.fundo, (0, 0))

        # Gatos mais altos (pulando) são desenhados por último -> ficam por cima
        ordem = sorted(range(len(self.gatos)), key=lambda k: self.gatos[k].altura_atual)
        for indice in ordem:
            self.gatos[indice].desenhar(self.tela, self.fonte_gato, self.estado_do_gato(indice))

        self.desenhar_painel_codigo()
        self.desenhar_painel_info()
        self.desenhar_mensagem()

    # ============================================================= loop principal
    def executar(self) -> None:
        """Loop principal: eventos -> atualização -> desenho."""
        while self.rodando:
            dt = self.relogio.tick(FPS) / 1000.0  # segundos desde o último quadro
            for evento in pygame.event.get():
                self.processar_evento(evento)
            self.atualizar(dt)
            self.desenhar()
            pygame.display.flip()
        pygame.quit()


def main() -> None:
    VisualizadorBubbleSort().executar()


if __name__ == "__main__":
    main()
