import sys
import os
from pathlib import Path

# Adiciona o diretório raiz ao path do Python
root_dir = Path(__file__).parent.parent
app_dir = root_dir / 'app'

# Adiciona o diretório raiz e o diretório app ao path do Python
sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(app_dir))

# Carrega as variáveis de ambiente
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(root_dir, '.env'))

# Configura o ambiente de teste
os.environ['ENV'] = 'test'
