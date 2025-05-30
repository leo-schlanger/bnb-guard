#!/usr/bin/env python3
"""
Script de Configuração do Ambiente BNBGuard
Resolve conflitos de dependências e configura o ambiente corretamente.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def run_command(command, description):
    """Executa um comando e exibe o progresso."""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - Concluído")
            return True
        else:
            print(f"❌ {description} - Erro:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ {description} - Exceção: {str(e)}")
        return False

def check_python_version():
    """Verifica se a versão do Python é compatível."""
    version = sys.version_info
    print(f"🐍 Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print("❌ Python 3.9+ é necessário!")
        return False
    
    print("✅ Versão do Python compatível")
    return True

def check_conda():
    """Verifica se o Conda está disponível."""
    try:
        result = subprocess.run("conda --version", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Conda disponível: {result.stdout.strip()}")
            return True
        else:
            print("❌ Conda não encontrado")
            return False
    except:
        print("❌ Conda não disponível")
        return False

def setup_conda_environment():
    """Configura o ambiente Conda."""
    print("\n🔄 CONFIGURANDO AMBIENTE CONDA")
    print("=" * 50)
    
    # Verificar se o ambiente já existe
    result = subprocess.run("conda env list", shell=True, capture_output=True, text=True)
    if "bnbguard" in result.stdout:
        print("⚠️ Ambiente 'bnbguard' já existe")
        response = input("Deseja recriar o ambiente? (s/N): ").lower()
        if response == 's':
            run_command("conda env remove -n bnbguard -y", "Removendo ambiente existente")
        else:
            print("📦 Usando ambiente existente")
            return True
    
    # Criar ambiente a partir do environment.yml
    if not run_command("conda env create -f environment.yml", "Criando ambiente Conda"):
        print("❌ Falha ao criar ambiente Conda")
        return False
    
    print("✅ Ambiente Conda configurado com sucesso!")
    print("📌 Para ativar o ambiente use: conda activate bnbguard")
    return True

def setup_pip_environment():
    """Configura o ambiente usando pip."""
    print("\n📦 CONFIGURANDO AMBIENTE PIP")
    print("=" * 50)
    
    # Atualizar pip
    if not run_command(f"{sys.executable} -m pip install --upgrade pip", "Atualizando pip"):
        print("⚠️ Falha ao atualizar pip")
    
    # Instalar dependências
    if not run_command(f"{sys.executable} -m pip install -r requirements.txt", "Instalando dependências"):
        print("❌ Falha ao instalar dependências")
        return False
    
    print("✅ Dependências instaladas com sucesso!")
    return True

def create_env_file():
    """Cria arquivo .env a partir do exemplo."""
    print("\n⚙️ CONFIGURANDO ARQUIVO .env")
    print("=" * 50)
    
    if Path(".env").exists():
        print("✅ Arquivo .env já existe")
        return True
    
    if Path("env.example").exists():
        try:
            with open("env.example", "r") as src:
                content = src.read()
            
            with open(".env", "w") as dst:
                dst.write(content)
            
            print("✅ Arquivo .env criado a partir do exemplo")
            print("⚠️ IMPORTANTE: Configure sua BSCSCAN_API_KEY no arquivo .env")
            return True
        except Exception as e:
            print(f"❌ Erro ao criar .env: {str(e)}")
            return False
    else:
        print("❌ Arquivo env.example não encontrado")
        return False

def resolve_package_conflicts():
    """Resolve conflitos comuns de pacotes."""
    print("\n🔧 RESOLVENDO CONFLITOS DE PACOTES")
    print("=" * 50)
    
    # Verificar conflitos comuns
    conflicts_resolved = 0
    
    # Conflito pydantic-settings
    try:
        import pydantic_settings
        print("✅ pydantic-settings importado com sucesso")
    except ImportError:
        if run_command(f"{sys.executable} -m pip install pydantic-settings==2.1.0", "Instalando pydantic-settings"):
            conflicts_resolved += 1
    
    # Conflito web3
    try:
        import web3
        print("✅ web3 importado com sucesso")
    except ImportError:
        if run_command(f"{sys.executable} -m pip install web3==6.15.1", "Instalando web3"):
            conflicts_resolved += 1
    
    # Conflito fastapi
    try:
        import fastapi
        print("✅ fastapi importado com sucesso")
    except ImportError:
        if run_command(f"{sys.executable} -m pip install fastapi==0.104.1", "Instalando fastapi"):
            conflicts_resolved += 1
    
    if conflicts_resolved > 0:
        print(f"✅ {conflicts_resolved} conflitos resolvidos")
    else:
        print("✅ No conflicts detected")
    
    return True

def test_imports():
    """Testa as importações principais."""
    print("\n🧪 TESTANDO IMPORTAÇÕES")
    print("=" * 50)
    
    imports_to_test = [
        ("fastapi", "FastAPI"),
        ("pydantic", "Pydantic"),
        ("web3", "Web3"),
        ("httpx", "HTTPX"),
        ("aiohttp", "aiohttp"),
        ("pytest", "pytest"),
    ]
    
    success_count = 0
    for module, name in imports_to_test:
        try:
            __import__(module)
            print(f"✅ {name}")
            success_count += 1
        except ImportError as e:
            print(f"❌ {name}: {str(e)}")
    
    print(f"\n📊 Importações: {success_count}/{len(imports_to_test)} bem-sucedidas")
    return success_count == len(imports_to_test)

def main():
    """Main script function."""
    print("🚀 CONFIGURAÇÃO DO AMBIENTE BNBGUARD")
    print("=" * 60)
    print("📋 Este script irá configurar o ambiente e resolver conflitos")
    print()
    
    # Verificar Python
    if not check_python_version():
        sys.exit(1)
    
    # Verificar se estamos no diretório correto
    if not Path("requirements.txt").exists():
        print("❌ Execute este script no diretório raiz do projeto BNBGuard")
        sys.exit(1)
    
    # Configurar ambiente
    has_conda = check_conda()
    
    if has_conda:
        print("\n🎯 OPÇÕES DE CONFIGURAÇÃO:")
        print("1. Usar Conda (recomendado)")
        print("2. Usar pip apenas")
        
        choice = input("\nEscolha uma opção (1-2): ").strip()
        
        if choice == "1":
            success = setup_conda_environment()
        else:
            success = setup_pip_environment()
    else:
        success = setup_pip_environment()
    
    if not success:
        print("\n❌ FALHA NA CONFIGURAÇÃO DO AMBIENTE")
        sys.exit(1)
    
    # Criar arquivo .env
    create_env_file()
    
    # Resolver conflitos
    resolve_package_conflicts()
    
    # Testar importações
    all_imports_ok = test_imports()
    
    # Resultado final
    print("\n" + "=" * 60)
    if all_imports_ok:
        print("🎉 CONFIGURAÇÃO CONCLUÍDA COM SUCESSO!")
        print("\n📋 PRÓXIMOS PASSOS:")
        if has_conda and input("Usou Conda? (s/N): ").lower() == 's':
            print("1. Ative o ambiente: conda activate bnbguard")
        print("2. Configure sua BSCSCAN_API_KEY no arquivo .env")
        print("3. Execute o projeto: python main.py")
        print("4. Teste a API: http://localhost:3000/docs")
    else:
        print("⚠️ CONFIGURAÇÃO CONCLUÍDA COM ALGUNS PROBLEMAS")
        print("Verifique os erros acima e execute novamente se necessário")
    
    print("\n💡 Para mais informações, consulte o README.md")

if __name__ == "__main__":
    main() 