import pygame
import sys
import math

# Inicialização do Pygame
pygame.init()
pygame.font.init()

# Constantes da tela
LARGURA = 1000
ALTURA = 600
FPS = 60

# Cores
COR_FUNDO = (135, 206, 235)  # Azul céu (cenário dia)
COR_CHAO = (34, 139, 34)     # Verde grama
COR_GATO = (255, 165, 0)     # Laranja
COR_GATO_CONTORNO = (200, 100, 0)
COR_TEXTO = (0, 0, 0)
COR_PAINEL = (0, 0, 0, 150)  # Preto translúcido
COR_DESTAQUE_CODIGO = (255, 255, 0) # Amarelo

FONTE_GATO = pygame.font.SysFont('Arial', 24, bold=True)
FONTE_CODIGO = pygame.font.SysFont('Consolas', 18)

class GatoElemento:
    def __init__(self, numero, index, total_elementos):
        self.numero = numero
        self.raio_corpo = 35
        self.raio_cabeca = 25
        
        # Posição alvo (para onde o gato deve ir)
        self.x_alvo = self._calcular_x(index, total_elementos)
        self.y_alvo = ALTURA - 150
        
        # Posição atual
        self.x = self.x_alvo
        self.y = self.y_alvo
        
        # Variáveis de animação de troca
        self.em_animacao = False
        self.progresso_anim = 0.0
        self.origem_x = 0
        self.origem_y = 0
        self.curva_altura = 0
        self.velocidade_anim = 0.03

    def _calcular_x(self, index, total_elementos):
        espacamento = 100
        largura_total = espacamento * (total_elementos - 1)
        start_x = (LARGURA - largura_total) // 2
        return start_x + index * espacamento

    def iniciar_troca(self, novo_index, total_elementos, arco_para_cima=True):
        self.origem_x = self.x
        self.origem_y = self.y
        self.x_alvo = self._calcular_x(novo_index, total_elementos)
        self.em_animacao = True
        self.progresso_anim = 0.0
        # A altura do arco depende da distância e da direção
        distancia = abs(self.x_alvo - self.origem_x)
        direcao_arco = -1 if arco_para_cima else 1
        self.curva_altura = (distancia / 2) * direcao_arco

    def atualizar(self):
        if self.em_animacao:
            self.progresso_anim += self.velocidade_anim
            if self.progresso_anim >= 1.0:
                self.progresso_anim = 1.0
                self.em_animacao = False
                self.x = self.x_alvo
                self.y = self.y_alvo
            else:
                # Interpolação linear para o eixo X
                self.x = self.origem_x + (self.x_alvo - self.origem_x) * self.progresso_anim
                # Arco parabólico para o Y usando seno (0 a PI)
                self.y = self.origem_y + math.sin(self.progresso_anim * math.pi) * self.curva_altura

    def desenhar(self, surface):
        # Desenhar orelhas (triângulos)
        x_cabeca = self.x
        y_cabeca = self.y - self.raio_corpo - 10
        
        # Orelha esquerda
        pontos_orelha_esq = [
            (x_cabeca - 15, y_cabeca - 10),
            (x_cabeca - 25, y_cabeca - 35),
            (x_cabeca - 5, y_cabeca - 20)
        ]
        pygame.draw.polygon(surface, COR_GATO, pontos_orelha_esq)
        pygame.draw.polygon(surface, COR_GATO_CONTORNO, pontos_orelha_esq, 2)
        
        # Orelha direita
        pontos_orelha_dir = [
            (x_cabeca + 15, y_cabeca - 10),
            (x_cabeca + 25, y_cabeca - 35),
            (x_cabeca + 5, y_cabeca - 20)
        ]
        pygame.draw.polygon(surface, COR_GATO, pontos_orelha_dir)
        pygame.draw.polygon(surface, COR_GATO_CONTORNO, pontos_orelha_dir, 2)

        # Desenhar cabeça
        pygame.draw.circle(surface, COR_GATO, (int(x_cabeca), int(y_cabeca)), self.raio_cabeca)
        pygame.draw.circle(surface, COR_GATO_CONTORNO, (int(x_cabeca), int(y_cabeca)), self.raio_cabeca, 2)
        
        # Olhos
        pygame.draw.circle(surface, (255, 255, 255), (int(x_cabeca - 10), int(y_cabeca - 5)), 6)
        pygame.draw.circle(surface, (255, 255, 255), (int(x_cabeca + 10), int(y_cabeca - 5)), 6)
        pygame.draw.circle(surface, (0, 0, 0), (int(x_cabeca - 10), int(y_cabeca - 5)), 3)
        pygame.draw.circle(surface, (0, 0, 0), (int(x_cabeca + 10), int(y_cabeca - 5)), 3)
        
        # Nariz e boca
        pygame.draw.circle(surface, (255, 105, 180), (int(x_cabeca), int(y_cabeca + 5)), 3)
        pygame.draw.line(surface, (0, 0, 0), (x_cabeca, y_cabeca + 8), (x_cabeca - 5, y_cabeca + 12), 1)
        pygame.draw.line(surface, (0, 0, 0), (x_cabeca, y_cabeca + 8), (x_cabeca + 5, y_cabeca + 12), 1)

        # Desenhar corpo
        pygame.draw.circle(surface, COR_GATO, (int(self.x), int(self.y)), self.raio_corpo)
        pygame.draw.circle(surface, COR_GATO_CONTORNO, (int(self.x), int(self.y)), self.raio_corpo, 2)
        
        # Desenhar número na barriga
        texto = FONTE_GATO.render(str(self.numero), True, COR_TEXTO)
        retangulo_texto = texto.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(texto, retangulo_texto)


