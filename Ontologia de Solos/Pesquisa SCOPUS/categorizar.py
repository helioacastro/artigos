import pandas as pd
import os
import google.generativeai as genai # Importa a biblioteca do Gemini
import sys # Importa o módulo sys para obter o caminho do script
import json # Para formatar a resposta do Gemini como JSON
import os 
from dotenv import load_dotenv


def categorize_summaries_with_gemini_and_update_planilha(caminho_planilha, categorias_ontologia_solos):
    """
    Categoriza resumos de textos usando a API do Gemini e atualiza uma planilha Excel.

    Args:
        caminho_planilha (str): O caminho completo para o arquivo Excel da planilha.
        categorias_ontologia_solos (dict): Um dicionário com as categorias e termos-chave para categorização.
                                          Ex: {'Categoria A': ['termo1', 'termo2'], ...}
    """
    # Carrega as variáveis do arquivo .env
    load_dotenv()    
    # --- Configuração da API do Gemini ---
    # VOCÊ DEVE INSERIR SUA CHAVE DE API AQUI!
    # Obtenha sua chave em https://makers.google.com/
    # GEMINI_API_KEY = "Substitua por sua chave de API real!"
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    
    if not gemini_api_key:
        print("ERRO: A chave da API do Gemini não foi configurada. Por favor, insira sua chave em GEMINI_API_KEY.")
        return

    genai.configure(api_key=gemini_api_key)
    model = genai.GenerativeModel('gemini-2.5-flash') # Usando gemini-2.0-flash para categorização

    print(f"Carregando planilha de: {caminho_planilha}")
    try:
        df = pd.read_excel(caminho_planilha)
    except FileNotFoundError:
        print(f"Erro: Planilha não encontrada em '{caminho_planilha}'. Verifique o caminho.")
        return
    except Exception as e:
        print(f"Erro ao carregar a planilha: {e}")
        return

    # Preparar a lista de categorias para o prompt do Gemini
    lista_categorias_para_prompt = ", ".join(categorias_ontologia_solos.keys())

    # Itera sobre cada linha da planilha
    for index, row in df.iterrows():
        id_documento = str(row['ID do Documento']) # Garante que é uma string
        resumo = row['Resumo Gerado pela IA (Gemini)']
        categorias_existentes = row['Categorias Atribuídas pela IA (Gemini)']

        # Verifica se há um resumo e se as categorias ainda não foram atribuídas
        if pd.notna(resumo) and pd.isna(categorias_existentes):
            print(f"Categorizando resumo para: {id_documento}")
            try:
                # Prompt para o Gemini para categorização
                # Estamos pedindo uma resposta JSON para facilitar o parsing
                prompt = f"""
                Dado o seguinte resumo de um artigo sobre Ontologia de Solos,
                identifique qual das seguintes categorias melhor se aplica.
                Se múltiplas categorias se aplicarem, liste todas.
                Se nenhuma se aplicar, indique 'Outros'.

                Categorias disponíveis: {lista_categorias_para_prompt}

                Resumo:
                {resumo}

                Por favor, responda no formato JSON, com uma chave 'categorias' contendo uma lista de strings.
                Exemplo: {{"categorias": ["Categoria A", "Categoria B"]}}
                """
                
                # Configuração para resposta JSON
                generation_config = {
                    "response_mime_type": "application/json",
                    "response_schema": {
                        "type": "OBJECT",
                        "properties": {
                            "categorias": {
                                "type": "ARRAY",
                                "items": {"type": "STRING"}
                            }
                        }
                    }
                }

                # Chamada à API do Gemini
                response = model.generate_content(prompt, generation_config=generation_config)
                
                if response.candidates and response.candidates[0].content.parts:
                    # O conteúdo da resposta JSON vem como uma string, precisa ser parseado
                    json_string = response.candidates[0].content.parts[0].text
                    
                    try:
                        parsed_response = json.loads(json_string)
                        assigned_categories = parsed_response.get('categorias', [])
                        
                        # Converte a lista de categorias em uma string separada por ponto e vírgula
                        df.at[index, 'Categorias Atribuídas pela IA (Gemini)'] = "; ".join(assigned_categories)
                        print(f"Categorias atribuídas para {id_documento}: {'; '.join(assigned_categories)}")
                    except json.JSONDecodeError:
                        print(f"Aviso: Resposta JSON inválida para {id_documento}: {json_string}")
                        df.at[index, 'Categorias Atribuídas pela IA (Gemini)'] = "ERRO: Resposta JSON inválida."
                else:
                    print(f"Aviso: Não foi possível categorizar {id_documento}. Resposta da API: {response}")
                    df.at[index, 'Categorias Atribuídas pela IA (Gemini)'] = "ERRO: Não foi possível categorizar."

            except Exception as e:
                print(f"Erro ao categorizar resumo para '{id_documento}': {e}")
                df.at[index, 'Categorias Atribuídas pela IA (Gemini)'] = f"ERRO: {e}"
        elif pd.isna(resumo):
            print(f"Resumo não disponível para '{id_documento}'. Pulando categorização.")
        else:
            print(f"Categorias já existem para '{id_documento}'. Pulando.")

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

# --- DEFINA SUAS CATEGORIAS AQUI ---
# Este dicionário será usado para guiar a categorização do Gemini.
# As chaves são os nomes das categorias e os valores são listas de termos-chave
# ou descrições que ajudam a definir a categoria para a IA.
# O Gemini usará os nomes das chaves para a categorização.
CATEGORIAS_ONTOLOGIA_SOLOS = {
    "Vocabulários Controlados em Solos": [
        "terminologia de solos", "glossário de solos", "thesaurus de solos",
        "vocabulário controlado", "ontologia leve", "padronização de termos"
    ],
    "Interoperabilidade de Dados de Solos": [
        "compartilhamento de dados de solos", "integração de dados de solos",
        "padrões de dados de solos", "troca de informações de solos",
        "serviços web de solos", "APIs de solos"
    ],
    "Modelagem Semântica de Solos": [
        "ontologia de solos", "modelagem conceitual de solos",
        "representação do conhecimento em solos", "OWL", "RDF", "lógica descritiva",
        "raciocínio ontológico"
    ],
    "Aplicações de Ontologia de Solos em Agricultura de Precisão": [
        "agricultura de precisão", "manejo de solos", "tomada de decisão em solos",
        "sensores de solos", "mapas de solos", "otimização de recursos"
    ],
    "Padrões ISO para Solos e Ontologias": [
        "ISO 19152", "ISO 25178", "padrões de geoinformação",
        "normas técnicas de solos", "harmonização de dados"
    ],
    "Desafios e Limitações da Ontologia de Solos": [
        "desafios", "limitações", "complexidade", "adoção", "manutenção", "evolução"
    ],
    "Estudos de Caso e Implementações": [
        "estudo de caso", "projeto piloto", "implementação", "experiência prática", "plataforma"
    ],
    "Outros": [] # Categoria para artigos que não se encaixam nas demais
}

# --- Executa a função ---
if __name__ == "__main__":
    categorize_summaries_with_gemini_and_update_planilha(PLANILHA_PATH, CATEGORIAS_ONTOLOGIA_SOLOS)
