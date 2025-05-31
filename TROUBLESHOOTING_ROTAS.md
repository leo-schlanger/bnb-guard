# 🔧 Troubleshooting - Rotas com Problemas BNBGuard API

## 📊 Status dos Testes (Porta 8000)

### ✅ **ROTAS FUNCIONANDO CORRETAMENTE**
- `GET /` - Informações da API ✅
- `GET /api/v1/health` - Health check básico ✅  
- `GET /api/v1/analysis/health` - Health analysis ✅
- `GET /api/v1/audits/health` - Health audits ✅
- `GET /api/v1/analysis/tokens/{address}` - Análise individual ✅
- `POST /api/v1/analysis/tokens/batch` - Batch tokens (formato correto) ✅
- `POST /api/v1/audits/tokens/compare` - **COMPARAÇÃO DE TOKENS FUNCIONANDO** ✅

### ❌ **ROTAS COM PROBLEMAS IDENTIFICADOS**
- `GET /test-log` - **ERRO 500** 🚨 (corrigido, aguarda restart)
- `POST /api/v1/audits/pools/compare` - **PROBLEMAS NO INSOMNIA** ⚠️

---

## 🚨 **PROBLEMAS IDENTIFICADOS**

### **1. Endpoint `/test-log` - ERRO 500**
**Status**: ⚠️ **CORRIGIDO NO CÓDIGO - REQUER RESTART DA API**

### **2. Comparação de Pools no Insomnia**
**Problema**: A rota `POST /api/v1/audits/pools/compare` existe no código mas apresenta problemas no Insomnia.

**Possíveis Causas**:
1. **Timeout**: Comparação de pools é mais lenta (pode levar até 90s)
2. **Formato de endereços**: Pools podem precisar de endereços específicos
3. **Limitações da API**: Máximo 3 pools por comparação
4. **Problemas de conectividade**: Terminal PowerShell instável

**Evidências**:
- ✅ Rota existe no código (`app/routes/audits.py` linha 614)
- ✅ Comparação de tokens funciona perfeitamente
- ✅ Formato JSON correto: `["0x...", "0x..."]`
- ❓ Teste via terminal PowerShell falhou

---

## 🔄 **AÇÕES NECESSÁRIAS**

### **1. REINICIAR A API** 
```bash
# Parar a API atual
Ctrl+C (ou fechar o terminal)

# Reiniciar a API
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### **2. TESTAR COMPARAÇÕES APÓS RESTART**
```powershell
# Testar comparação de tokens (já funcionando)
$body = '["0x55d398326f99059fF775485246999027B3197955", "0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56"]'
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/audits/tokens/compare" -Method POST -ContentType "application/json" -Body $body

