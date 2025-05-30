#!/usr/bin/env python3
"""
Teste de Metadados de Token
Valida que a busca de informações de token está funcionando corretamente.
"""

import json
import time
from app.core.utils.metadata import fetch_token_metadata

def test_known_token():
    """Testa com token conhecido (CAKE)."""
    print("🧪 TESTANDO METADADOS DE TOKEN")
    print("=" * 60)
    
    # Token CAKE (PancakeSwap)
    cake_address = "0x0E09FaBB73Bd3Ade0a17ECC321fD13a19e81cE82"
    
    print(f"🔍 Analisando token: {cake_address}")
    print("⏳ Buscando metadados...")
    
    start_time = time.time()
    
    try:
        metadata = fetch_token_metadata(cake_address)
        duration = time.time() - start_time
        
        print(f"✅ Metadados obtidos em {duration:.2f}s")
        print()
        
        # Verificar informações básicas
        print("📋 INFORMAÇÕES DO TOKEN:")
        print(f"   Nome: {metadata.get('name', 'N/A')}")
        print(f"   Símbolo: {metadata.get('symbol', 'N/A')}")
        print(f"   Decimais: {metadata.get('decimals', 'N/A')}")
        print(f"   Supply: {metadata.get('totalSupply', 'N/A')}")
        print(f"   Criador: {metadata.get('ContractCreator', 'N/A')}")
        print()
        
        # Verificar se não tem valores "Unknown"
        issues = []
        if metadata.get('name') == 'Unknown':
            issues.append("Nome está 'Unknown'")
        if metadata.get('symbol') == 'Unknown':
            issues.append("Símbolo está 'Unknown'")
        if metadata.get('ContractCreator') == 'Unknown':
            issues.append("Criador está 'Unknown'")
            
        if issues:
            print("❌ PROBLEMAS ENCONTRADOS:")
            for issue in issues:
                print(f"   - {issue}")
            return False
        else:
            print("✅ TODOS OS DADOS OBTIDOS CORRETAMENTE!")
            return True
            
    except Exception as e:
        print(f"❌ Erro ao buscar metadados: {str(e)}")
        return False

def test_token_analysis_response():
    """Testa se o formato de resposta está correto para análise."""
    print("\n🔬 TESTANDO FORMATO DE RESPOSTA PARA ANÁLISE")
    print("=" * 60)
    
    cake_address = "0x0E09FaBB73Bd3Ade0a17ECC321fD13a19e81cE82"
    
    try:
        metadata = fetch_token_metadata(cake_address)
        
        # Verificar se tem ambos os formatos (novo e legacy)
        has_new_format = all(key in metadata for key in ['name', 'symbol', 'decimals'])
        has_legacy_format = all(key in metadata for key in ['TokenName', 'TokenSymbol', 'Decimals'])
        
        print(f"✅ Formato novo (lowercase): {'Sim' if has_new_format else 'Não'}")
        print(f"✅ Formato legacy (capitalized): {'Sim' if has_legacy_format else 'Não'}")
        
        if has_new_format and has_legacy_format:
            print("✅ COMPATIBILIDADE TOTAL - ambos os formatos disponíveis!")
            return True
        else:
            print("❌ Compatibility issues detected")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return False

def main():
    """Main test function."""
    print("🚀 TESTE DE METADADOS DE TOKEN")
    print("=" * 60)
    print("📋 Verificando se o problema 'Unknown' foi resolvido")
    print()
    
    # Executar testes
    test1 = test_known_token()
    test2 = test_token_analysis_response()
    
    # Resultado final
    print("\n" + "=" * 60)
    if test1 and test2:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ O problema 'Unknown' foi RESOLVIDO!")
        print()
        print("📋 RESULTADO:")
        print("   - Metadados são obtidos corretamente da blockchain")
        print("   - Nome, símbolo e dados básicos funcionando")
        print("   - Criador do contrato sendo identificado")
        print("   - Compatibilidade com formatos antigo e novo")
        return True
    else:
        print("❌ ALGUNS TESTES FALHARAM")
        print("Verifique os erros acima")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 