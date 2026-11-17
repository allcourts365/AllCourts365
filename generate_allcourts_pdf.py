import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register Arial TrueType fonts for native UTF-8 and standard sans-serif kerning
pdfmetrics.registerFont(TTFont('AppFont', 'C:/Windows/Fonts/arial.ttf'))
pdfmetrics.registerFont(TTFont('AppFont-Bold', 'C:/Windows/Fonts/arialbd.ttf'))
pdfmetrics.registerFont(TTFont('AppFont-Italic', 'C:/Windows/Fonts/ariali.ttf'))

FONT_REG = 'AppFont'
FONT_BOLD = 'AppFont-Bold'
FONT_ITALIC = 'AppFont-Italic'

# Output filename
OUTPUT_FILENAME = "Apresentacao_Comercial_AllCourts365.pdf"

# Page Dimensions (A4: 595.27 x 841.89 pt)
PAGE_W, PAGE_H = A4
MARGIN_X = 36
CONTENT_W = PAGE_W - (2 * MARGIN_X) # 523.27 pt

# Exact Brand Colors matching Focus PDF
BG_DARK = colors.HexColor('#0a0f1d')
BG_DARK_SECONDARY = colors.HexColor('#0d1527')
BG_ACCENT_CIRCLE = colors.HexColor('#101b33')
CARD_BG = colors.HexColor('#131d33')
CARD_BORDER = colors.HexColor('#1e2d4d')
ORANGE_PRIMARY = colors.HexColor('#ff7a00')
ORANGE_LIGHT = colors.HexColor('#ff9433')
ORANGE_BADGE_BG = colors.HexColor('#1c2230')
CYAN_ACCENT = colors.HexColor('#38bdf8')
GREEN_ACCENT = colors.HexColor('#10b981')
TEXT_WHITE = colors.HexColor('#ffffff')
TEXT_LIGHT_GRAY = colors.HexColor('#cbd5e1')
TEXT_MUTED = colors.HexColor('#94a3b8')
TEXT_DARK = colors.HexColor('#64748b')
TABLE_HEADER_BG = colors.HexColor('#10192d')
TABLE_ROW_BORDER = colors.HexColor('#1e293b')

def get_style(name, font=FONT_REG, size=9, leading=12, color=TEXT_LIGHT_GRAY, align=TA_LEFT, bold=False):
    fname = FONT_BOLD if bold else font
    return ParagraphStyle(
        name=name,
        fontName=fname,
        fontSize=size,
        leading=leading,
        textColor=color,
        alignment=align
    )

def draw_background(c, page_num):
    # Dark base background
    c.setFillColor(BG_DARK)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    
    # Decorative subtle circles
    c.setFillColor(BG_ACCENT_CIRCLE)
    if page_num == 1:
        c.circle(PAGE_W + 60, PAGE_H + 60, 200, stroke=0, fill=1)
        c.circle(-50, -50, 160, stroke=0, fill=1)
    elif page_num == 2:
        c.circle(-70, -70, 220, stroke=0, fill=1)
        c.circle(PAGE_W + 50, PAGE_H * 0.75, 140, stroke=0, fill=1)
    elif page_num == 3:
        c.circle(-80, -80, 230, stroke=0, fill=1)
        c.circle(PAGE_W + 70, -50, 170, stroke=0, fill=1)
    elif page_num == 4:
        c.circle(PAGE_W + 90, PAGE_H - 80, 220, stroke=0, fill=1)
        c.circle(-60, 180, 140, stroke=0, fill=1)

