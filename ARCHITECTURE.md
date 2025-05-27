# 🏗️ BNBGuard Architecture Documentation

## 📋 Overview

BNBGuard implements a clean, modular architecture that separates **simple analysis** (for end users) from **comprehensive audits** (for developers), with distinct endpoints for tokens and pools.

## 🎯 Architecture Goals

### ✅ Simple Analysis (`/analysis`)
- **Target Audience**: End users, wallets, bots, apps
- **Focus**: Essential information for quick decisions
- **Response Time**: Fast response (< 10 seconds)
- **Format**: User-friendly, simple scores, clear recommendations

### 🔍 Comprehensive Audits (`/audits`)
- **Target Audience**: Developers, researchers, analysts
- **Focus**: Complete technical analysis and improvement recommendations
- **Response Time**: Deep analysis (up to 45 seconds)
- **Format**: Technical, detailed metrics, improvement points

## 🛠️ API Structure

### 📊 Simple Analysis - `/api/v1/analysis`

#### 🪙 Tokens
```
GET /api/v1/analysis/tokens/{address}
GET /api/v1/analysis/tokens/{address}/quick
POST /api/v1/analysis/tokens/batch
```

**Returns:**
- Security score (0-100)
- Risk level (LOW/MEDIUM/HIGH/CRITICAL)
- Quick checks (honeypot, high fees, etc.)
- Simple recommendation
- Basic token information

#### 🏊 Pools
```
GET /api/v1/analysis/pools/{address}
GET /api/v1/analysis/pools/{address}/quick
POST /api/v1/analysis/pools/batch
```

**Returns:**
- Security score (0-100)
- Liquidity in USD
- Rug pull risk
- Liquidity lock status
- LP recommendation

### 🔬 Comprehensive Audits - `/api/v1/audits`

#### 🪙 Tokens
```
GET /api/v1/audits/tokens/{address}
GET /api/v1/audits/tokens/{address}/security
GET /api/v1/audits/tokens/{address}/recommendations
POST /api/v1/audits/tokens/compare
```

**Returns:**
- Complete security analysis
- Categorized vulnerabilities
- Detailed code analysis
- Improvement recommendations
- Advanced technical metrics

#### 🏊 Pools
```
GET /api/v1/audits/pools/{address}
GET /api/v1/audits/pools/{address}/liquidity
GET /api/v1/audits/pools/{address}/economics
POST /api/v1/audits/pools/compare
```

**Returns:**
- Complete liquidity analysis
- Economic evaluation (APR/APY, IL)
- Technical market analysis
- Optimization recommendations
- Efficiency metrics

## 🎨 Use Cases

### 📱 For Wallets and Apps
```javascript
// Quick check before transaction
const safety = await fetch('/api/v1/analysis/tokens/0x.../quick');
if (safety.risk_level === 'CRITICAL') {
  showWarning('⚠️ High-risk token!');
}
```

### 🤖 For Trading Bots
```python
# Batch analysis of multiple tokens
tokens = ['0x...', '0x...', '0x...']
results = await analyze_tokens_batch(tokens)
safe_tokens = [t for t in results if t.safety_score > 70]
```

### 🔧 For Developers
```javascript
// Complete audit for due diligence
const audit = await fetch('/api/v1/audits/tokens/0x...');
const recommendations = audit.recommendations.filter(r => r.priority === 'critical');
```

### 💰 For Liquidity Providers
```python
# Economic analysis of pool
pool_economics = await fetch('/api/v1/audits/pools/0x.../economics')
estimated_apr = pool_economics.fee_metrics.estimated_apr
il_risk = pool_economics.impermanent_loss_analysis.risk_level
```

## 📊 Response Comparison

### Simple Analysis (Token)
```json
{
  "status": "success",
  "safety_score": 75,
  "risk_level": "MEDIUM",
  "recommendation": "⚡ MODERATE RISK - Verify contract before large transactions",
  "token_info": {
    "name": "Example Token",
    "symbol": "EXT",
    "total_supply": "1000000000"
  },
  "quick_checks": {
    "honeypot": false,
    "high_fees": false,
    "verified_contract": true,
    "ownership_renounced": false
  },
  "critical_risks": [],
  "warnings": ["🔓 Ownership not renounced"],
  "analysis_duration_ms": 2500
}
```

