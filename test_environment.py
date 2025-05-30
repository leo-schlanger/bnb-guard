#!/usr/bin/env python3
"""
Script de Teste do Ambiente BNBGuard
Verifica se todas as dependências e configurações estão funcionando.
"""

import sys
import traceback

def test_imports():
    """Testa as importações principais."""
    print("🧪 TESTANDO IMPORTAÇÕES")
    print("=" * 50)
    
    tests = [
        ("fastapi", "FastAPI framework"),
        ("pydantic", "Pydantic validation"),
        ("pydantic_settings", "Pydantic Settings"),
        ("uvicorn", "ASGI server"),
        ("httpx", "HTTP client"),
        ("requests", "HTTP requests"),
        ("loguru", "Logging"),
        ("dotenv", "Environment variables"),
    ]
    
    success_count = 0
    for module, description in tests:
        try:
            __import__(module)
            print(f"✅ {description}")
            success_count += 1
        except ImportError as e:
            print(f"❌ {description}: {str(e)}")
    
    print(f"\n📊 Importações: {success_count}/{len(tests)} bem-sucedidas")
    return success_count == len(tests)

def test_configuration():
    """Testa se a configuração carrega corretamente."""
    print("\n⚙️ TESTANDO CONFIGURAÇÃO")
    print("=" * 50)
    
    try:
        from app.core.config import settings
        print(f"✅ Configuração carregada")
        print(f"   - API Title: {settings.API_TITLE}")
        print(f"   - API Port: {settings.API_PORT}")
        print(f"   - Log Level: {settings.LOG_LEVEL}")
        print(f"   - CORS Origins: {settings.CORS_ORIGINS}")
        return True
    except Exception as e:
        print(f"❌ Erro na configuração: {str(e)}")
        traceback.print_exc()
        return False

def test_application():
    """Testa se a aplicação principal carrega."""
    print("\n🚀 TESTANDO APLICAÇÃO")
    print("=" * 50)
    
    try:
        from app.main import app
        print("✅ Aplicação FastAPI carregada")
        print(f"   - Tipo: {type(app)}")
        return True
    except Exception as e:
        print(f"❌ Erro na aplicação: {str(e)}")
        traceback.print_exc()
        return False

def test_basic_functionality():
    """Testa funcionalidades básicas."""
    print("\n🔧 TESTANDO FUNCIONALIDADES BÁSICAS")
    print("=" * 50)
    
    try:
        # Teste de logging
        from loguru import logger
        logger.info("Teste de logging")
        print("✅ Logging system working")
        
        # Teste de HTTP client
        import httpx
        print("✅ Cliente HTTP disponível")
        
        # Teste de validação
        from pydantic import BaseModel
        
        class TestModel(BaseModel):
            name: str
            value: int
        
        test_obj = TestModel(name="test", value=42)
        print("✅ Validação Pydantic funcionando")
        
        return True
    except Exception as e:
        print(f"❌ Erro nas funcionalidades: {str(e)}")
        traceback.print_exc()
        return False

def main():
    """Main test function."""
    print("🧪 TESTE DO AMBIENTE BNBGUARD")
    print("=" * 60)
    print("📋 Verificando se o ambiente está configurado corretamente")
    print()
    
    # Verificar Python
    version = sys.version_info
    print(f"🐍 Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print("❌ Python 3.9+ é necessário!")
        return False
    
    # Executar testes
    tests = [
        test_imports,
        test_configuration,
        test_application,
        test_basic_functionality
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Erro no teste: {str(e)}")
            results.append(False)
    
    # Resultado final
    success_count = sum(results)
    total_tests = len(results)
    
    print("\n" + "=" * 60)
    if success_count == total_tests:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("\n✅ O ambiente está configurado corretamente")
        print("\n📋 PRÓXIMOS PASSOS:")
        print("1. Execute: python main.py")
        print("2. Acesse: http://localhost:3000/docs")
        print("3. Configure sua BSCSCAN_API_KEY no arquivo .env")
        return True
    else:
        print(f"⚠️ {success_count}/{total_tests} TESTES PASSARAM")
        print("\n❌ Alguns problemas foram encontrados")
        print("Verifique os erros acima e execute novamente")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 