def draw_header(c, page_num):
    y = PAGE_H - 42
    if page_num == 1:
        # Modern AllCourts365 Logo on top-left
        c.setFont(FONT_BOLD, 22)
        c.setFillColor(TEXT_WHITE)
        c.drawString(MARGIN_X, y, "AllCourts")
        ac_w = c.stringWidth("AllCourts", FONT_BOLD, 22)
        c.setFillColor(ORANGE_PRIMARY)
        c.drawString(MARGIN_X + ac_w, y, "365")
        num_w = c.stringWidth("365", FONT_BOLD, 22)
        c.setFont(FONT_BOLD, 10)
        c.drawString(MARGIN_X + ac_w + num_w + 1, y + 9, "®")
        
        # Subtitle logo: by EVO2WIN
        c.setFont(FONT_BOLD, 8.5)
        c.setFillColor(TEXT_MUTED)
        c.drawString(MARGIN_X + 2, y - 11, "by")
        c.setFillColor(TEXT_WHITE)
        c.drawString(MARGIN_X + 16, y - 11, "EVO")
        c.setFillColor(ORANGE_PRIMARY)
        c.drawString(MARGIN_X + 37, y - 11, "2")
        c.setFillColor(TEXT_WHITE)
        c.drawString(MARGIN_X + 43, y - 11, "WIN")
        
        # Pill badge on top-right: B2B • APRESENTAÇÃO COMERCIAL OFICIAL
        badge_text = "B2B • APRESENTAÇÃO COMERCIAL OFICIAL"
        c.setFont(FONT_BOLD, 8)
        tw = c.stringWidth(badge_text, FONT_BOLD, 8)
        bx = PAGE_W - MARGIN_X - tw - 24
        by = y - 4
        bw = tw + 24
        bh = 22
        c.setStrokeColor(ORANGE_PRIMARY)
        c.setLineWidth(1)
        c.setFillColor(ORANGE_BADGE_BG)
        c.roundRect(bx, by, bw, bh, 11, stroke=1, fill=1)
        c.setFillColor(ORANGE_PRIMARY)
        c.drawString(bx + 12, by + 7, badge_text)
    else:
        # Header for pages 2, 3, 4
        c.setFont(FONT_BOLD, 8)
        c.setFillColor(ORANGE_PRIMARY)
        c.drawString(MARGIN_X, y + 8, "ALLCOURTS365® BY EVO2WIN")
        brand_w = c.stringWidth("ALLCOURTS365® BY EVO2WIN", FONT_BOLD, 8)
        c.setFont(FONT_REG, 8)
        c.setFillColor(TEXT_MUTED)
        c.drawString(MARGIN_X + brand_w + 6, y + 8, "•  Apresentação Comercial & Proposta de Valor para Arenas")
        
        c.setFillColor(TEXT_MUTED)
        c.drawRightString(PAGE_W - MARGIN_X, y + 8, "www.evo2win.com/allcourts")
        
        # Divider line
        c.setStrokeColor(colors.HexColor('#19253d'))
        c.setLineWidth(0.8)
        c.line(MARGIN_X, y, PAGE_W - MARGIN_X, y)

def draw_footer(c, page_num):
    y = 26
    c.setFont(FONT_BOLD, 8)
    c.setFillColor(ORANGE_PRIMARY)
    c.drawString(MARGIN_X, y, "AllCourts365 by EVO2WIN")
    w = c.stringWidth("AllCourts365 by EVO2WIN", FONT_BOLD, 8)
    c.setFont(FONT_REG, 8)
    c.setFillColor(TEXT_MUTED)
    c.drawString(MARGIN_X + w + 6, y, "•  Tecnologia Inteligente de Gestão Esportiva, Rankings e Torneios")
    
    c.drawRightString(PAGE_W - MARGIN_X, y, f"Página {page_num} de 4")

def draw_card(c, x, y, w, h, fill_color=CARD_BG, border_color=CARD_BORDER, radius=8, line_width=1):
    c.setFillColor(fill_color)
    c.setStrokeColor(border_color)
    c.setLineWidth(line_width)
    c.roundRect(x, y, w, h, radius, stroke=1, fill=1)

def draw_paragraph(c, text, style, x, top_y, avail_w, max_h=999):
    p = Paragraph(text, style)
    w, h = p.wrap(avail_w, max_h)
    p.drawOn(c, x, top_y - h)
    return h

def draw_check_icon(c, x, y, size=9, color=GREEN_ACCENT):
    c.saveState()
    c.setStrokeColor(color)
    c.setLineWidth(1.8)
    c.setLineCap(1)
    c.setLineJoin(1)
    p = c.beginPath()
    p.moveTo(x, y + (size * 0.45))
    p.lineTo(x + (size * 0.35), y + (size * 0.1))
    p.lineTo(x + (size * 0.95), y + (size * 0.85))
    c.drawPath(p, stroke=1, fill=0)
    c.restoreState()

