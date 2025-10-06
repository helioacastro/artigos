import pandas as pd
import bibtexparser
import os
import sys

def update_planilha_com_bibtex(caminho_planilha, pasta_bibtex):
    """
    Atualiza uma planilha Excel com metadados extraídos de arquivos BibTeX.

    Args:
        caminho_planilha (str): O caminho completo para o arquivo Excel da planilha.
        pasta_bibtex (str): O caminho para a pasta que contém os arquivos .bib.
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

    # Mapeamento dos campos BibTeX para as colunas da planilha
    # As chaves são os campos BibTeX, os valores são os nomes das colunas na planilha
    bibtex_to_planilha_map = {
        'title': 'Título Original do Artigo',
        'author': 'Autores',
        'year': 'Ano de Publicação',
        'Year': 'Ano de Publicação', # Para garantir compatibilidade com diferentes formatos
        'journal': 'Periódico/Conferência',
        'booktitle': 'Periódico/Conferência', # Para artigos de conferência
        'doi': 'URL/Link para o Artigo (SCOPUS/DOI)',
        'url': 'URL/Link para o Artigo (SCOPUS/DOI)',
        'keywords': 'Palavras-chave do Autor',
        'Author Keywords': 'Palavras-chave do Autor',
        'abstract': 'Abstract Original',
        'Source title' : 'Periódico/Conferência'
    }

    # Itera sobre cada linha da planilha
    for index, row in df.iterrows():
        id_documento = str(row['ID do Documento']) # Garante que é uma string

        # Extrai o nome base do arquivo (sem extensão)
        nome_base_arquivo = os.path.splitext(id_documento)[0]
        
        # Constrói o caminho potencial para o arquivo .bib
        caminho_bib_file = os.path.join(pasta_bibtex, f"{nome_base_arquivo}.bib")

        if os.path.exists(caminho_bib_file):
            print(f"Processando arquivo BibTeX: {caminho_bib_file}")
            try:
                with open(caminho_bib_file, 'r', encoding='utf-8') as bibtex_file:
                    bib_database = bibtexparser.load(bibtex_file)

                if bib_database.entries:
                    entry = bib_database.entries[0] # Assume que há apenas uma entrada por arquivo .bib

                    # Atualiza as colunas da planilha com os dados do BibTeX
                    for bib_field, planilha_column in bibtex_to_planilha_map.items():
                        if bib_field in entry:
                            value = entry[bib_field]
                            
                            # Formatação específica para autores
                            if bib_field == 'author':
                                # bibtexparser.customization.convert_to_unicode pode ser útil aqui
                                # mas para simplicidade, vamos apenas substituir 'and' por '; '
                                authors = value.replace(' and ', '; ')
                                df.at[index, planilha_column] = authors
                            # Formatação para DOI/URL
                            elif bib_field == 'doi':
                                df.at[index, planilha_column] = f"https://doi.org/{value}"
                            elif bib_field == 'url' and not pd.isna(df.at[index, 'URL/Link para o Artigo (SCOPUS/DOI)']):
                                # Se já tiver um DOI, não sobrescreve com URL, a menos que o DOI esteja vazio
                                if not df.at[index, 'URL/Link para o Artigo (SCOPUS/DOI)'].startswith("https://doi.org/"):
                                    df.at[index, planilha_column] = value
                                else:
                                    # Se a coluna já tem um DOI, podemos adicionar a URL como uma alternativa
                                    # ou apenas ignorar para evitar sobrescrever
                                    pass # Ignora se DOI já preenchido
                            else:
                                df.at[index, planilha_column] = value
                        else:
                            # Se o campo BibTeX não existir, garante que a coluna na planilha esteja vazia
                            # ou mantém o valor existente se já houver um (útil para campos opcionais)
                            if pd.isna(df.at[index, planilha_column]): # Apenas se estiver vazio
                                df.at[index, planilha_column] = None # Ou ''

                    # Atualiza as colunas de controle para indicar que o BibTeX foi processado
                    # df.at[index, 'BibTeX Processado?'] = 'Sim' # Adicionar se quiser uma coluna de controle
                else:
                    print(f"Aviso: Nenhum entrada encontrada no arquivo BibTeX: {caminho_bib_file}")

            except Exception as e:
                print(f"Erro ao processar arquivo BibTeX '{caminho_bib_file}': {e}")
        else:
            print(f"Arquivo BibTeX não encontrado para '{id_documento}' em '{caminho_bib_file}'. Ignorando.")

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
# Caminho para a pasta onde você salvou seus arquivos .bib
BIBTEX_FOLDER = r'' + PASTA_BASE + r'\\Metadados_BibTeX\\'

# --- Executa a função ---             
if __name__ == "__main__":
    update_planilha_com_bibtex(PLANILHA_PATH, BIBTEX_FOLDER)