# Testar comparação de pools (investigar)
$bodyPools = '["0x16b9a82891338f9bA80E2D6970FddA79D1eb0daE", "0x58F876857a02D6762E0101bb5C46A8c1ED44Dc16"]'
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/audits/pools/compare" -Method POST -ContentType "application/json" -Body $bodyPools
```

---

## 🧪 **STATUS DETALHADO DOS TESTES**

### **Fase 1: Health Checks** ✅
1. `GET /` ✅ (funcionando)
2. `GET /api/v1/health` ✅ (funcionando)
3. `GET /api/v1/analysis/health` ✅ (funcionando)
4. `GET /api/v1/audits/health` ✅ (funcionando)

### **Fase 2: Análise Individual** ✅
1. `GET /api/v1/analysis/tokens/{valid_address}` ✅ (funcionando)
2. `GET /api/v1/analysis/tokens/{valid_address}/quick` ⏳ (não testado)
3. `GET /api/v1/analysis/pools/{valid_address}` ⏳ (não testado)
4. `GET /api/v1/analysis/pools/{valid_address}/quick` ⏳ (não testado)

### **Fase 3: Análise Batch** ✅
1. `POST /api/v1/analysis/tokens/batch` ✅ (funcionando)
2. `POST /api/v1/analysis/pools/batch` ⏳ (não testado)

### **Fase 4: Auditorias** ⏳
1. `GET /api/v1/audits/tokens/{address}` ⏳ (não testado)
2. `GET /api/v1/audits/tokens/{address}/security` ⏳ (não testado)
3. `GET /api/v1/audits/pools/{address}` ⏳ (não testado)

### **Fase 5: Comparações** ⚠️
1. `POST /api/v1/audits/tokens/compare` ✅ (funcionando!)
2. `POST /api/v1/audits/pools/compare` ❌ (problemática no Insomnia)

### **Fase 6: Debug** ❌
1. `GET /test-log` ❌ (erro 500, corrigido no código)

---

## 🔍 **ANÁLISE ESPECÍFICA: COMPARAÇÃO DE POOLS**

### **Limitações da Rota** (conforme código)
- **Máximo**: 3 pools por comparação
- **Timeout**: Até 90 segundos (mais lento que tokens)
- **Formato**: Array JSON direto `["0x...", "0x..."]`
- **Pools válidos**: Devem existir na BSC e ter liquidez

### **Pools de Teste Recomendados** (com maior liquidez)
```json
[
  "0x16b9a82891338f9bA80E2D6970FddA79D1eb0daE",  // USDT/BNB (PancakeSwap)
  "0x58F876857a02D6762E0101bb5C46A8c1ED44Dc16"   // BUSD/BNB (PancakeSwap)
]
```

### **Possíveis Problemas no Insomnia**
1. **Timeout configurado muito baixo** (< 90s)
2. **Request sendo cortado pelo PowerShell**
3. **Problema de codificação de caracteres**
4. **Endereços de pools inválidos ou sem liquidez**

---

## 📝 **COMANDOS DE TESTE WINDOWS POWERSHELL**

### **Comparação de Tokens (Funcionando)**:
```powershell
$body = '["0x55d398326f99059fF775485246999027B3197955", "0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56"]'
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/audits/tokens/compare" -Method POST -ContentType "application/json" -Body $body
```

### **Comparação de Pools (Problemática)**:
```powershell
# Teste 1: Com timeout estendido
$body = '["0x16b9a82891338f9bA80E2D6970FddA79D1eb0daE", "0x58F876857a02D6762E0101bb5C46A8c1ED44Dc16"]'
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/audits/pools/compare" -Method POST -ContentType "application/json" -Body $body -TimeoutSec 120

# Teste 2: Apenas um pool (para debug)
$body = '["0x16b9a82891338f9bA80E2D6970FddA79D1eb0daE"]'
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/audits/pools/compare" -Method POST -ContentType "application/json" -Body $body
```

---

## 🛠️ **CORREÇÕES PARA INSOMNIA**

### **1. Configurar Timeout Adequado**
- No Insomnia: Settings → Request/Response → Timeout: 120000ms (2 minutos)

### **2. Testar Pools Individuais Primeiro**
- Testar `GET /api/v1/audits/pools/{address}` antes da comparação
- Verificar se os endereços de pools são válidos

### **3. Usar Pools com Alta Liquidez**
- USDT/BNB: `0x16b9a82891338f9bA80E2D6970FddA79D1eb0daE`
- BUSD/BNB: `0x58F876857a02D6762E0101bb5C46A8c1ED44Dc16`
- ETH/BNB: `0x74E4716E431f45807DCF19f284c7aA99F18a4fbc`

---

## ⚡ **RESUMO EXECUTIVO ATUALIZADO**

| Status | Descrição | Ação |
|--------|-----------|------- |
| ✅ | API funcionando na porta 8000 | Nenhuma |
| ✅ | Health checks operacionais | Nenhuma |
| ✅ | Análises individuais funcionando | Nenhuma |
| ✅ | Batch analysis funcionando | Nenhuma |
| ✅ | **Comparação de tokens funcionando** | **Confirmado!** |
| ⚠️ | Endpoint /test-log com erro 500 | **RESTART NECESSÁRIO** |
| ❌ | **Comparação de pools problemática** | **Investigar timeout/endereços** |
| ❓ | Outras rotas não testadas | Testar após restart |

---

## 📞 **PRÓXIMOS PASSOS PRIORITÁRIOS**

1. **REINICIAR** a API para aplicar correções no test-log
2. **CONFIGURAR** timeout adequado no Insomnia (120s)
3. **TESTAR** comparação de pools com timeout estendido
4. **VALIDAR** endereços de pools individuais antes da comparação
5. **DOCUMENTAR** novos problemas encontrados

---

*Última atualização: 31/05/2025 - 23:00*
*Status: Comparação de tokens ✅ | Comparação de pools ❌ | Test-log pendente restart* 