# =========================================================================
# PAGE 1: Visão Geral e Proposta de Valor
# =========================================================================
def render_page_1(c):
    draw_background(c, 1)
    draw_header(c, 1)
    
    # Title: Transforme sua Arena em um Espetáculo Esportivo
    title_style = get_style('p1_title', FONT_BOLD, 25, 30, TEXT_WHITE, bold=True)
    draw_paragraph(c, "Transforme sua Arena em um Espetáculo Esportivo", title_style, MARGIN_X, PAGE_H - 100, CONTENT_W)
    
    # Subtitle
    sub_text = "O sistema inteligente de Gestão de Torneios, Rankings em Tempo Real e Agendamento de Quadras da <b>EVO2WIN</b>, valorizando suas quadras, encantando associados e automatizando 100% da operação do seu clube."
    sub_style = get_style('p1_sub', FONT_REG, 10, 14.5, TEXT_MUTED)
    draw_paragraph(c, sub_text, sub_style, MARGIN_X, PAGE_H - 168, CONTENT_W)
    
    # Callout Box 1: POR QUE AS ARENAS MAIS LUCRATIVAS ESTÃO ADOTANDO O ALLCOURTS365?
    box1_y = PAGE_H - 325
    box1_h = 120
    draw_card(c, MARGIN_X, box1_y, CONTENT_W, box1_h, fill_color=CARD_BG, border_color=CARD_BORDER, radius=8)
    
    c.setFont(FONT_BOLD, 9.5)
    c.setFillColor(ORANGE_PRIMARY)
    c.drawString(MARGIN_X + 16, box1_y + box1_h - 22, "POR QUE AS ARENAS MAIS LUCRATIVAS ESTÃO ADOTANDO O ALLCOURTS365?")
    
    box1_body = "Praticantes de <b>Beach Tennis, Padel, Tênis, Futevôlei e Pickleball</b> buscam organização impecável, desafios frequentes e reconhecimento. Administrar inscrições em grupos de WhatsApp, montar tabelas à mão e somar pontos de ranking no Excel consome dezenas de horas e gera atritos. O AllCourts365 entrega a experiência definitiva: chaves eliminatórias geradas em segundos, rankings dinâmicos atualizados na hora do ponto final e um portal exclusivo no smartphone do atleta, sem necessidade de baixar nenhum aplicativo."
    box1_style = get_style('p1_b1_text', FONT_REG, 9, 13.5, TEXT_LIGHT_GRAY)
    draw_paragraph(c, box1_body, box1_style, MARGIN_X + 16, box1_y + box1_h - 32, CONTENT_W - 32)
    
    # Section Header: OS 3 PILARES DO RETORNO COMERCIAL PARA SUA ARENA
    c.setFont(FONT_BOLD, 9.5)
    c.setFillColor(ORANGE_PRIMARY)
    c.drawString(MARGIN_X, PAGE_H - 348, "OS 3 PILARES DO RETORNO COMERCIAL PARA SUA ARENA")
    
    # 3 Pillar Cards in a Single Row Container
    pills_y = PAGE_H - 565
    pills_h = 205
    draw_card(c, MARGIN_X, pills_y, CONTENT_W, pills_h, fill_color=CARD_BG, border_color=CARD_BORDER, radius=8)
    
    col_w = (CONTENT_W - 32) / 3
    
    # Divider lines between pillars
    c.setStrokeColor(colors.HexColor('#192640'))
    c.setLineWidth(0.8)
    c.line(MARGIN_X + 16 + col_w, pills_y + 15, MARGIN_X + 16 + col_w, pills_y + pills_h - 15)
    c.line(MARGIN_X + 16 + (col_w * 2), pills_y + 15, MARGIN_X + 16 + (col_w * 2), pills_y + pills_h - 15)
    
    # Pillar 1
    p1_x = MARGIN_X + 16
    c.setFont(FONT_BOLD, 12)
    c.setFillColor(ORANGE_PRIMARY)
    c.drawString(p1_x, pills_y + pills_h - 26, "01. Eficiência & Tempo")
    p1_body = "Quadras gerenciadas pelo sistema AllCourts365 ganham dinamismo imediato. Você automatiza sorteios, chaveamento e cálculo de pontuações, economizando mais de 15 horas semanais da sua equipe e eliminando erros manuais de organização."
    p1_style = get_style('p1_col1', FONT_REG, 8.5, 13, TEXT_LIGHT_GRAY)
    draw_paragraph(c, p1_body, p1_style, p1_x, pills_y + pills_h - 38, col_w - 14)
    
    # Pillar 2
    p2_x = MARGIN_X + 16 + col_w + 14
    c.setFont(FONT_BOLD, 12)
    c.setFillColor(ORANGE_PRIMARY)
    c.drawString(p2_x, pills_y + pills_h - 26, "02. Retenção de Atletas")
    p2_body = "Rankings dinâmicos e calendários pessoais estimulam desafios contínuos entre os jogadores. Associados motivados jogam mais vezes por semana, aumentando o fluxo na arena e elevando o consumo no bar, locações de quadra e pro shop."
    p2_style = get_style('p1_col2', FONT_REG, 8.5, 13, TEXT_LIGHT_GRAY)
    draw_paragraph(c, p2_body, p2_style, p2_x, pills_y + pills_h - 38, col_w - 14)
    
    # Pillar 3
    p3_x = MARGIN_X + 16 + (col_w * 2) + 14
    c.setFont(FONT_BOLD, 12)
    c.setFillColor(ORANGE_PRIMARY)
    c.drawString(p3_x, pills_y + pills_h - 26, "03. Receita com Patrocínio")
    p3_body = "O AllCourts365 é 100% White-Label e possui espaços nobres para marcas parceiras nos murais, cards e tabelas de classificação. A venda dessas cotas comerciais locais cobre o investimento da plataforma com folga e gera lucro líquido mensal."
    p3_style = get_style('p1_col3', FONT_REG, 8.5, 13, TEXT_LIGHT_GRAY)
    draw_paragraph(c, p3_body, p3_style, p3_x, pills_y + pills_h - 38, col_w - 14)
    
    # Bottom 4 Metrics Bar
    bar_y = 52
    bar_h = 60
    draw_card(c, MARGIN_X, bar_y, CONTENT_W, bar_h, fill_color=CARD_BG, border_color=CARD_BORDER, radius=8)
    
    metric_w = CONTENT_W / 4
    
    # Metric Dividers
    for i in range(1, 4):
        cx = MARGIN_X + (metric_w * i)
        c.setStrokeColor(colors.HexColor('#192640'))
        c.setLineWidth(0.8)
        c.line(cx, bar_y + 10, cx, bar_y + bar_h - 10)
        
    metrics = [
        ("< 1 min", "Chaves e Sorteios na Hora"),
        ("100% Web", "Sem Instalação de App (PWA)"),
        ("White-Label", "Cores e Logo do Seu Clube"),
        ("Multi-Quadra", "Tênis, Beach, Padel e +")
    ]
    
    for i, (m_val, m_desc) in enumerate(metrics):
        mx = MARGIN_X + (metric_w * i) + (metric_w / 2)
        c.setFont(FONT_BOLD, 16)
        c.setFillColor(ORANGE_PRIMARY)
        c.drawCentredString(mx, bar_y + 34, m_val)
        c.setFont(FONT_REG, 8)
        c.setFillColor(TEXT_LIGHT_GRAY)
        c.drawCentredString(mx, bar_y + 16, m_desc)
        
    draw_footer(c, 1)

