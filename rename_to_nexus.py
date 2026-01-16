import os
import glob

# Encontrar todos os arquivos HTML
files = glob.glob('templates/**/*.html', recursive=True)

for filepath in files:
    try:
        # Ler conteúdo
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Substituir
        new_content = content.replace('- CSHub', '- Nexus').replace('- GRSHub', '- Nexus')
        
        # Escrever de volta
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f'Updated: {filepath}')
    except Exception as e:
        print(f'Error with {filepath}: {e}')

print('Done!')
