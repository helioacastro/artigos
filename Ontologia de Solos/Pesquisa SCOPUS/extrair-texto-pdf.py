import pandas as pd
import os
from PyPDF2 import PdfReader # Importa o PdfReader para extração de texto
import sys # Importa o módulo sys para obter o caminho do script

def extract_text_from_pdfs_and_update_planilha(caminho_planilha, pasta_pdfs_originais, pasta_textos_extraidos):
    """
    Extrai texto de arquivos PDF e atualiza uma planilha Excel.

    Args:
        caminho_planilha (str): O caminho completo para o arquivo Excel da planilha.
        pasta_pdfs_originais (str): O caminho para a pasta que contém os arquivos PDF originais.
        pasta_textos_extraidos (str): O caminho para a pasta onde os arquivos de texto serão salvos.
    """
    print(f"Carregando planilha de: {caminho_planilha}")
    try:
        df = pd.read_excel(caminho_planilha)
    except FileNotFoundError:
        print(f"Erro: Planilha não encontrada em '{caminho_planilha}'. Verifique o caminho.")
        return
    except Exception as e:
        print(f"Erro ao carregar a planilha: {e}")
        return

    # Garante que a pasta de textos extraídos exista
    os.makedirs(pasta_textos_extraidos, exist_ok=True)

    # Itera sobre cada linha da planilha
    for index, row in df.iterrows():
        id_documento = str(row['ID do Documento']) # Garante que é uma string

        # Extrai o nome base do arquivo (sem extensão)
        nome_base_arquivo = os.path.splitext(id_documento)[0]

        # Constrói o caminho potencial para o arquivo PDF original
        caminho_pdf_original = os.path.join(pasta_pdfs_originais, f"{nome_base_arquivo}.pdf")
        
        # Constrói o caminho para o arquivo de texto de saída
        caminho_txt_saida = os.path.join(pasta_textos_extraidos, f"{nome_base_arquivo}.txt")

        # Verifica se o PDF existe e se o texto ainda não foi extraído (coluna vazia)
        if os.path.exists(caminho_pdf_original) and pd.isna(row['Caminho do Arquivo de Texto Extraído (.txt)']):
            print(f"Extraindo texto de: {caminho_pdf_original}")
            try:
                with open(caminho_pdf_original, 'rb') as pdf_file:
                    reader = PdfReader(pdf_file)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text() + "\n" # Extrai texto de cada página

                # Salva o texto extraído em um arquivo .txt
                with open(caminho_txt_saida, 'w', encoding='utf-8') as txt_file:
                    txt_file.write(text)

                # Atualiza a planilha
                df.at[index, 'Caminho do Arquivo de Texto Extraído (.txt)'] = caminho_txt_saida
                df.at[index, 'PDF Disponível?'] = 'Sim' # Confirma que o PDF foi processado

            except Exception as e:
                print(f"Erro ao extrair texto de '{caminho_pdf_original}': {e}")
                df.at[index, 'Caminho do Arquivo de Texto Extraído (.txt)'] = f"ERRO: {e}" # Registra o erro na planilha
                df.at[index, 'PDF Disponível?'] = 'Erro' # Marca como erro
        elif not os.path.exists(caminho_pdf_original):
            # Se o PDF não for encontrado, apenas imprime uma mensagem e ignora a atualização da planilha
            print(f"PDF não encontrado para '{id_documento}' em '{caminho_pdf_original}'. Ignorando extração.")
        else:
            print(f"Texto já extraído para '{id_documento}'. Pulando.")


    # Salva a planilha atualizada
    try:
        df.to_excel(caminho_planilha, index=False)
        print(f"\nPlanilha atualizada e salva em: {caminho_planilha}")
    except Exception as e:
        print(f"Erro ao salvar a planilha: {e}")

# --- Configurações que você precisa ajustar ---
# Diretório base onde o script está localizado
PASTA_BASE = os.path.abspath(os.path.dirname(sys.argv[0]))

# Caminho completo para o seu arquivo Excel
PLANILHA_PATH = r'' + PASTA_BASE + '\\Pesquisa_Ontologia_Solos.xlsx'

# Caminho para a pasta onde você salvou seus arquivos PDF originais
PDFS_ORIGINAIS_FOLDER = r'' + PASTA_BASE + '\\PDFs_Originais\\'

# Caminho para a pasta onde os arquivos de texto extraídos serão salvos
TEXTOS_EXTRAIDOS_FOLDER = r'' + PASTA_BASE + '\\Textos_Extraidos\\'

# --- Executa a função ---
if __name__ == "__main__":
    extract_text_from_pdfs_and_update_planilha(PLANILHA_PATH, PDFS_ORIGINAIS_FOLDER, TEXTOS_EXTRAIDOS_FOLDER)
