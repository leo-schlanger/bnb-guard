# 🚀 Coleção de Testes BNBGuard para Insomnia v2.0.0

Este arquivo contém uma coleção completa e organizada de testes para a API BNBGuard v2.0.0, pronta para ser importada no Insomnia REST Client.

## 🔧 PROBLEMAS CORRIGIDOS

### ✅ **Rotas de Batch Corrigidas**
- ❌ Formato antigo (quebrado): `{"token_addresses": ["0x...", "0x..."]}`
- ✅ Formato correto: `["0x...", "0x..."]`
- Limitações respeitadas: 10 tokens max, 5 pools max para análise, 5 tokens max e 3 pools max para comparação

### ✅ **Versão da API Atualizada**
- Atualizada para v2.0.0 (estava incorretamente marcada como v1.0.0)
- Swagger/OpenAPI agora reflete a versão correta

### ✅ **Endpoint de Teste de Logs**
- Marcado com aviso: só funciona com `ENV=development`
- Adicionadas instruções para verificar variável de ambiente

### ⚠️ **Comparação de Pools - Configuração de Timeout**
- **Problema identificado**: Comparação de pools pode levar até 90 segundos
- **Solução**: Configurar timeout no Insomnia para 120000ms (2 minutos)
- **Configuração**: Settings → Request/Response → Timeout: 120000ms
- **Status**: Rota funciona, requer configuração adequada de timeout

## 📂 Estrutura da Coleção

A coleção está organizada em 5 categorias principais:

### 1. 🏠 Root & Info
- **Informações da API v2.0.0**: Obtém metadados e estrutura da API
- **Documentação Swagger v2.0.0**: Acesso à documentação interativa

### 2. 🏥 Health Check
- **Health Check Básico**: Verifica status básico da API
- **Health Check Detalhado**: Status detalhado do sistema com informações de ambiente
- **Status dos Serviços Externos**: Monitora BSC Node e BscScan API
- **Status do Sistema de Logs**: Verifica funcionamento dos logs

### 3. 📊 Analysis (Usuários Finais)
Análises simples e rápidas para usuários finais:

#### 3.1 🪙 Tokens
- **Análise Simples de Token**: Análise completa com score de segurança
- **Verificação Rápida de Token**: Check ultra-rápido para bots e trading
- **Análise em Lote - Tokens (CORRIGIDO)**: Múltiplos tokens (máx 10) - formato correto

#### 3.2 🏊 Pools
- **Análise Simples de Pool**: Análise de segurança de pools de liquidez
- **Verificação Rápida de Pool**: Check rápido de pools
- **Análise em Lote - Pools (CORRIGIDO)**: Múltiplos pools (máx 5) - formato correto

### 4. 🔍 Audits (Desenvolvedores)
Auditorias técnicas completas para desenvolvedores:

#### 4.1 🪙 Token Audits
- **Auditoria Completa de Token**: Análise técnica detalhada
- **Auditoria de Segurança**: Foco em vulnerabilidades e riscos
- **Recomendações de Melhoria**: Sugestões de melhorias técnicas

#### 4.2 🏊 Pool Audits
- **Auditoria Completa de Pool**: Análise técnica detalhada do pool
- **Auditoria de Liquidez**: Análise específica de liquidez
- **Auditoria Econômica**: Análise de aspectos econômicos

#### 4.3 ⚖️ Comparações
- **Comparar Tokens (CORRIGIDO)**: Comparação lado a lado de múltiplos tokens (máx 5) - formato correto
- **Comparar Pools (CORRIGIDO)**: Comparação lado a lado de múltiplos pools (máx 3) - formato correto

### 5. 🐛 Debug (Desenvolvimento)
- **⚠️ Teste de Logs (ENV=development)**: Testa sistema de logs (apenas em desenvolvimento)

## 🔧 Como Importar

### Passo 1: Baixar o Arquivo
Salve o arquivo `insomnia_tests.json` em seu computador.

### Passo 2: Importar no Insomnia
1. Abra o Insomnia REST Client
2. Clique em **Create** > **Import From** > **File**
3. Selecione o arquivo `insomnia_tests.json`
4. A coleção será importada automaticamente

### Passo 3: Configurar Environment
A coleção já vem com variáveis de ambiente configuradas:

```json
{
  "base_url": "http://localhost:8000",
  "api_prefix": "/api/v1",
  "example_token": "0x55d398326f99059fF775485246999027B3197955",
  "example_pool": "0x16b9a82891338f9bA80E2D6970FddA79D1eb0daE"
}
```

## ⚙️ Configuração de Ambiente

### Para Desenvolvimento Local
```json
{
  "base_url": "http://localhost:8000",
  "api_prefix": "/api/v1"
}
```

### Para Staging
```json
{
  "base_url": "https://staging-api.bnbguard.com",
  "api_prefix": "/api/v1"
}
```

### Para Produção
```json
{
  "base_url": "https://api.bnbguard.com",
  "api_prefix": "/api/v1"
}
```

## 🧪 Casos de Teste Incluídos

### Tokens de Teste
- **USDT BSC**: `0x55d398326f99059fF775485246999027B3197955`
- **BUSD**: `0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56`
- **USDC**: `0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d`