# =========================================================================
# PAGE 2: Recursos Desenvolvidos para Máxima Performance
# =========================================================================
def render_page_2(c):
    draw_background(c, 2)
    draw_header(c, 2)
    
    # Eyebrow
    c.setFont(FONT_BOLD, 8.5)
    c.setFillColor(ORANGE_PRIMARY)
    c.drawString(MARGIN_X, PAGE_H - 68, "TECNOLOGIA DE PONTA ALLCOURTS365 BY EVO2WIN")
    
    # Title
    c.setFont(FONT_BOLD, 22)
    c.setFillColor(TEXT_WHITE)
    c.drawString(MARGIN_X, PAGE_H - 96, "Recursos Desenvolvidos para Máxima Performance")
    
    # Subtitle
    c.setFont(FONT_REG, 9.5)
    c.setFillColor(TEXT_MUTED)
    c.drawString(MARGIN_X, PAGE_H - 114, "Conheça os recursos que tornam o AllCourts365 a solução mais completa e robusta do mercado para quadras esportivas:")
    
    # Grid Container for 6 Features
    grid_y = PAGE_H - 550
    grid_h = 420
    draw_card(c, MARGIN_X, grid_y, CONTENT_W, grid_h, fill_color=CARD_BG, border_color=CARD_BORDER, radius=8)
    
    # Vertical divider inside grid
    c.setStrokeColor(colors.HexColor('#192640'))
    c.setLineWidth(0.8)
    c.line(MARGIN_X + (CONTENT_W / 2), grid_y + 15, MARGIN_X + (CONTENT_W / 2), grid_y + grid_h - 15)
    
    # Feature Items (3 in col 1, 3 in col 2)
    col1_x = MARGIN_X + 16
    col2_x = MARGIN_X + (CONTENT_W / 2) + 16
    feature_w = (CONTENT_W / 2) - 32
    
    features = [
        # Col 1
        (col1_x, grid_y + grid_h - 22, "DISPONÍVEL", CYAN_ACCENT, "Rankings Automáticos & Rodadas", 
         "Pontuação inteligente calculada em tempo real por rodada, sets e categorias (simples e duplas). Classificação com critérios de desempate e histórico completo."),
        (col1_x, grid_y + grid_h - 158, "DISPONÍVEL", CYAN_ACCENT, "Portal & Dashboard do Atleta", 
         "Sem atrito e sem barreiras: o jogador acompanha sua agenda pessoal, estatísticas, histórico de confrontos (H2H) e lança resultados direto pelo navegador do celular."),
        (col1_x, grid_y + grid_h - 294, "DISPONÍVEL", CYAN_ACCENT, "Identidade White-Label Completa", 
         "O clube personaliza suas cores oficiais, logo, imagens/vídeos de fundo, favicon e adiciona marca d'água oficial aos cards digitais dos atletas associados."),
        
        # Col 2
        (col2_x, grid_y + grid_h - 22, "DISPONÍVEL", CYAN_ACCENT, "Torneios Eliminatórios (Brackets)", 
         "Geração visual instantânea de chaves eliminatórias com cabeças de chave, repescagem e chaves paralelas, prontas para impressão e acompanhamento ao vivo."),
        (col2_x, grid_y + grid_h - 158, "DISPONÍVEL", CYAN_ACCENT, "Multi-Quadra & Multi-Esporte", 
         "Gerencie 1, 6 ou mais de 20 quadras simultâneas com departamentos independentes para Tênis, Beach Tennis, Padel e Futevôlei com controle total em um só painel web."),
        (col2_x, grid_y + grid_h - 294, "EM DESENVOLVIMENTO • FASE 2", ORANGE_PRIMARY, "Integração Focus Vídeo & IA (EVO2WIN)", 
         "Futura integração nativa com o sistema de Replay Inteligente Focus e Análise Esportiva por IA da EVO2WIN, unindo chaveamento e replays dos pontos nas quadras.")
    ]
    
    for fx, top_pos, badge_txt, badge_color, feat_title, feat_desc in features:
        # Badge
        c.setFont(FONT_BOLD, 7.5)
        c.setFillColor(badge_color)
        c.drawString(fx, top_pos, f"■ {badge_txt}")
        
        # Title
        c.setFont(FONT_BOLD, 12)
        c.setFillColor(TEXT_WHITE)
        c.drawString(fx, top_pos - 18, feat_title)
        
        # Body
        b_style = get_style(f'feat_{feat_title[:5]}', FONT_REG, 8.5, 12.5, TEXT_LIGHT_GRAY)
        draw_paragraph(c, feat_desc, b_style, fx, top_pos - 26, feature_w)
    
    # Bottom Architecture Card
    arch_y = 52
    arch_h = 100
    draw_card(c, MARGIN_X, arch_y, CONTENT_W, arch_h, fill_color=CARD_BG, border_color=CARD_BORDER, radius=8)
    
    c.setFont(FONT_BOLD, 9.5)
    c.setFillColor(ORANGE_PRIMARY)
    c.drawString(MARGIN_X + 16, arch_y + arch_h - 22, "ARQUITETURA RESILIENTE EM NUVEM (ZERO TRAVAMENTOS E ZERO COMPLICAÇÃO)")
    
    arch_body = "Diferente de sistemas legados ou planilhas compartilhadas que corrompem e travam, o AllCourts365 trabalha com <b>arquitetura moderna em nuvem de alta disponibilidade</b> e tecnologia PWA (Progressive Web App). O sistema carrega instantaneamente em qualquer smartphone, tablet ou computador. Mesmo em finais de semana com dezenas de partidas simultâneas, o banco de dados processa os placares em milissegundos com sincronização imediata e backup diário automático."
    arch_style = get_style('p2_arch', FONT_REG, 8.5, 12.5, TEXT_LIGHT_GRAY)
    draw_paragraph(c, arch_body, arch_style, MARGIN_X + 16, arch_y + arch_h - 32, CONTENT_W - 32)
    
    draw_footer(c, 2)

