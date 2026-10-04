"""
Testes unitários do visualizador Bubble Sort com Gatos.

Rodam sem abrir janela: o SDL é configurado com drivers "dummy".
Execute a partir da raiz do projeto com:

    python -m unittest discover -s tests -v
ou
    python -m pytest
"""

import os
import sys
import unittest
from itertools import combinations
from pathlib import Path

# Precisa ser definido ANTES de importar o pygame -> nenhuma janela/áudio real
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pygame  # noqa: E402

import bubble_sort_gatos as app  # noqa: E402


def contar_inversoes(valores):
    """Número de pares fora de ordem = número de trocas do Bubble Sort."""
    return sum(1 for a, b in combinations(valores, 2) if a > b)


def tecla(codigo):
    return pygame.event.Event(pygame.KEYDOWN, key=codigo)


# =============================================================================
# Funções auxiliares puras
# =============================================================================
class TestLimitar(unittest.TestCase):
    def test_valor_dentro_do_intervalo_nao_muda(self):
        self.assertEqual(app.limitar(5, 0, 10), 5)

    def test_valor_abaixo_vira_minimo(self):
        self.assertEqual(app.limitar(-3, 0, 10), 0)

    def test_valor_acima_vira_maximo(self):
        self.assertEqual(app.limitar(42, 0, 10), 10)


class TestSuavizar(unittest.TestCase):
    def test_extremos_e_meio(self):
        self.assertEqual(app.suavizar(0.0), 0.0)
        self.assertEqual(app.suavizar(1.0), 1.0)
        self.assertAlmostEqual(app.suavizar(0.5), 0.5)

    def test_valores_fora_do_intervalo_sao_limitados(self):
        self.assertEqual(app.suavizar(-1.0), 0.0)
        self.assertEqual(app.suavizar(2.0), 1.0)

    def test_e_monotonica_crescente(self):
        amostras = [app.suavizar(k / 100) for k in range(101)]
        self.assertEqual(amostras, sorted(amostras))

    def test_comeca_e_termina_devagar(self):
        # Easing: o primeiro 10% do tempo percorre menos de 10% do caminho
        self.assertLess(app.suavizar(0.1), 0.1)
        self.assertGreater(app.suavizar(0.9), 0.9)


class TestInterpolarCor(unittest.TestCase):
    def test_extremos(self):
        self.assertEqual(app.interpolar_cor((0, 0, 0), (200, 100, 50), 0), (0, 0, 0))
        self.assertEqual(app.interpolar_cor((0, 0, 0), (200, 100, 50), 1), (200, 100, 50))

    def test_meio(self):
        self.assertEqual(app.interpolar_cor((0, 0, 0), (200, 100, 50), 0.5), (100, 50, 25))

    def test_t_fora_do_intervalo_e_limitado(self):
        self.assertEqual(app.interpolar_cor((10, 10, 10), (20, 20, 20), 5), (20, 20, 20))
        self.assertEqual(app.interpolar_cor((10, 10, 10), (20, 20, 20), -5), (10, 10, 10))

    def test_resultado_tem_inteiros(self):
        cor = app.interpolar_cor((0, 0, 0), (255, 255, 255), 1 / 3)
        self.assertTrue(all(isinstance(c, int) for c in cor))


class TestCalcularPosicoesX(unittest.TestCase):
    def test_fileira_centralizada_e_espacada(self):
        posicoes = app.calcular_posicoes_x(8, 1100, 110)
        self.assertEqual(len(posicoes), 8)
        self.assertAlmostEqual(sum(posicoes) / len(posicoes), 550)
        for a, b in zip(posicoes, posicoes[1:]):
            self.assertAlmostEqual(b - a, 110)

    def test_um_elemento_fica_no_centro(self):
        self.assertEqual(app.calcular_posicoes_x(1, 800, 100), [400])

    def test_zero_ou_negativo_retorna_vazio(self):
        self.assertEqual(app.calcular_posicoes_x(0, 800, 100), [])
        self.assertEqual(app.calcular_posicoes_x(-2, 800, 100), [])