### Comprehensive Audit (Token)
```json
{
  "status": "success",
  "security_assessment": {
    "overall_score": 72.5,
    "security_grade": "B",
    "component_scores": {
      "contract_security": 80,
      "ownership_analysis": 60,
      "tokenomics": 75,
      "functionality": 85
    }
  },
  "vulnerabilities": [
    {
      "type": "ownership_control",
      "severity": "medium",
      "description": "Owner has excessive control over contract",
      "impact": "Owner can modify critical parameters",
      "recommendation": "Implement timelock or renounce ownership"
    }
  ],
  "static_analysis": {
    "code_quality": {
      "complexity_score": 65,
      "documentation_score": 40,
      "best_practices_score": 70
    }
  },
  "recommendations": [
    {
      "category": "ownership",
      "priority": "high",
      "title": "Implement Ownership Controls",
      "description": "Current ownership structure poses risks",
      "implementation": "Add timelock contract or multi-sig",
      "impact": "Reduces centralization risk",
      "estimated_cost": "Medium"
    }
  ],
  "audit_info": {
    "duration_ms": 15750,
    "analysis_depth": "comprehensive",
    "confidence_level": "high"
  }
}
```

## 🔄 Service Architecture

### 1. Token Analysis Service
```python
# app/services/token_analysis_service.py
- Simple and fast analysis
- Safety score (0-100)
- Honeypot detection
- Basic security checks
```

### 2. Token Audit Service
```python
# app/services/token_audit_service.py
- Complete security audit
- Vulnerability analysis
- Technical recommendations
- Code quality metrics
```

### 3. Pool Analysis Service
```python
# app/services/pool_analysis_service.py
- Simple pool analysis
- Liquidity verification
- Rug pull risk assessment
- LP recommendations
```

### 4. Pool Audit Service
```python
# app/services/pool_audit_service.py
- Complete pool audit
- Economic analysis (APR/APY)
- Impermanent loss evaluation
- Efficiency metrics
```

## 🚀 Recommended Integrations

### 📱 Wallets
```javascript
// Verification before approving transaction
const quickCheck = await bnbguard.analysis.tokens.quick(tokenAddress);
if (quickCheck.safety_score < 50) {
  return showRiskWarning(quickCheck.recommendation);
}
```

### 🤖 Trading Bots
```python
# Security filter for tokens
async def is_token_safe(address):
    result = await bnbguard.analysis.tokens.quick(address)
    return result.safety_score > 70 and not result.is_honeypot
```

### 🌐 DeFi Apps
```javascript
// Pool analysis before providing liquidity
const poolAnalysis = await bnbguard.analysis.pools.get(poolAddress);
const riskWarnings = poolAnalysis.critical_risks;
if (riskWarnings.length > 0) {
  showPoolRisks(riskWarnings);
}
```

### 🔍 Audit Platforms
```python
# Complete audit for report
audit_result = await bnbguard.audits.tokens.comprehensive(token_address)
security_issues = audit_result.vulnerabilities
recommendations = audit_result.recommendations

# Generate audit report
generate_audit_report(audit_result)
```

## 📈 Performance Metrics

### Performance Targets
- **Simple Analysis**: < 10 seconds
- **Comprehensive Audits**: < 45 seconds
- **Quick Checks**: < 3 seconds
- **Batch Analysis**: < 30 seconds (10 tokens)

### Rate Limits
- **Analysis**: 100 requests/min
- **Audits**: 20 requests/min
- **Quick Checks**: 200 requests/min
- **Batch**: 10 requests/min

## 🛡️ Security and Reliability

### Input Validation
- ✅ Address validation
- ✅ Rate limiting
- ✅ Parameter sanitization
- ✅ Request timeouts

### Error Handling
- 🔄 Automatic retry for temporary failures
- 📝 Detailed error logging
- 🚨 Alerts for critical failures
- 📊 Availability metrics

## 🎯 Implementation Status

1. **Phase 1**: ✅ New architecture implementation
2. **Phase 2**: ✅ Testing and optimization
3. **Phase 3**: ✅ Legacy route removal
4. **Phase 4**: ✅ English documentation
5. **Phase 5**: 🚀 Production deployment

## 📞 Support

For questions about the architecture:
- 📖 Documentation: `/docs` and `/redoc`
- 🔍 Health Check: `/api/v1/analysis/health` and `/api/v1/audits/health`
- 🧪 Testing: Test endpoints available in development

---

**🎉 The new architecture offers complete flexibility for different use cases, from quick checks to comprehensive audits!** 