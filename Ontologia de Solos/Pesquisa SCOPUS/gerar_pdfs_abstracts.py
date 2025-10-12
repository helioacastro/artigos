import pandas as pd
import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import black
from reportlab.lib.units import inch

def generate_abstract_pdfs(caminho_planilha, pasta_pdfs_saida):
    """
    Gera arquivos PDF a partir do Abstract Original para registros
    onde o PDF original não está disponível na planilha.

    Args:
        caminho_planilha (str): Caminho completo para o arquivo Excel da planilha.
        pasta_pdfs_saida (str): Caminho para a pasta onde os novos PDFs serão salvos.
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

    # Garante que a pasta de saída exista
    os.makedirs(pasta_pdfs_saida, exist_ok=True)
    print(f"Arquivos PDF serão salvos em: {pasta_pdfs_saida}")

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
    
    print(f"\nEncontrados {len(df_filtrado)} registros para gerar PDFs de Abstract.")

    # 2. Itera sobre os registros filtrados para gerar os PDFs
    for index, row in df_filtrado.iterrows():
        try:
            id_documento = str(row['ID do Documento']).replace(".pdf", "").replace(".bib", "").strip()
            
            # Sanitiza o nome do arquivo, substituindo caracteres inválidos por underscore
            nome_arquivo_pdf = f"ABSTRACT_{id_documento}.pdf"
            for char in r'<>:"/\|?*':
                nome_arquivo_pdf = nome_arquivo_pdf.replace(char, '_')
                
            caminho_saida_pdf = os.path.join(pasta_pdfs_saida, nome_arquivo_pdf)

            # Conteúdo para o PDF
            story = []
            
            # 1. Título
            titulo = str(row['Título Original do Artigo']).strip() if pd.notna(row['Título Original do Artigo']) else "Título Indisponível"
            story.append(Paragraph(titulo, title_style))
            
            # 2. Metadados (Autores e Ano)
            autores = str(row['Autores']).strip() if pd.notna(row['Autores']) else "Autores Indisponíveis"
            ano = str(row['Ano de Publicação']).strip() if pd.notna(row['Ano de Publicação']) else "s.d."
            metadados = f"{autores} ({ano})"
            story.append(Paragraph(metadados, meta_style))
            
            # 3. Cabeçalho Abstract
            story.append(Spacer(1, 0.5 * inch))
            story.append(Paragraph("<b>ABSTRACT ORIGINAL</b>", styles['Heading3']))
            story.append(Spacer(1, 0.1 * inch))
            
            # 4. Conteúdo do Abstract
            abstract_text = str(row['Abstract Original']).strip()
            # O ReportLab precisa de texto bem formatado (pode usar tags HTML básicas como <b>, <i>, <br/>)
            # Remove quebras de linha e normaliza espaços para evitar problemas de formatação no PDF
            abstract_text = abstract_text.replace('\n', ' ').replace('\r', ' ')
            story.append(Paragraph(abstract_text, abstract_style))

            # 3. Gera o PDF
            doc = SimpleDocTemplate(caminho_saida_pdf, pagesize=letter)
            doc.build(story)
            
            print(f"  -> PDF gerado com sucesso: {nome_arquivo_pdf}")

        except Exception as e:
            print(f"ERRO CRÍTICO ao processar o documento {id_documento}: {e}")
            
    print("\nProcesso de geração de PDFs concluído.")

# --- Configurações que você precisa ajustar ---
# Diretório base onde o script está localizado
PASTA_BASE = os.path.abspath(os.path.dirname(sys.argv[0])) 

# Caminho completo para o seu arquivo Excel
PLANILHA_PATH = r'' + PASTA_BASE + '\\Pesquisa_Ontologia_Solos.xlsx'

# Caminho para a pasta onde os novos PDFs (com o Abstract) serão salvos
PASTA_PDFS_ABSTRACTS = r'' + PASTA_BASE + '\\PDFs_Abstracts_NotebookLM'

# --- Executa a função ---
if __name__ == "__main__":
    generate_abstract_pdfs(PLANILHA_PATH, PASTA_PDFS_ABSTRACTS)