class TestCalcularFracao(unittest.TestCase):
    def test_minimo_meio_maximo(self):
        self.assertEqual(app.calcular_fracao(1, 1, 9), 0.0)
        self.assertEqual(app.calcular_fracao(5, 1, 9), 0.5)
        self.assertEqual(app.calcular_fracao(9, 1, 9), 1.0)

    def test_valores_iguais_nao_dividem_por_zero(self):
        self.assertEqual(app.calcular_fracao(3, 3, 3), 0.5)


# =============================================================================
# Gerador de passos do Bubble Sort
# =============================================================================
class TestGerarPassosBubbleSort(unittest.TestCase):
    CASOS = [
        list(app.ARRAY_INICIAL),
        [],
        [42],
        [1, 2, 3, 4, 5],
        [5, 4, 3, 2, 1],
        [3, 1, 3, 2, 1],
        [-5, 10, 0, -1, 7],
    ]

    def passos(self, valores):
        return list(app.gerar_passos_bubble_sort(valores))

    def test_estado_final_e_ordenado(self):
        for valores in self.CASOS:
            with self.subTest(valores=valores):
                self.assertEqual(list(self.passos(valores)[-1].estado), sorted(valores))

    def test_nao_altera_a_lista_original(self):
        valores = [3, 2, 1]
        self.passos(valores)
        self.assertEqual(valores, [3, 2, 1])

    def test_primeiro_e_ultimo_passo(self):
        passos = self.passos(app.ARRAY_INICIAL)
        self.assertEqual((passos[0].acao, passos[0].linha), (app.ACAO_INICIO, app.LINHA_N))
        self.assertEqual((passos[-1].acao, passos[-1].linha), (app.ACAO_FIM, app.LINHA_RETURN))

    def test_quantidade_de_comparacoes(self):
        for valores in self.CASOS:
            n = len(valores)
            with self.subTest(valores=valores):
                comparacoes = [p for p in self.passos(valores) if p.acao == app.ACAO_COMPARACAO]
                self.assertEqual(len(comparacoes), n * (n - 1) // 2)

    def test_quantidade_de_trocas_igual_ao_numero_de_inversoes(self):
        for valores in self.CASOS:
            with self.subTest(valores=valores):
                trocas = [p for p in self.passos(valores) if p.acao == app.ACAO_TROCA]
                self.assertEqual(len(trocas), contar_inversoes(valores))

    def test_array_do_enunciado_tem_14_trocas_e_80_passos(self):
        passos = self.passos(app.ARRAY_INICIAL)
        self.assertEqual(sum(p.acao == app.ACAO_TROCA for p in passos), 14)
        self.assertEqual(len(passos), 80)  # 1 início + 8 passadas + 28*2 + 14 trocas + 1 fim

    def test_comparacao_reflete_o_estado_e_troca_so_quando_necessario(self):
        passos = self.passos(app.ARRAY_INICIAL)
        for anterior, atual in zip(passos, passos[1:]):
            if anterior.acao == app.ACAO_COMPARACAO:
                j = anterior.j
                esperado = anterior.estado[j] > anterior.estado[j + 1]
                self.assertEqual(anterior.resultado, esperado)
                # Só existe passo de troca logo após uma comparação verdadeira
                self.assertEqual(atual.acao == app.ACAO_TROCA, esperado)

    def test_troca_inverte_exatamente_as_posicoes_j_e_j_mais_1(self):
        passos = self.passos(app.ARRAY_INICIAL)
        for anterior, atual in zip(passos, passos[1:]):
            if atual.acao == app.ACAO_TROCA:
                esperado = list(anterior.estado)
                j = atual.j
                esperado[j], esperado[j + 1] = esperado[j + 1], esperado[j]
                self.assertEqual(list(atual.estado), esperado)

    def test_linhas_apontam_para_o_codigo_certo(self):
        trechos = {
            app.ACAO_INICIO: "n = len(arr)",
            app.ACAO_LOOP_EXTERNO: "for i in range(n)",
            app.ACAO_LOOP_INTERNO: "for j in range(0, n - i - 1)",
            app.ACAO_COMPARACAO: "if arr[j] > arr[j + 1]",
            app.ACAO_TROCA: "arr[j], arr[j + 1] = arr[j + 1], arr[j]",
            app.ACAO_FIM: "return arr",
        }
        for passo in self.passos(app.ARRAY_INICIAL):
            self.assertIn(trechos[passo.acao], app.CODIGO_BUBBLE_SORT[passo.linha])

    def test_indices_respeitam_os_limites_dos_lacos(self):
        n = len(app.ARRAY_INICIAL)
        for passo in self.passos(app.ARRAY_INICIAL):
            if passo.j is not None:
                self.assertLessEqual(0, passo.j)
                self.assertLess(passo.j, n - passo.i - 1)

    def test_maior_elemento_borbulha_ao_final_de_cada_passada(self):
        passos = self.passos(app.ARRAY_INICIAL)
        n = len(app.ARRAY_INICIAL)
        for passo in passos:
            if passo.acao == app.ACAO_LOOP_EXTERNO and passo.i > 0:
                # As últimas i posições já contêm os i maiores, ordenados
                fim = list(passo.estado[n - passo.i:])
                self.assertEqual(fim, sorted(app.ARRAY_INICIAL)[n - passo.i:])


# =============================================================================
# GatoElemento
# =============================================================================
class TestGatoElemento(unittest.TestCase):
    def setUp(self):
        self.gato = app.GatoElemento(5, x=100, escala=1.0, y_pes=400)

    def test_estado_inicial(self):
        self.assertEqual(self.gato.numero, 5)
        self.assertEqual(self.gato.x, 100)
        self.assertEqual(self.gato.y_base, 400 - app.RAIO_CORPO_BASE)
        self.assertEqual(self.gato.y, self.gato.y_base)
        self.assertEqual(self.gato.altura_atual, 0)
        self.assertFalse(self.gato.em_animacao)

    def test_escala_altera_o_tamanho(self):
        grande = app.GatoElemento(9, x=0, escala=1.2)
        self.assertAlmostEqual(grande.raio_corpo, app.RAIO_CORPO_BASE * 1.2)
        self.assertAlmostEqual(grande.raio_cabeca, app.RAIO_CABECA_BASE * 1.2)

    def test_pulo_em_arco(self):
        self.gato.iniciar_movimento(300, altura_arco=80, duracao=1.0)
        self.assertTrue(self.gato.em_animacao)

        self.gato.atualizar(0.5)  # metade do tempo -> metade do caminho, topo do arco
        self.assertAlmostEqual(self.gato.x, 200)
        self.assertAlmostEqual(self.gato.altura_atual, 80)

        self.gato.atualizar(0.5)
        self.assertFalse(self.gato.em_animacao)
        self.assertEqual(self.gato.x, 300)
        self.assertEqual(self.gato.y, self.gato.y_base)

    def test_deslizar_mantem_o_y(self):
        self.gato.iniciar_movimento(0, altura_arco=0, duracao=1.0)
        for _ in range(10):
            self.gato.atualizar(0.1)
            self.assertAlmostEqual(self.gato.y, self.gato.y_base)
        self.assertAlmostEqual(self.gato.x, 0)

    def test_x_avanca_sempre_na_direcao_do_destino(self):
        self.gato.iniciar_movimento(300, altura_arco=50, duracao=1.0)
        anterior = self.gato.x
        while self.gato.em_animacao:
            self.gato.atualizar(1 / 60)
            self.assertGreaterEqual(self.gato.x, anterior)
            anterior = self.gato.x

    def test_dt_grande_nao_ultrapassa_o_destino(self):
        self.gato.iniciar_movimento(300, altura_arco=50, duracao=0.5)
        self.gato.atualizar(10)
        self.assertEqual(self.gato.x, 300)
        self.assertFalse(self.gato.em_animacao)

    def test_concluir_movimento(self):
        self.gato.iniciar_movimento(250, altura_arco=60, duracao=1.0)
        self.gato.atualizar(0.3)
        self.gato.concluir_movimento()
        self.assertEqual((self.gato.x, self.gato.y), (250, self.gato.y_base))
        self.assertFalse(self.gato.em_animacao)

    def test_duracao_zero_move_instantaneamente(self):
        self.gato.iniciar_movimento(500, altura_arco=60, duracao=0)
        self.assertEqual(self.gato.x, 500)
        self.assertFalse(self.gato.em_animacao)

    def test_atualizar_parado_nao_faz_nada(self):
        self.gato.atualizar(1.0)
        self.assertEqual((self.gato.x, self.gato.y), (100, self.gato.y_base))

    def test_desenhar_em_todos_os_estados(self):
        pygame.font.init()
        fonte = pygame.font.Font(None, 22)
        fundo = (1, 2, 3)
        for estado in (app.ESTADO_NORMAL, app.ESTADO_COMPARANDO, app.ESTADO_ORDENADO):
            with self.subTest(estado=estado):
                superficie = pygame.Surface((300, 500))
                superficie.fill(fundo)
                self.gato.desenhar(superficie, fonte, estado)
                # Algo foi desenhado na posição do corpo
                cor = superficie.get_at((int(self.gato.x) + 20, int(self.gato.y)))[:3]
                self.assertNotEqual(tuple(cor), fundo)

    def test_comparando_desenha_brilho_amarelo(self):
        pygame.font.init()
        fonte = pygame.font.Font(None, 22)
        superficie = pygame.Surface((300, 500))
        self.gato.desenhar(superficie, fonte, app.ESTADO_COMPARANDO)
        # Logo além da borda esquerda do corpo fica o halo de destaque
        x = int(self.gato.x - self.gato.raio_corpo - 4)
        self.assertEqual(tuple(superficie.get_at((x, int(self.gato.y))))[:3], app.COR_DESTAQUE)


# =============================================================================
# VisualizadorBubbleSort
# =============================================================================
class TestVisualizadorBubbleSort(unittest.TestCase):
    def setUp(self):
        self.vis = app.VisualizadorBubbleSort()

    def tearDown(self):
        pygame.quit()

    def executar_ate_o_fim(self):
        passos = 0
        while self.vis.avancar_passo():
            passos += 1
            self.assertLess(passos, 1000, "o algoritmo não terminou")
        self.vis.concluir_animacoes()
        return passos

    # ---------------------------------------------------------------- estado
    def test_estado_inicial(self):
        self.assertEqual(self.vis.numeros, list(app.ARRAY_INICIAL))
        self.assertFalse(self.vis.concluido)
        self.assertFalse(self.vis.modo_automatico)
        self.assertIsNone(self.vis.linha_atual)
        self.assertEqual((self.vis.comparacoes, self.vis.trocas), (0, 0))
        for gato, x in zip(self.vis.gatos, self.vis.posicoes_x):
            self.assertEqual(gato.x, x)

    def test_array_vazio_e_rejeitado(self):
        with self.assertRaises(ValueError):
            app.VisualizadorBubbleSort([])

    def test_gatos_maiores_representam_numeros_maiores(self):
        por_numero = sorted(self.vis.gatos, key=lambda g: g.numero)
        raios = [g.raio_corpo for g in por_numero]
        self.assertEqual(raios, sorted(raios))

    # ------------------------------------------------------------- algoritmo
    def test_ordenacao_completa(self):
        passos = self.executar_ate_o_fim()
        self.assertEqual(passos, 80)
        self.assertEqual(self.vis.numeros, sorted(app.ARRAY_INICIAL))
        self.assertTrue(self.vis.concluido)
        self.assertEqual(self.vis.comparacoes, 28)
        self.assertEqual(self.vis.trocas, 14)
        self.assertEqual(self.vis.ordenados, set(range(8)))
        self.assertEqual(self.vis.linha_atual, app.LINHA_RETURN)
        # Cada gato terminou exatamente na posição X do seu índice
        for gato, x in zip(self.vis.gatos, self.vis.posicoes_x):
            self.assertAlmostEqual(gato.x, x)
            self.assertAlmostEqual(gato.y, gato.y_base)

    def test_gatos_ficam_sincronizados_com_o_algoritmo(self):
        while self.vis.avancar_passo():
            self.assertEqual(self.vis.numeros, list(self.vis.passo_atual.estado))
            self.assertEqual(self.vis.linha_atual, self.vis.passo_atual.linha)

    def test_avancar_depois_do_fim_retorna_false(self):
        self.executar_ate_o_fim()
        self.assertFalse(self.vis.avancar_passo())

    def test_troca_inicia_animacao_com_arco_e_deslize(self):
        while self.vis.avancar_passo():
            if self.vis.passo_atual.acao == app.ACAO_TROCA:
                break
        j = self.vis.passo_atual.j
        maior, menor = self.vis.gatos[j + 1], self.vis.gatos[j]
        self.assertTrue(maior.em_animacao and menor.em_animacao)
        self.assertGreater(maior.altura_arco, 0)  # o maior pula por cima
        self.assertEqual(menor.altura_arco, 0)    # o menor desliza
        self.assertEqual(maior.x_destino, self.vis.posicoes_x[j + 1])
        self.assertEqual(menor.x_destino, self.vis.posicoes_x[j])

    def test_avancar_durante_animacao_finaliza_a_animacao(self):
        while self.vis.avancar_passo():
            if self.vis.passo_atual.acao == app.ACAO_TROCA:
                break
        self.assertTrue(self.vis.animacoes_em_andamento())
        self.vis.avancar_passo()
        self.assertFalse(self.vis.animacoes_em_andamento())

    def test_destaques_e_ordenados(self):
        while self.vis.avancar_passo():
            passo = self.vis.passo_atual
            if passo.acao == app.ACAO_COMPARACAO:
                self.assertEqual(self.vis.destacados, (passo.j, passo.j + 1))
                self.assertEqual(self.vis.estado_do_gato(passo.j), app.ESTADO_COMPARANDO)
            if passo.acao == app.ACAO_LOOP_EXTERNO and passo.i == 3:
                self.assertEqual(self.vis.ordenados, {5, 6, 7})
                self.assertEqual(self.vis.estado_do_gato(7), app.ESTADO_ORDENADO)

    def test_reiniciar(self):
        for _ in range(20):
            self.vis.avancar_passo()
        self.vis.modo_automatico = True
        self.vis.reiniciar()
        self.assertEqual(self.vis.numeros, list(app.ARRAY_INICIAL))
        self.assertEqual((self.vis.comparacoes, self.vis.trocas), (0, 0))
        self.assertFalse(self.vis.modo_automatico)
        self.assertIsNone(self.vis.passo_atual)
        self.assertEqual(self.executar_ate_o_fim(), 80)

    def test_array_personalizado(self):
        vis = app.VisualizadorBubbleSort([3, 3, 1])
        while vis.avancar_passo():
            pass
        self.assertEqual(vis.numeros, [1, 3, 3])

    # --------------------------------------------------------------- eventos
    def test_espaco_avanca_um_passo_e_pausa_o_automatico(self):
        self.vis.modo_automatico = True
        self.vis.processar_evento(tecla(pygame.K_SPACE))
        self.assertFalse(self.vis.modo_automatico)
        self.assertEqual(self.vis.passo_atual.acao, app.ACAO_INICIO)
        self.vis.processar_evento(tecla(pygame.K_SPACE))
        self.assertEqual(self.vis.passo_atual.acao, app.ACAO_LOOP_EXTERNO)

    def test_enter_liga_e_desliga_o_automatico(self):
        self.vis.processar_evento(tecla(pygame.K_RETURN))
        self.assertTrue(self.vis.modo_automatico)
        self.vis.processar_evento(tecla(pygame.K_KP_ENTER))
        self.assertFalse(self.vis.modo_automatico)

    def test_enter_depois_do_fim_recomeca_no_automatico(self):
        self.executar_ate_o_fim()
        self.vis.processar_evento(tecla(pygame.K_RETURN))
        self.assertFalse(self.vis.concluido)
        self.assertTrue(self.vis.modo_automatico)
        self.assertEqual(self.vis.numeros, list(app.ARRAY_INICIAL))

    def test_tecla_r_reinicia(self):
        for _ in range(30):
            self.vis.avancar_passo()
        self.vis.processar_evento(tecla(pygame.K_r))
        self.assertIsNone(self.vis.passo_atual)
        self.assertEqual(self.vis.numeros, list(app.ARRAY_INICIAL))

    def test_esc_e_fechar_janela_encerram(self):
        self.vis.processar_evento(tecla(pygame.K_ESCAPE))
        self.assertFalse(self.vis.rodando)
        self.vis.rodando = True
        self.vis.processar_evento(pygame.event.Event(pygame.QUIT))
        self.assertFalse(self.vis.rodando)

    def test_controle_de_velocidade_respeita_limites(self):
        for _ in range(10):
            self.vis.processar_evento(tecla(pygame.K_PLUS))
        self.assertEqual(self.vis.velocidade, app.VELOCIDADE_MAX)
        for _ in range(10):
            self.vis.processar_evento(tecla(pygame.K_MINUS))
        self.assertEqual(self.vis.velocidade, app.VELOCIDADE_MIN)
        self.vis.processar_evento(tecla(pygame.K_UP))
        self.assertEqual(self.vis.velocidade, app.VELOCIDADE_MIN * 2)

    def test_velocidade_encurta_a_animacao_da_troca(self):
        self.vis.velocidade = 2.0
        while self.vis.avancar_passo():
            if self.vis.passo_atual.acao == app.ACAO_TROCA:
                break
        self.assertAlmostEqual(self.vis.gatos[0].duracao, app.DURACAO_TROCA / 2)

    def test_outros_eventos_sao_ignorados(self):
        self.vis.processar_evento(pygame.event.Event(pygame.MOUSEMOTION, pos=(0, 0), rel=(0, 0), buttons=(0, 0, 0)))
        self.vis.processar_evento(tecla(pygame.K_a))
        self.assertIsNone(self.vis.passo_atual)
        self.assertTrue(self.vis.rodando)

    # ------------------------------------------------------- modo automático
    def test_automatico_espera_o_intervalo(self):
        self.vis.modo_automatico = True
        self.vis.atualizar(app.INTERVALO_AUTO / 2)
        self.assertIsNone(self.vis.passo_atual)
        self.vis.atualizar(app.INTERVALO_AUTO / 2 + 0.01)
        self.assertEqual(self.vis.passo_atual.acao, app.ACAO_INICIO)

    def test_automatico_nao_avanca_durante_animacao(self):
        while self.vis.avancar_passo():
            if self.vis.passo_atual.acao == app.ACAO_TROCA:
                break
        passo = self.vis.passo_atual
        self.vis.modo_automatico = True
        self.vis.atualizar(0.01)  # animação ainda rodando
        self.assertIs(self.vis.passo_atual, passo)

    def test_automatico_ordena_tudo_sozinho(self):
        self.vis.processar_evento(tecla(pygame.K_RETURN))
        quadros = 0
        while not self.vis.concluido:
            self.vis.atualizar(1 / 30)
            quadros += 1
            self.assertLess(quadros, 10_000, "o modo automático travou")
        self.assertEqual(self.vis.numeros, sorted(app.ARRAY_INICIAL))
        self.assertFalse(self.vis.modo_automatico)

    # --------------------------------------------------------------- desenho
    def test_desenhar_em_varios_momentos_nao_quebra(self):
        self.vis.desenhar()
        while self.vis.avancar_passo():
            self.vis.atualizar(0.2)  # captura gatos no meio do pulo
            self.vis.desenhar()
        self.vis.desenhar()

    def test_linha_ativa_do_codigo_fica_amarela(self):
        self.vis.avancar_passo()  # destaca a linha "n = len(arr)"
        self.vis.desenhar()
        rect = self.vis.rect_painel_codigo
        y = rect.top + 46 + app.LINHA_N * self.vis.altura_linha_codigo + 2
        cor = tuple(self.vis.tela.get_at((rect.right - 14, y)))[:3]
        self.assertEqual(cor, app.COR_LINHA_ATIVA)


if __name__ == "__main__":
    unittest.main(verbosity=2)
