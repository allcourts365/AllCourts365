from fpdf import FPDF
from fpdf.enums import XPos, YPos

class PDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 15)
        self.cell(0, 10, 'Manual do Administrador do Clube - AllCourts365', border=False, align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def chapter_title(self, title):
        self.set_font('helvetica', 'B', 12)
        self.set_fill_color(200, 220, 255)
        self.cell(0, 8, title, border=False, fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(4)

    def chapter_body(self, body):
        self.set_font('helvetica', '', 11)
        self.multi_cell(0, 6, body)
        self.ln(6)

    def list_item(self, text):
        self.set_font('helvetica', '', 11)
        self.multi_cell(0, 6, f'  -  {text}')
        self.ln(2)
        
    def sub_title(self, text):
        self.set_font('helvetica', 'B', 11)
        self.cell(0, 6, text, border=False, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(2)

pdf = PDF()
pdf.add_page()
pdf.set_auto_page_break(auto=True, margin=15)

# Índice
pdf.chapter_title('Índice')
index_items = [
    "1. Introdução",
    "2. Acesso e Configuração Inicial",
    "3. Gestão de Usuários e Atletas",
    "4. Gestão de Quadras",
    "5. Gestão de Torneios",
    "6. Notícias e Comunicação"
]
for item in index_items:
    pdf.set_font('helvetica', '', 11)
    pdf.cell(0, 6, item, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.ln(10)

# Capitulo 1
pdf.chapter_title('1. Introdução')
pdf.chapter_body('O painel administrativo do AllCourts365 oferece controle total sobre as operações do seu clube. Como administrador, você poderá gerenciar as configurações gerais do clube, as quadras, atletas, torneios e também disparar mensagens para seus membros.')

# Capitulo 2
pdf.chapter_title('2. Acesso e Configuração Inicial')
pdf.chapter_body('Após realizar o login na plataforma, você terá acesso à área administrativa (Painel Admin).')
pdf.sub_title('Configurações do Clube')
pdf.list_item('Informações Básicas: Acesse "Clubes" e selecione seu clube para editar informações como nome, site, descrição, e regras em PDF.')
pdf.list_item('Horários: Defina os horários de abertura e fechamento para dias de semana, sábados e domingos.')
pdf.list_item('Visuais e Marca d\'Água: Você pode ajustar o Favicon, Logo, Imagem/Vídeo de Fundo, e as cores do painel do seu clube, além de adicionar marca d\'água aos cards dos atletas.')
pdf.ln(4)

# Capitulo 3
pdf.chapter_title('3. Gestão de Usuários e Atletas')
pdf.chapter_body('O cadastro de jogadores é essencial para a operação de torneios e rankings.')
pdf.list_item('Aprovação de Vínculos: Na seção "Solicitações de Vínculo de Atleta", você pode aprovar usuários do aplicativo que desejam se vincular aos atletas do seu clube.')
pdf.list_item('Mesclagem de Atletas: Caso existam atletas duplicados, vá em "Atletas", selecione os duplicados e utilize a ação "Mesclar atletas selecionados" no topo da página. O atleta principal que você escolher herdará todas as partidas e estatísticas.')
pdf.list_item('Gestão de Perfis: Você pode editar os perfis técnicos dos atletas (Estilo de jogo, Raquete, Lado, etc.) através de "Perfis de Usuário".')
pdf.ln(4)

# Capitulo 4
pdf.chapter_title('4. Gestão de Quadras')
pdf.chapter_body('Para criar ou editar as quadras disponíveis no seu clube:')
pdf.list_item('Vá até "Quadras" no menu principal.')
pdf.list_item('Você pode marcar uma quadra como disponível para "Ranking" ou para torneios "Eliminatórios" (ou ambos).')
pdf.ln(4)

# Capitulo 5
pdf.chapter_title('5. Gestão de Torneios')
pdf.chapter_body('O sistema suporta Torneios de Ranking e Eliminatórios.')
pdf.sub_title('Configuração de Torneios (Ranking/Eliminatório)')
pdf.list_item('Na seção "Ranking" ou "Torneio Eliminatório", você pode criar um novo torneio definindo o formato de set, duração, data de início/fim e prazo de inscrição.')
pdf.list_item('Defina as regras de pontuação personalizadas caso não queira usar o padrão.')

pdf.sub_title('Sorteio e Chaves Automáticas')
pdf.list_item('Para criar as chaves/rodadas automaticamente, baixe a Planilha Modelo fornecida no formulário do torneio.')
pdf.list_item('Preencha com o Nome, Categoria, e Email dos atletas, e envie através do campo "Upload Planilha".')
pdf.list_item('O sistema gerará automaticamente todos os confrontos iniciais com base nos inscritos da planilha. Opcionalmente para Torneios Eliminatórios, será gerada uma chave eliminatória.')

pdf.sub_title('Histórico e Partidas')
pdf.list_item('No caso de Rankings, você pode enviar uma planilha de Histórico para importar jogos anteriores.')
pdf.list_item('Em "Partidas", você pode ver e editar os jogos individualmente, definindo o placar Set a Set, e finalizando a partida para calcular a pontuação automaticamente.')
pdf.ln(4)

# Capitulo 6
pdf.chapter_title('6. Notícias e Comunicação')
pdf.chapter_body('Mantenha os atletas informados usando o módulo de comunicação.')
pdf.list_item('Notícias: Crie postagens em "Notícias" que aparecerão na página inicial do seu clube. Você pode adicionar texto rico, imagens e vídeos.')
pdf.list_item('Mensagens em Massa (Broadcast): Acesse "Mensagens em Massa" para enviar avisos diretamente para o painel de mensagens dos atletas do clube.')

pdf.output("Manual_Admin_Clube_AllCourts365_v2.pdf")
print("PDF gerado com sucesso!")
