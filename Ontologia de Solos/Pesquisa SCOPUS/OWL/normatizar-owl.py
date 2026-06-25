import re
import os

def full_fix_manchester(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Coleta todas as AnnotationProperty existentes para declará-las no topo
    annotation_properties = set(re.findall(r'([a-zA-Z0-9_]+:[a-zA-Z0-9_]+)', re.sub(r'Annotations:\s*.*?\n', '', content)))
    
    # Padroniza as anotações do cabeçalho da ontologia
    header_annotations = """Annotations:
       rabbit:Purpose "To describe soil properties and processes, as well as their relationships.",
       rabbit:Scope "The ontology mainly describes soil physical properties and processes, as well as how they affect each other.",
       rabbit:KnowledgeSource "The knowledge sources of this ontology include: - knowledge explained in the textbook: Principles of Soil Physics, by Rattan Lal and Manoj K. Shukla, 2004. - knowledge of domain experts - The SWEET ontology (https://sweet.jpl.nasa.gov) - online dictionaries: Oxford Dictionary (http://www.oxforddictionaries.com) and Cambridge Dictionary (http://dictionary.cambridge.org)",
       owl:VersionInfo "Version 1",
       rabbit:License "Creative Commons Attribution 4.0 International (CC BY 4.0)",
       rabbit:Acknowledgment "This research is supported by EPSRC under grant no. EP/K021699/1 which we gratefully acknowledge.",
       dc:creator "Heshan Du, University of Leeds",
       dc:date "April, 2016" """

    # Divide o arquivo pelas declarações principais (identificadas no início da linha)
    blocks = re.split(r'\n(?=[a-zA-Z0-9_]+:\s)', content)
    
    prefix_header = []
    fixed_blocks = []
    
    ann_regex = re.compile(r'Annotations:\s*(.*?)(?=\n\w+:|\Z)', re.DOTALL)

    for block in blocks:
        stripped_block = block.strip()
        if not stripped_block:
            continue
            
        if block.startswith('Prefix:'):
            prefix_header.append(block.strip())
            continue
            
        if block.startswith('Ontology:'):
            # Substitui as anotações antigas e quebradas do cabeçalho pelas unificadas
            ont_declaration = block.split('Annotations:')[0].strip()
            full_ontology_block = f"{ont_declaration}\n\n{header_annotations}"
            prefix_header.append(full_ontology_block)
            continue
        
        entity_declaration = block.split('\n')[0]
        
        # Coleta e limpa todas as linhas de anotação do bloco
        found_annotations = ann_regex.findall(block)
        clean_annotations = []
        
        for ann_block in found_annotations:
            items = [item.strip() for item in ann_block.split('\n') if item.strip()]
            for item in items:
                clean_item = re.sub(r',\s*$', '', item)
                if clean_item and not clean_item.startswith('Annotations:'):
                    clean_annotations.append(clean_item)

        cleaned_block = ann_regex.sub('', block)
        
        body_lines = []
        for line in cleaned_block.split('\n')[1:]:
            line_str = line.strip()
            if line_str and not line_str.startswith('rabbit:') and not line_str.startswith('dc:') and not line_str.startswith('owl:') and not any(line_str.startswith(k) for k in ["Class:", "ObjectProperty:", "DataProperty:", "Individual:", "AnnotationProperty:"]):
                body_lines.append(line)

        new_block_lines = [entity_declaration]
        
        if clean_annotations:
            new_block_lines.append("       Annotations:")
            for i, ann in enumerate(clean_annotations):
                if i < len(clean_annotations) - 1:
                    new_block_lines.append(f"              {ann},")
                else:
                    new_block_lines.append(f"              {ann}")
        
        new_block_lines.extend(body_lines)
        fixed_blocks.append("\n".join(new_block_lines))

    # Declaração das AnnotationProperty no topo
    annotation_declarations = ["\nAnnotationProperty: dc:creator", "AnnotationProperty: dc:date", "AnnotationProperty: owl:versionInfo", "AnnotationProperty: rabbit:Scope", "AnnotationProperty: rabbit:Purpose", "AnnotationProperty: rabbit:KnowledgeSource", "AnnotationProperty: rabbit:License", "AnnotationProperty: rabbit:Description", "AnnotationProperty: rabbit:Acknowledgment"]

    # Monta a saída final
    final_output = "\n\n".join(prefix_header) + "\n\n" + "\n".join(annotation_declarations) + "\n\n\n" + "\n\n".join(fixed_blocks)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_output)

    print(f"Arquivo de ontologia reestruturado com sucesso! Salvo em: {output_path}")

# --- EXECUÇÃO ---
arquivo_original = "Soil-Property-Process.owl"
arquivo_corrigido = "Soil-Property-Process-CLEANED.owl"

if os.path.exists(arquivo_original):
    full_fix_manchester(arquivo_original, arquivo_corrigido)
else:
    print(f"Erro: O arquivo {arquivo_original} não foi encontrado.")