# =========================================================================
# PAGE 3: Experiência do Usuário & Retorno Financeiro
# =========================================================================
def render_page_3(c):
    draw_background(c, 3)
    draw_header(c, 3)
    
    # Eyebrow
    c.setFont(FONT_BOLD, 8.5)
    c.setFillColor(ORANGE_PRIMARY)
    c.drawString(MARGIN_X, PAGE_H - 68, "EXPERIÊNCIA DO USUÁRIO & RETORNO FINANCEIRO")
    
    # Title - Perfectly balanced font size for Arial Bold
    c.setFont(FONT_BOLD, 20)
    c.setFillColor(TEXT_WHITE)
    c.drawString(MARGIN_X, PAGE_H - 96, "Da Organização Sem Esforço ao Lucro Real no Caixa")
    
    # Subtitle
    c.setFont(FONT_REG, 9.5)
    c.setFillColor(TEXT_MUTED)
    c.drawString(MARGIN_X, PAGE_H - 114, "Uma experiência intuitiva para os atletas e um modelo de negócios comprovadamente lucrativo para o gestor:")
    
    # 4-Step Process Box
    steps_y = PAGE_H - 250
    steps_h = 120
    draw_card(c, MARGIN_X, steps_y, CONTENT_W, steps_h, fill_color=CARD_BG, border_color=CARD_BORDER, radius=8)
    
    step_w = (CONTENT_W - 32) / 4
    
    # Step dividers
    for i in range(1, 4):
        sx = MARGIN_X + 16 + (step_w * i)
        c.setStrokeColor(colors.HexColor('#192640'))
        c.setLineWidth(0.8)
        c.line(sx, steps_y + 12, sx, steps_y + steps_h - 12)
        
    steps_data = [
        ("Passo 1", "Setup em Minutos", "Cadastre categorias, quadras e importe sua lista de atletas facilmente por planilha Excel ou link de auto-cadastro."),
        ("Passo 2", "Chaves & Rodadas", "O sistema sorteia as chaves eliminatórias ou gera as rodadas do ranking com distribuição justa de confrontos."),
        ("Passo 3", "Atletas em Ação", "Os jogadores acompanham o calendário, combinam a quadra e lançam os placares set a set diretamente pelo celular."),
        ("Passo 4", "Lucro & Engajamento", "O ranking atualiza na hora, os associados jogam mais vezes e o clube monetiza com torneios e patrocinadores.")
    ]
    
    for i, (s_num, s_title, s_desc) in enumerate(steps_data):
        sx = MARGIN_X + 16 + (step_w * i) + (0 if i == 0 else 8)
        avail_sw = step_w - 12
        
        c.setFont(FONT_BOLD, 9)
        c.setFillColor(ORANGE_PRIMARY)
        c.drawString(sx, steps_y + steps_h - 22, s_num)
        
        c.setFont(FONT_BOLD, 10.5)
        c.setFillColor(TEXT_WHITE)
        c.drawString(sx, steps_y + steps_h - 38, s_title)
        
        s_style = get_style(f'step_{i}', FONT_REG, 7.8, 11.5, TEXT_LIGHT_GRAY)
        draw_paragraph(c, s_desc, s_style, sx, steps_y + steps_h - 46, avail_sw)
    
    # Section Header: SIMULAÇÃO DE RETORNO FINANCEIRO MENSAL POR ARENA
    c.setFont(FONT_BOLD, 9.5)
    c.setFillColor(ORANGE_PRIMARY)
    c.drawString(MARGIN_X, PAGE_H - 275, "SIMULAÇÃO DE RETORNO FINANCEIRO MENSAL POR ARENA")
    
    # Table Box
    table_y = PAGE_H - 490
    table_h = 200
    draw_card(c, MARGIN_X, table_y, CONTENT_W, table_h, fill_color=CARD_BG, border_color=CARD_BORDER, radius=8)
    
    # Table Header Row
    th_h = 32
    c.setFillColor(TABLE_HEADER_BG)
    c.roundRect(MARGIN_X, table_y + table_h - th_h, CONTENT_W, th_h, 8, stroke=0, fill=1)
    # Square bottom of header
    c.rect(MARGIN_X, table_y + table_h - th_h, CONTENT_W, 10, stroke=0, fill=1)
    
    c.setFont(FONT_BOLD, 9.5)
    c.setFillColor(TEXT_WHITE)
    c.drawString(MARGIN_X + 16, table_y + table_h - 20, "Linha de Receita")
    c.drawString(MARGIN_X + 215, table_y + table_h - 20, "Estimativa Média")
    c.drawRightString(MARGIN_X + CONTENT_W - 16, table_y + table_h - 20, "Potencial Mensal")
    
    # Table Rows
    rows = [
        ("Inscrições em Rankings & Torneios", 
         "80 a 160 atletas em circuitos internos (taxa R$ 25 a R$ 50/mês)", 
         "R$ 2.000 a R$ 5.000 /mês", GREEN_ACCENT),
        ("Cotas de Patrocínio Digital", 
         "Até 3 marcas parceiras exibidas no portal White-Label e murais", 
         "R$ 1.200 a R$ 2.400 /mês", GREEN_ACCENT),
        ("Aumento na Locação de Quadras", 
         "Horas extras geradas por confrontos de ranking e desafios (30-60h)", 
         "R$ 800 a R$ 2.000 /mês", GREEN_ACCENT)
    ]
    
    row_h = 40
    curr_y = table_y + table_h - th_h
    
    for r_title, r_est, r_pot, r_color in rows:
        curr_y -= row_h
        # Line divider
        c.setStrokeColor(TABLE_ROW_BORDER)
        c.setLineWidth(0.8)
        c.line(MARGIN_X, curr_y + row_h, MARGIN_X + CONTENT_W, curr_y + row_h)
        
        c.setFont(FONT_BOLD, 9)
        c.setFillColor(TEXT_WHITE)
        c.drawString(MARGIN_X + 16, curr_y + 24, r_title)
        
        c.setFont(FONT_REG, 8)
        c.setFillColor(TEXT_MUTED)
        c.drawString(MARGIN_X + 16, curr_y + 11, r_est)
        
        c.setFont(FONT_BOLD, 9.5)
        c.setFillColor(r_color)
        c.drawRightString(MARGIN_X + CONTENT_W - 16, curr_y + 16, r_pot)
        
    # Table Summary / Total Row
    curr_y -= 48
    c.setStrokeColor(TABLE_ROW_BORDER)
    c.setLineWidth(1)
    c.line(MARGIN_X, curr_y + 48, MARGIN_X + CONTENT_W, curr_y + 48)
    
    c.setFillColor(colors.HexColor('#16223b'))
    c.roundRect(MARGIN_X, curr_y, CONTENT_W, 48, 8, stroke=0, fill=1)
    c.rect(MARGIN_X, curr_y + 35, CONTENT_W, 13, stroke=0, fill=1)
    
    c.setFont(FONT_BOLD, 9.5)
    c.setFillColor(TEXT_WHITE)
    c.drawString(MARGIN_X + 16, curr_y + 28, "POTENCIAL TOTAL DE FATURAMENTO")
    c.drawString(MARGIN_X + 16, curr_y + 14, "ADICIONAL")
    
    c.setFont(FONT_REG, 8.5)
    c.setFillColor(TEXT_LIGHT_GRAY)
    c.drawString(MARGIN_X + 215, curr_y + 20, "Cobre os custos e gera lucro líquido")
    
    c.setFont(FONT_BOLD, 11)
    c.setFillColor(ORANGE_PRIMARY)
    c.drawRightString(MARGIN_X + CONTENT_W - 16, curr_y + 20, "R$ 4.000 a R$ 9.400 /mês")
    
    # Bottom Differential Callout Box
    diff_y = 52
    diff_h = 100
    draw_card(c, MARGIN_X, diff_y, CONTENT_W, diff_h, fill_color=CARD_BG, border_color=CARD_BORDER, radius=8)
    
    c.setFont(FONT_BOLD, 9.5)
    c.setFillColor(ORANGE_PRIMARY)
    c.drawString(MARGIN_X + 16, diff_y + diff_h - 22, "DIFERENCIAL EXCLUSIVO: PORTAL WHITE-LABEL COM PATROCINADORES CLICÁVEIS")
    
    diff_body = "Enquanto outros sistemas exibem marcas de terceiros ou operam em tabelas engessadas, o AllCourts365 conta com um <b>Portal Web White-Label de última geração</b>. Tanto no desktop quanto no mobile, o associado visualiza a logomarca do patrocinador da sua arena e pode clicar no botão 'Visitar', sendo direcionado para o WhatsApp, Instagram ou site do anunciante. Isso transforma sua arena em uma <b>mídia comercial de alto impacto mensurável</b>."
    diff_style = get_style('p3_diff', FONT_REG, 8.5, 12.5, TEXT_LIGHT_GRAY)
    draw_paragraph(c, diff_body, diff_style, MARGIN_X + 16, diff_y + diff_h - 32, CONTENT_W - 32)
    
    draw_footer(c, 3)

