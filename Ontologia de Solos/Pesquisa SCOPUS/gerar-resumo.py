import pandas as pd
import os
import google.generativeai as genai # Importa a biblioteca do Gemini
import sys # Importa o módulo sys para obter o caminho do script

def generate_summaries_with_gemini_and_update_planilha(caminho_planilha):
    """
    Gera resumos de textos usando a API do Gemini e atualiza uma planilha Excel.

    Args:
        caminho_planilha (str): O caminho completo para o arquivo Excel da planilha.
    """
    # --- Configuração da API do Gemini ---
    # VOCÊ DEVE INSERIR SUA CHAVE DE API AQUI!
    # Obtenha sua chave em https://makers.google.com/
    GEMINI_API_KEY = "AIzaSyAfY6q29S7c4wcsEQeYhBnGMwZDZkRdvG4" # Substitua por sua chave de API real!
    
    if not GEMINI_API_KEY:
        print("ERRO: A chave da API do Gemini não foi configurada. Por favor, insira sua chave em GEMINI_API_KEY.")
        return

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash') # Usando gemini-2.0-flash para geração de texto

    print(f"Carregando planilha de: {caminho_planilha}")
    try:
        df = pd.read_excel(caminho_planilha)
    except FileNotFoundError:
        print(f"Erro: Planilha não encontrada em '{caminho_planilha}'. Verifique o caminho.")
        return
    except Exception as e:
        print(f"Erro ao carregar a planilha: {e}")
        return

    # Itera sobre cada linha da planilha
    for index, row in df.iterrows():
        id_documento = str(row['ID do Documento']) # Garante que é uma string
        caminho_txt = row['Caminho do Arquivo de Texto Extraído (.txt)']
        resumo_existente = row['Resumo Gerado pela IA (Gemini)']

        # Verifica se o caminho do texto existe, se o arquivo .txt existe e se o resumo ainda não foi gerado
        if pd.notna(caminho_txt) and os.path.exists(caminho_txt) and pd.isna(resumo_existente):
            print(f"Gerando resumo para: {id_documento} (lendo de {caminho_txt})")
            try:
                with open(caminho_txt, 'r', encoding='utf-8') as txt_file:
                    document_text = txt_file.read()

                # Prompt para o Gemini
                # Você pode ajustar este prompt para obter o tipo de resumo desejado
                prompt = f"""
                Por favor, forneça um resumo conciso dos principais pontos e descobertas do seguinte documento,
                com foco em Ontologia de Solos, métodos, aplicações e resultados chave.
                O resumo deve ter entre 3 e 5 frases.

                Texto do Documento:
                {document_text}
                """
                
                # Chamada à API do Gemini
                response = model.generate_content(prompt)
                
                if response.candidates and response.candidates[0].content.parts:
                    generated_summary = response.candidates[0].content.parts[0].text
                    df.at[index, 'Resumo Gerado pela IA (Gemini)'] = generated_summary
                    print(f"Resumo gerado para {id_documento}.")
                else:
                    print(f"Aviso: Não foi possível gerar resumo para {id_documento}. Resposta da API: {response}")
                    df.at[index, 'Resumo Gerado pela IA (Gemini)'] = "ERRO: Não foi possível gerar resumo."

            except Exception as e:
                print(f"Erro ao gerar resumo para '{id_documento}': {e}")
                df.at[index, 'Resumo Gerado pela IA (Gemini)'] = f"ERRO: {e}"
        elif pd.isna(caminho_txt) or not os.path.exists(caminho_txt):
            print(f"Caminho do texto não disponível ou arquivo .txt não encontrado para '{id_documento}'. Pulando geração de resumo.")
        else:
            print(f"Resumo já existe para '{id_documento}'. Pulando.")

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

# --- Executa a função ---
if __name__ == "__main__":
    generate_summaries_with_gemini_and_update_planilha(PLANILHA_PATH)