### Pools de Teste
- **USDT/BNB**: `0x16b9a82891338f9bA80E2D6970FddA79D1eb0daE`
- **BUSD/BNB**: `0x58F876857a02D6762E0101bb5C46A8c1ED44Dc16`
- **USDC/BNB**: `0x7EFaEf62fDdCCa950418312c6C91Aef321375A00`

## 🚀 Fluxos de Teste Recomendados

### 1. Teste Inicial (Health Check)
```
1. Health Check Básico
2. Health Check Detalhado
3. Status dos Serviços Externos
```

### 2. Teste de Análise Simples
```
1. Análise Simples de Token
2. Verificação Rápida de Token
3. Análise Simples de Pool
4. Verificação Rápida de Pool
```

### 3. Teste de Auditoria Completa
```
1. Auditoria Completa de Token
2. Auditoria de Segurança
3. Auditoria Completa de Pool
4. Auditoria de Liquidez
```

### 4. Teste de Funcionalidades Avançadas (CORRIGIDAS)
```
1. Análise em Lote - Tokens (formato correto)
2. Análise em Lote - Pools (formato correto)
3. Comparar Tokens (formato correto)
4. Comparar Pools (formato correto)
```

## 📝 Notas Importantes

### ⚠️ **Formatos Corrigidos para Batch/Comparação**

**FORMATO CORRETO para todas as rotas batch/comparação:**
```json
[
  "0x55d398326f99059fF775485246999027B3197955",
  "0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56",
  "0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d"
]
```

**❌ FORMATO INCORRETO (não usar):**
```json
{
  "token_addresses": ["0x...", "0x..."]
}
```

### Limitações por Endpoint
- **Análise em Lote - Tokens**: Máximo 10 tokens
- **Análise em Lote - Pools**: Máximo 5 pools
- **Comparar Tokens**: Máximo 5 tokens
- **Comparar Pools**: Máximo 3 pools

### Headers Padrão
Todas as requisições incluem:
```
Accept: application/json
Content-Type: application/json (para POST requests)
```

### Variáveis Dinâmicas
- `{{ _.base_url }}`: URL base da API
- `{{ _.api_prefix }}`: Prefixo da API (/api/v1)
- `{{ _.example_token }}`: Token de exemplo para testes
- `{{ _.example_pool }}`: Pool de exemplo para testes

### Parâmetros Opcionais
Alguns endpoints têm parâmetros opcionais que vêm desabilitados por padrão. Você pode habilitá-los conforme necessário.

## 🔄 Atualizações

Para manter a coleção atualizada:
1. Baixe a versão mais recente do arquivo
2. Re-importe no Insomnia
3. As configurações de ambiente serão preservadas

## 🐛 Troubleshooting

### ⚠️ Endpoint de Teste de Logs (Erro 500)
**Problema**: O endpoint `/test-log` só funciona quando `ENV=development`

**Solução**:
1. Verificar se a variável de ambiente `ENV=development` está configurada
2. Se estiver em produção/staging, este endpoint retornará 404 (esperado)
3. Este endpoint é apenas para desenvolvimento e debug

### ⚠️ Comparação de Pools - Timeout
**Problema**: Comparação de pools falha por timeout ou não responde

**Soluções**:
1. **Configurar timeout adequado**: 120000ms (2 minutos) no Insomnia
2. **Testar pools individuais primeiro**: Use o request "🧪 Teste Pool Individual"
3. **Usar pools com alta liquidez**: USDT/BNB, BUSD/BNB do PancakeSwap
4. **Máximo 2-3 pools**: Não exceder limite de 3 pools por comparação

### Rotas de Batch/Comparação Quebradas
**Problema**: Rotas retornando erro 422 ou de validação

**Solução**:
1. ✅ Usar o formato correto: `["address1", "address2"]`
2. ❌ Não usar: `{"token_addresses": ["address1"]}`
3. Respeitar os limites máximos por endpoint

### API não responde
1. Verifique se a API está rodando na URL configurada
2. Teste primeiro o Health Check Básico
3. Verifique logs da aplicação

### Erro 404
1. Confirme se a `base_url` está correta
2. Verifique se o `api_prefix` está configurado corretamente
3. Consulte a documentação da API em `/docs`

### Erro de validação
1. Verifique se os endereços de tokens/pools são válidos
2. Confirme o formato dos dados enviados (especialmente batch/comparação)
3. Consulte os schemas na documentação

## 📊 Monitoramento

Use os endpoints de Health Check para monitorar:
- Status da API v2.0.0
- Performance dos serviços externos
- Estado do sistema de logs
- Métricas de uptime

## 🆕 Changelog v2.0.0

- ✅ Corrigido formato das rotas batch (analysis e audits)
- ✅ Corrigido formato das rotas de comparação
- ✅ Atualizada versão da API para v2.0.0
- ✅ Adicionados avisos para endpoint de teste de logs
- ✅ Documentados limites por endpoint
- ✅ Melhorada documentação de troubleshooting

---

**Dica**: Para uma experiência completa, mantenha tanto esta coleção quanto a documentação Swagger (`/docs`) abertas durante os testes! 