class VisualizadorBubbleSort:
    def __init__(self):
        self.tela = pygame.display.set_mode((LARGURA, ALTURA))
        pygame.display.set_caption("Bubble Sort com Gatos!")
        self.relogio = pygame.time.Clock()
        
        # Array inicial conforme especificado
        self.array_numeros = [7, 4, 2, 1, 8, 3, 6, 5]
        self.n = len(self.array_numeros)
        
        # Criar as instâncias dos gatos
        self.gatos = [GatoElemento(num, i, self.n) for i, num in enumerate(self.array_numeros)]
        
        # Variáveis de controle de estado do Bubble Sort
        self.i = 0
        self.j = 0
        self.estado_algoritmo = "INICIO_I" # Estados: INICIO_I, INICIO_J, COMPARANDO, TROCANDO, AVANCAR_J, FIM
        
        # Controle de execução (manual ou automático)
        self.modo_automatico = False
        self.linha_codigo_atual = 2
        
        # Código fonte para exibição no painel
        self.codigo = [
            "def bubble_sort(arr):",
            "    n = len(arr)",
            "    for i in range(n):",
            "        for j in range(0, n - i - 1):",
            "            if arr[j] > arr[j + 1]:",
            "                arr[j], arr[j + 1] = arr[j + 1], arr[j]"
        ]

    def desenhar_painel_codigo(self):
        # Criar uma superfície com suporte a alpha (transparência)
        painel = pygame.Surface((450, 200), pygame.SRCALPHA)
        painel.fill(COR_PAINEL)
        
        y_offset = 15
        for idx, linha in enumerate(self.codigo):
            if idx == self.linha_codigo_atual:
                # Fundo amarelo de destaque para a linha em execução
                rect_destaque = pygame.Rect(10, y_offset, 430, 25)
                pygame.draw.rect(painel, COR_DESTAQUE_CODIGO, rect_destaque)
                texto = FONTE_CODIGO.render(linha, True, (0, 0, 0))
            else:
                texto = FONTE_CODIGO.render(linha, True, (255, 255, 255))
                
            painel.blit(texto, (15, y_offset + 3))
            y_offset += 25
            
        self.tela.blit(painel, (20, 20))

    def desenhar_cenario(self):
        # Preenche o fundo (céu)
        self.tela.fill(COR_FUNDO)
        # Desenha o chão (grama)
        pygame.draw.rect(self.tela, COR_CHAO, (0, ALTURA - 100, LARGURA, 100))
        
        # Textos de instrução
        instrucoes1 = FONTE_CODIGO.render("ESPAÇO: Avançar passo-a-passo", True, COR_TEXTO)
        instrucoes2 = FONTE_CODIGO.render("ENTER: Iniciar/Pausar automático", True, COR_TEXTO)
        self.tela.blit(instrucoes1, (LARGURA - 380, 20))
        self.tela.blit(instrucoes2, (LARGURA - 380, 50))
        
        status_auto = "LIGADO" if self.modo_automatico else "DESLIGADO"
        cor_status = (0, 150, 0) if self.modo_automatico else (200, 0, 0)
        texto_status = FONTE_CODIGO.render(f"Modo Auto: {status_auto}", True, cor_status)
        self.tela.blit(texto_status, (LARGURA - 380, 80))

    def animacoes_em_andamento(self):
        return any(gato.em_animacao for gato in self.gatos)

    def executar_passo_algoritmo(self):
        if self.estado_algoritmo == "FIM":
            return

        # Aguarda a animação visual terminar antes de avançar a lógica
        if self.animacoes_em_andamento():
            return 

        if self.estado_algoritmo == "INICIO_I":
            if self.i < self.n:
                self.linha_codigo_atual = 2
                self.estado_algoritmo = "INICIO_J"
            else:
                self.estado_algoritmo = "FIM"
                self.linha_codigo_atual = -1 # Finalizou, não destaca nada
                
        elif self.estado_algoritmo == "INICIO_J":
            if self.j < self.n - self.i - 1:
                self.linha_codigo_atual = 3
                self.estado_algoritmo = "COMPARANDO"
            else:
                # Fim do loop interno (j), avança o externo (i) e reseta o interno
                self.i += 1
                self.j = 0
                self.estado_algoritmo = "INICIO_I"
                
        elif self.estado_algoritmo == "COMPARANDO":
            self.linha_codigo_atual = 4
            if self.gatos[self.j].numero > self.gatos[self.j + 1].numero:
                self.estado_algoritmo = "TROCANDO"
            else:
                self.estado_algoritmo = "AVANCAR_J"
                
        elif self.estado_algoritmo == "TROCANDO":
            self.linha_codigo_atual = 5
            
            # Iniciar as animações de troca
            gato_esq = self.gatos[self.j]
            gato_dir = self.gatos[self.j + 1]
            
            # Gato da esquerda faz um arco por cima, o da direita arco por baixo
            gato_esq.iniciar_troca(self.j + 1, self.n, arco_para_cima=True)
            gato_dir.iniciar_troca(self.j, self.n, arco_para_cima=False)
            
            # Trocar na lista
            self.gatos[self.j], self.gatos[self.j + 1] = self.gatos[self.j + 1], self.gatos[self.j]
            
            self.estado_algoritmo = "AVANCAR_J"
            
        elif self.estado_algoritmo == "AVANCAR_J":
            if not self.animacoes_em_andamento():
                self.j += 1
                self.estado_algoritmo = "INICIO_J"

    def run(self):
        rodando = True
        
        # Timer para o modo automático
        ultimo_tempo = pygame.time.get_ticks()
        intervalo_auto = 600 # Milissegundos entre os passos (se não houver animação rolado)
        
        while rodando:
            tempo_atual = pygame.time.get_ticks()
            
            # Tratar eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    rodando = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        # Executa um passo manual
                        if not self.modo_automatico:
                            self.executar_passo_algoritmo()
                    elif event.key == pygame.K_RETURN:
                        # Alternar modo automático
                        self.modo_automatico = not self.modo_automatico

            # Lógica do modo automático
            if self.modo_automatico:
                if not self.animacoes_em_andamento():
                    if tempo_atual - ultimo_tempo > intervalo_auto:
                        self.executar_passo_algoritmo()
                        ultimo_tempo = tempo_atual
                else:
                    ultimo_tempo = tempo_atual # Segura o timer enquanto a animação ocorre

            # Atualizar estado visual (animações)
            for gato in self.gatos:
                gato.atualizar()

            # Processo de desenho
            self.desenhar_cenario()
            
            # Desenhar os gatos que não estão em animação primeiro (ficam no fundo)
            for gato in self.gatos:
                if not gato.em_animacao:
                    gato.desenhar(self.tela)
            
            # Desenhar os gatos em animação por cima
            for gato in self.gatos:
                if gato.em_animacao:
                    gato.desenhar(self.tela)
                    
            self.desenhar_painel_codigo()

            # Atualizar tela
            pygame.display.flip()
            self.relogio.tick(FPS)
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    visualizador = VisualizadorBubbleSort()
    visualizador.run()
