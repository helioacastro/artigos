import pandas as pd
import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import black
from reportlab.lib.units import inch

def generate_single_abstract_pdf(caminho_planilha, caminho_pdf_saida):
    """
    Gera um arquivo PDF ÚNICO contendo os Abstracts Originais para registros
    onde o PDF original não está disponível na planilha, com uma página por artigo.

    Args:
        caminho_planilha (str): Caminho completo para o arquivo Excel da planilha.
        caminho_pdf_saida (str): Caminho completo para o arquivo PDF final que será gerado.
    """
    
    print(f"Carregando planilha de: {caminho_planilha}")
    try:
        df = pd.read_excel(caminho_planilha)
    except FileNotFoundError:
        print(f"ERRO: Planilha não encontrada em '{caminho_planilha}'.")
        return
    except Exception as e:
        print(f"ERRO ao carregar a planilha: {e}")
        return

    # Garante que a pasta de saída do PDF exista
    pasta_saida = os.path.dirname(caminho_pdf_saida)
    if pasta_saida:
        os.makedirs(pasta_saida, exist_ok=True)

    # Estilos do ReportLab
    styles = getSampleStyleSheet()
    
    # Estilo para o Título (Centralizado e em negrito)
    title_style = ParagraphStyle(
        name='TitleStyle',
        parent=styles['Heading1'],
        fontSize=14,
        leading=16,
        alignment=1, # Centro
        spaceAfter=12,
        textColor=black
    )
    
    # Estilo para Metadados (Autores/Ano)
    meta_style = ParagraphStyle(
        name='MetaStyle',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        alignment=1, # Centro
        spaceAfter=12,
        textColor=black
    )
    
    # Estilo para o Abstract
    abstract_style = ParagraphStyle(
        name='AbstractStyle',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        alignment=4, # Justificado
        spaceBefore=12,
        textColor=black
    )

    # 1. Filtra os registros: PDF Disponível? != 'Sim' E Abstract Original não vazio
    df_filtrado = df[
        (df['PDF Disponível?'].astype(str).str.lower() != 'sim') & 
        (df['Abstract Original'].notna()) & 
        (df['Abstract Original'].astype(str).str.strip() != '')
    ]
    
    total_registros = len(df_filtrado)
    print(f"\nEncontrados {total_registros} registros para inserir no PDF.")

    if total_registros == 0:
        print("Nenhum abstract para processar. O PDF não será gerado.")
        return

    # 2. Inicializa o documento e a lista "story" UMA ÚNICA VEZ antes do loop
    doc = SimpleDocTemplate(caminho_pdf_saida, pagesize=letter)
    story = []

    # 3. Itera sobre os registros filtrados para preencher o PDF
    processados_com_sucesso = 0
    for index, row in df_filtrado.iterrows():
        try:
            id_documento = str(row['ID do Documento']).replace(".pdf", "").replace(".bib", "").strip()
            
            # 1. Título
            titulo = str(row['Título Original do Artigo']).strip() if pd.notna(row['Título Original do Artigo']) else "Título Indisponível"
            story.append(Paragraph(titulo, title_style))
            
            # 2. Metadados (Autores e Ano)
            autores = str(row['Autores']).strip() if pd.notna(row['Autores']) else "Autores Indisponíveis"
            ano = str(row['Ano de Publicação']).strip() if pd.notna(row['Ano de Publicação']) else "s.d."
            metadados = f"{autores} ({ano})"
            story.append(Paragraph(metadados, meta_style))
            
            # 3. Identificador Opcional (ID do Documento) - Útil para saber qual artigo é qual
            story.append(Paragraph(f"<b>ID do Documento:</b> {id_documento}", styles['Normal']))
            
            # 4. Cabeçalho Abstract
            story.append(Spacer(1, 0.3 * inch))
            story.append(Paragraph("<b>ABSTRACT ORIGINAL</b>", styles['Heading3']))
            story.append(Spacer(1, 0.1 * inch))
            
            # 5. Conteúdo do Abstract
            abstract_text = str(row['Abstract Original']).strip()
            # Remove quebras de linha e normaliza espaços para evitar problemas de formatação no PDF
            abstract_text = abstract_text.replace('\n', ' ').replace('\r', ' ')
            story.append(Paragraph(abstract_text, abstract_style))

            # 6. Adiciona a QUEBRA DE PÁGINA ao final de cada artigo
            story.append(PageBreak())
            
            processados_com_sucesso += 1

        except Exception as e:
            print(f"ERRO ao processar o documento {id_documento}: {e}")
            
    # 4. Gera o arquivo PDF FINAL (Fora do loop)
    if processados_com_sucesso > 0:
        print("\nConstruindo o arquivo PDF...")
        try:
            doc.build(story)
            print(f"SUCESSO! Arquivo PDF compilado gerado com {processados_com_sucesso} páginas.")
            print(f"Salvo em: {caminho_pdf_saida}")
        except Exception as e:
            print(f"ERRO CRÍTICO ao salvar o PDF: {e}")
            print("Verifique se o arquivo já não está aberto em outro programa.")
    else:
        print("\nFalha ao processar os registros. O PDF não foi gerado.")


# --- Configurações que você precisa ajustar ---
# Diretório base onde o script está localizado
PASTA_BASE = os.path.abspath(os.path.dirname(sys.argv[0])) 

# Caminho completo para o seu arquivo Excel
PLANILHA_PATH = os.path.join(PASTA_BASE, 'Pesquisa_Ontologia_Solos.xlsx')

# Caminho para o ARQUIVO PDF ÚNICO que será gerado
# Mudei a variável para refletir que agora é um arquivo, não uma pasta
ARQUIVO_PDF_SAIDA = os.path.join(PASTA_BASE, 'Abstracts_Compilados.pdf')

# --- Executa a função ---
if __name__ == "__main__":
    generate_single_abstract_pdf(PLANILHA_PATH, ARQUIVO_PDF_SAIDA)