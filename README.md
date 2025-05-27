# 🛡️ BNBGuard API

**Automated risk analysis for BNB Chain tokens and pools**

[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](https://github.com/your-repo/bnbguard)
[![Python](https://img.shields.io/badge/python-3.11+-green.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-red.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

## 🎯 Overview

BNBGuard is a comprehensive API for analyzing the security and risk of tokens and liquidity pools on the BNB Smart Chain. It provides two distinct analysis modes:

- **🔍 Simple Analysis** - Quick safety checks for end users
- **🔬 Comprehensive Audits** - Detailed technical analysis for developers

## ✨ Features

### 🪙 Token Analysis
- **Honeypot Detection** - Identify tokens that prevent selling
- **Security Scoring** - 0-100 safety score with risk levels
- **Contract Verification** - Check if source code is verified
- **Ownership Analysis** - Detect dangerous ownership patterns
- **Fee Analysis** - Identify high trading fees

### 🏊 Pool Analysis
- **Liquidity Assessment** - Evaluate pool depth and stability
- **Rug Pull Detection** - Check for liquidity lock status
- **Economic Analysis** - Calculate APR/APY and impermanent loss
- **Market Health** - Assess trading patterns and volume

### 🚀 Advanced Features
- **Batch Processing** - Analyze multiple assets simultaneously
- **Comparative Analysis** - Side-by-side asset comparison
- **Real-time Data** - Live blockchain data integration
- **Structured Logging** - Comprehensive request tracking

## 🏗️ Architecture

### 📊 Analysis Endpoints (`/api/v1/analysis`)
**Target Audience:** End users, wallets, trading bots

```
GET  /api/v1/analysis/tokens/{address}        # Simple token analysis
GET  /api/v1/analysis/tokens/{address}/quick  # Ultra-fast safety check
POST /api/v1/analysis/tokens/batch            # Batch token analysis
GET  /api/v1/analysis/pools/{address}         # Simple pool analysis
GET  /api/v1/analysis/pools/{address}/quick   # Ultra-fast pool check
POST /api/v1/analysis/pools/batch             # Batch pool analysis
```

### 🔬 Audit Endpoints (`/api/v1/audits`)
**Target Audience:** Developers, security researchers, DeFi protocols

```
GET  /api/v1/audits/tokens/{address}                    # Comprehensive token audit
GET  /api/v1/audits/tokens/{address}/security           # Security-focused audit
GET  /api/v1/audits/tokens/{address}/recommendations    # Improvement suggestions
POST /api/v1/audits/tokens/compare                      # Token comparison
GET  /api/v1/audits/pools/{address}                     # Comprehensive pool audit
GET  /api/v1/audits/pools/{address}/liquidity           # Liquidity-focused audit
GET  /api/v1/audits/pools/{address}/economics           # Economic analysis
POST /api/v1/audits/pools/compare                       # Pool comparison
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js (for BSC interaction)
- Git

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/your-repo/bnbguard.git
cd bnbguard
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment**
```bash
cp env.example .env
# Edit .env with your configuration
```

4. **Run the server**
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

5. **Access the API**
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **API Root:** http://localhost:8000/

## 📖 Usage Examples

### 🔍 Simple Token Analysis
```javascript
// Quick safety check for wallets
const response = await fetch('/api/v1/analysis/tokens/0x.../quick');
const data = await response.json();

if (data.risk_level === 'CRITICAL') {
  alert('⚠️ High-risk token detected!');
}
```

### 🤖 Batch Analysis for Trading Bots
```python
import asyncio
import aiohttp

async def analyze_tokens(tokens):
    async with aiohttp.ClientSession() as session:
        async with session.post('/api/v1/analysis/tokens/batch', 
                               json=tokens) as response:
            return await response.json()

# Filter safe tokens
tokens = ['0x...', '0x...', '0x...']
results = await analyze_tokens(tokens)
safe_tokens = [t for t in results['results'] if t['safety_score'] > 70]
```

### 🔬 Comprehensive Security Audit
```javascript
// Detailed audit for developers
const audit = await fetch('/api/v1/audits/tokens/0x.../security');
const data = await audit.json();

const criticalIssues = data.critical_vulnerabilities;
const recommendations = data.security_recommendations;
```

### 💰 Pool Economic Analysis
```python
# Liquidity provider analysis
import requests

response = requests.get('/api/v1/audits/pools/0x.../economics')
data = response.json()

estimated_apr = data['fee_metrics']['estimated_apr']
il_risk = data['impermanent_loss_analysis']['risk_level']

print(f"Estimated APR: {estimated_apr}%")
print(f"Impermanent Loss Risk: {il_risk}")
```

## 📊 Response Examples

### Simple Analysis Response
```json
{
  "status": "success",
  "safety_score": 85,
  "risk_level": "LOW",
  "recommendation": "✅ RELATIVELY SAFE - Standard risks apply",
  "token_info": {
    "name": "Example Token",
    "symbol": "EXT",
    "verified": true
  },
  "quick_checks": {
    "honeypot": false,
    "high_fees": false,
    "ownership_renounced": true
  },
  "analysis_duration_ms": 2500
}
```

### Comprehensive Audit Response
```json
{
  "status": "success",
  "security_assessment": {
    "overall_score": 72.5,
    "security_grade": "B"
  },
  "vulnerabilities": [
    {
      "type": "ownership_control",
      "severity": "medium",
      "description": "Owner has excessive control",
      "recommendation": "Implement timelock or renounce ownership"
    }
  ],
  "recommendations": [
    {
      "category": "security",
      "priority": "high",
      "title": "Implement Ownership Controls",
      "implementation": "Add timelock contract or multi-sig"
    }
  ]
}
```

## 🔧 Configuration

### Environment Variables
```bash
# API Configuration
PORT=8000
HOST=0.0.0.0
LOG_LEVEL=INFO

# Blockchain Configuration
BSC_RPC_URL=https://bsc-dataseed.binance.org/
WEB3_TIMEOUT=30
MAX_RETRIES=3

# Rate Limiting
ANALYSIS_RATE_LIMIT=100  # requests per minute
AUDIT_RATE_LIMIT=20      # requests per minute
```

### Performance Targets
- **Quick Checks:** < 3 seconds
- **Simple Analysis:** < 10 seconds
- **Comprehensive Audits:** < 45 seconds
- **Batch Processing:** < 30 seconds (10 items)

## 🧪 Testing

### Run Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_analysis.py
```

### API Testing
```bash
# Test analysis endpoints
curl -X GET "http://localhost:8000/api/v1/analysis/tokens/0x.../quick"

# Test audit endpoints
curl -X GET "http://localhost:8000/api/v1/audits/tokens/0x..."

# Health check
curl -X GET "http://localhost:8000/api/v1/health"
```

## 🔌 Integration Examples

### Wallet Integration
```javascript
class BNBGuardWallet {
  async checkTokenSafety(tokenAddress) {
    const response = await fetch(`/api/v1/analysis/tokens/${tokenAddress}/quick`);
    const data = await response.json();
    
    return {
      isSafe: data.safety_score > 70,
      riskLevel: data.risk_level,
      recommendation: data.recommendation
    };
  }
}
```

### DeFi Protocol Integration
```solidity
// Smart contract integration example
interface IBNBGuard {
    function getTokenSafetyScore(address token) external view returns (uint256);
    function isPoolSafe(address pool) external view returns (bool);
}

contract SafeDeFi {
    IBNBGuard public bnbGuard;
    
    modifier onlySafeTokens(address token) {
        require(bnbGuard.getTokenSafetyScore(token) > 70, "Token not safe");
        _;
    }
}
```

## 📈 Monitoring & Logging

### Health Endpoints
```bash
# Analysis service health
GET /api/v1/analysis/health

# Audit service health  
GET /api/v1/audits/health

# Overall system health
GET /api/v1/health
```

### Logging Structure
```json
{
  "timestamp": "2025-05-27T20:00:00Z",
  "level": "INFO",
  "service": "token_analysis",
  "message": "Token analysis completed",
  "context": {
    "token_address": "0x...",
    "safety_score": 85,
    "duration_ms": 2500
  }
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run pre-commit hooks
pre-commit install

# Run linting
flake8 app/
black app/

# Run type checking
mypy app/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🧑‍💻 About Us

### 👨‍💻 Bruno Weber — Co-Founder & COO
Experienced web and backend developer passionate about security and distributed systems. As COO of BNBGuard, Bruno leads strategy, product vision, and ecosystem integrations to bring automated security to the BNB Chain.

- [LinkedIn](https://www.linkedin.com/in/brunolweber/)
- [GitHub](https://github.com/Bruno-Weber)

### 👨‍💻 Leo Schlanger — Co-Founder & CTO
Full-stack developer with over 12 years of experience in software engineering. Specializes in automation, bots, smart contract integrations, and Web3 infrastructure. Leo is the technical mind behind BNBGuard, leading the development of its AI-based security engine.

- [LinkedIn](https://www.linkedin.com/in/leo-schlanger-226467192/)
- [GitHub](https://github.com/leo-schlanger)
  

## 🙏 Acknowledgments

- **FastAPI** - Modern web framework
- **Web3.py** - Ethereum library
- **BSC** - Binance Smart Chain
- **Community** - Contributors and users

---

**⚡ Built with ❤️ for the DeFi community**