# =========================================================================
# PAGE 4: Implantação, FAQ & Próximos Passos
# =========================================================================
def render_page_4(c):
    draw_background(c, 4)
    draw_header(c, 4)
    
    # Eyebrow
    c.setFont(FONT_BOLD, 8.5)
    c.setFillColor(ORANGE_PRIMARY)
    c.drawString(MARGIN_X, PAGE_H - 68, "IMPLANTAÇÃO, GARANTIA & PRÓXIMOS PASSOS")
    
    # Title
    c.setFont(FONT_BOLD, 22)
    c.setFillColor(TEXT_WHITE)
    c.drawString(MARGIN_X, PAGE_H - 96, "Tudo o que seu Clube Precisa para Começar")
    
    # Subtitle
    c.setFont(FONT_REG, 9.5)
    c.setFillColor(TEXT_MUTED)
    c.drawString(MARGIN_X, PAGE_H - 114, "Fornecemos a solução completa ponta a ponta: sem surpresas técnicas ou custos ocultos.")
    
    # 8-Item Checklist Box
    check_y = PAGE_H - 245
    check_h = 115
    draw_card(c, MARGIN_X, check_y, CONTENT_W, check_h, fill_color=CARD_BG, border_color=CARD_BORDER, radius=8)
    
    check_col_w = (CONTENT_W - 32) / 2
    
    items_left = [
        "Módulo Completo de Rankings (Simples e Duplas)",
        "Geração Instantânea de Chaves com PDF para Impressão",
        "Portal do Atleta com Histórico, Estatísticas e H2H",
        "Agendamento de Quadras com Prevenção de Conflitos"
    ]
    
    items_right = [
        "Personalização White-Label com Cores e Logo do Clube",
        "Placas de Quadra e Materiais com QR Code para os Atletas",
        "Suporte Técnico Dedicado e Treinamento da Equipe",
        "Importação Assistida de Dados e Planilhas Históricas"
    ]
    
    for i, it in enumerate(items_left):
        iy = check_y + check_h - 22 - (i * 24)
        draw_check_icon(c, MARGIN_X + 16, iy - 2, size=9, color=GREEN_ACCENT)
        c.setFont(FONT_REG, 8.5)
        c.setFillColor(TEXT_LIGHT_GRAY)
        c.drawString(MARGIN_X + 32, iy, it)
        
    for i, it in enumerate(items_right):
        iy = check_y + check_h - 22 - (i * 24)
        draw_check_icon(c, MARGIN_X + 16 + check_col_w, iy - 2, size=9, color=GREEN_ACCENT)
        c.setFont(FONT_REG, 8.5)
        c.setFillColor(TEXT_LIGHT_GRAY)
        c.drawString(MARGIN_X + 32 + check_col_w, iy, it)
        
    # FAQ Section
    faq_y = PAGE_H - 450
    faq_h = 185
    draw_card(c, MARGIN_X, faq_y, CONTENT_W, faq_h, fill_color=CARD_BG, border_color=CARD_BORDER, radius=8)
    
    c.setFont(FONT_BOLD, 9.5)
    c.setFillColor(ORANGE_PRIMARY)
    c.drawString(MARGIN_X + 16, faq_y + faq_h - 22, "PERGUNTAS FREQUENTES DE GESTORES DE CLUBES E ARENAS")
    
    faqs = [
        ("Preciso de equipamentos caros ou computadores dedicados no clube?",
         "Não! O AllCourts365 funciona 100% na nuvem. Você e seus administradores gerenciam tudo por qualquer navegador comum de celular, tablet ou computador conectado à internet."),
        ("Os jogadores precisam baixar algum aplicativo pesado na loja?",
         "Não! O AllCourts365 opera como Progressive Web App (PWA). O atleta aponta a câmera para o QR Code da quadra ou clica no link e já acessa instantaneamente sem ocupar espaço na memória."),
        ("É difícil migrar os dados das nossas planilhas e rankings atuais?",
         "Não! Disponibilizamos planilhas modelo e nossa equipe realiza a importação assistida de todos os seus atletas cadastrados e históricos anteriores para que a transição ocorra sem qualquer atrito.")
    ]
    
    fy_cursor = faq_y + faq_h - 40
    for q_text, a_text in faqs:
        # Divider line above questions 2 and 3
        if fy_cursor < faq_y + faq_h - 45:
            c.setStrokeColor(colors.HexColor('#192640'))
            c.setLineWidth(0.6)
            c.line(MARGIN_X + 16, fy_cursor + 8, MARGIN_X + CONTENT_W - 16, fy_cursor + 8)
            
        c.setFont(FONT_BOLD, 9)
        c.setFillColor(TEXT_WHITE)
        c.drawString(MARGIN_X + 16, fy_cursor - 6, q_text)
        
        a_style = get_style('faq_a', FONT_REG, 8, 11.5, TEXT_LIGHT_GRAY)
        h = draw_paragraph(c, a_text, a_style, MARGIN_X + 16, fy_cursor - 12, CONTENT_W - 32)
        fy_cursor -= (28 + h)

    # Big Orange-Bordered CTA Box
    cta_y = 52
    cta_h = 135
    c.setFillColor(CARD_BG)
    c.setStrokeColor(ORANGE_PRIMARY)
    c.setLineWidth(1.6)
    c.roundRect(MARGIN_X, cta_y, CONTENT_W, cta_h, 12, stroke=1, fill=1)
    
    c.setFont(FONT_BOLD, 18)
    c.setFillColor(ORANGE_PRIMARY)
    c.drawString(MARGIN_X + 24, cta_y + cta_h - 30, "PRONTO PARA ELEVAR O NÍVEL DA SUA")
    c.drawString(MARGIN_X + 24, cta_y + cta_h - 52, "ARENA?")
    
    cta_body = "Agende uma demonstração prática e descubra como o AllCourts365 pode transformar os torneios, rankings e a rotina do seu clube em um ambiente esportivo moderno, altamente concorrido e rentável."
    cta_style = get_style('cta_p', FONT_REG, 8.5, 12.5, TEXT_LIGHT_GRAY)
    draw_paragraph(c, cta_body, cta_style, MARGIN_X + 24, cta_y + cta_h - 64, CONTENT_W - 48)
    
    c.setFont(FONT_BOLD, 8.5)
    c.setFillColor(TEXT_WHITE)
    c.drawString(MARGIN_X + 24, cta_y + 36, "Fale diretamente com nosso Time Comercial:")
    
    c.setFont(FONT_REG, 8)
    c.setFillColor(TEXT_LIGHT_GRAY)
    c.drawString(MARGIN_X + 24, cta_y + 20, "■ WhatsApp / Telefone: Consulte seu representante comercial AllCourts365")
    c.drawString(MARGIN_X + 24, cta_y + 8, "■ E-mail: contato@evo2win.com   |   ■ Site: www.evo2win.com/allcourts")
    
    draw_footer(c, 4)

def build_pdf():
    c = canvas.Canvas(OUTPUT_FILENAME, pagesize=A4)
    
    print("Generating Page 1...")
    render_page_1(c)
    c.showPage()
    
    print("Generating Page 2...")
    render_page_2(c)
    c.showPage()
    
    print("Generating Page 3...")
    render_page_3(c)
    c.showPage()
    
    print("Generating Page 4...")
    render_page_4(c)
    c.showPage()
    
    c.save()
    print(f"PDF successfully generated: {OUTPUT_FILENAME}")

if __name__ == '__main__':
    build_pdf()
