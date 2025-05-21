<p align="center">
  <img src="./assets/logo.png" alt="BNBGuard Logo" width="200"/>
</p>


<p align="center">
  🛡️ Automated Security for the BNB Smart Chain — detect risks before they detect you.
</p>


## 🚀 Overview

**BNBGuard** is an automated security analysis platform focused exclusively on the **Binance Smart Chain (BSC)**. It was created to protect investors, developers, and regular users from scams, malicious contracts, honeypots, and fraudulent tokens.

Hundreds of new tokens are launched on BSC every day - many with malicious intent and no audit. BNBGuard addresses this issue by providing in-depth, accessible security analysis through a browser extension or API.

## 🛠️ Setup and Installation

### Prerequisites

- Python 3.8+
- Pip (Python package manager)
- BscScan API key (get it from [BscScan](https://bscscan.com/apis))

### Environment Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/leo-schlanger/bnb-guard.git
   cd bnb-guard
   ```

2. **Create and activate a virtual environment**
   ```bash
   # Linux/MacOS
   python -m venv venv
   source venv/bin/activate

   # Windows
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   - Copy `.env.example` to `.env`
   - Update variables as needed, especially `BSCSCAN_API_KEY`
   ```bash
   cp .env.example .env
   ```

### Running the Application

1. **Start the development server**
   ```bash
   uvicorn app.main:app --reload
   ```

2. **Access the interactive documentation**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Testing the API

You can test the endpoints using `curl` or tools like Postman/Insomnia:

```bash
# Token analysis
curl -X 'GET' \
  'http://localhost:8000/api/v1/analyze/0x0000000000000000000000000000000000000000' \
  -H 'accept: application/json'

# Token audit
curl -X 'GET' \
  'http://localhost:8000/api/v1/audit/0x0000000000000000000000000000000000000000' \
  -H 'accept: application/json'
```

## 🏗️ Project Structure

```
bnb-guard/
├── app/
│   ├── core/           # Core configurations and utilities
│   ├── models/         # Pydantic data models
│   ├── routes/         # API route definitions
│   ├── schemas/        # Request/response schemas
│   ├── services/       # Business logic and services
│   └── main.py         # Application entry point
├── tests/              # Automated tests
├── .env.example       # Environment variables example
├── requirements.txt    # Project dependencies
└── README.md          # Documentation
```

---

## 🎯 Purpose

- **Reduce financial losses** from scams and fraud.
- **Democratize security** with automated, understandable reports.
- **Strengthen the ecosystem** by empowering users and honest developers.

---

## ⚙️ How It Works

BNBGuard performs automated multi-layer analysis for newly created or user-submitted token contracts.

### 🔍 Metadata Collection
- Name, symbol, total supply
- Creator (deployer) address
- Deployment date and LP pair
- Verified source code via BscScan API

### 🧠 Static Analysis
- Detection of dangerous functions: `mint()`, `setFee()`, `pause()`, `blacklist()`
- Ownership renouncement check (`renounceOwnership()`)
- Abusive or modifiable buy/sell fees

### 🔄 Dynamic Analysis
- Real buy/sell simulation via PancakeSwap
- Honeypot detection
- Slippage manipulation and tax traps

### 🔗 On-Chain Analysis
- Deployer history (how many tokens created?)
- Token holder distribution
- Liquidity lock verification (LP lock)

### 📊 Risk Scoring
- Each red flag adds to a weighted score
- Final output: **Risk Score (0-100)** with visual warnings
- Verified projects may receive an audit NFT/SBT badge

---

## 🧩 Components

- **Browser extension** (like Wallet Guard)
- **Public/private API** for real-time security insights
- **PRO dashboard** with token monitoring and alerts
- **NFT/SBT Seal** for audited tokens
- **CLI script** for devs and integrators

---

## 💡 Core Values

- **Transparency:** traceable and auditable data
- **Accessibility:** security analysis for all users
- **Community-first:** promote good projects, block malicious intent
- **Innovation:** automation and AI where humans fall short

---

## 🧑‍💻 About Us

### 👨‍💻 Bruno Weber — Co-Founder & COO
Experienced web and backend developer passionate about security and distributed systems. As COO of BNBGuard, Bruno leads strategy, product vision, and ecosystem integrations to bring automated security to the BNB Chain.

- [LinkedIn](https://www.linkedin.com/in/brunolweber/)
- [GitHub](https://github.com/Bruno-Weber)

### 👨‍💻 Leo Schlanger — Co-Founder & CTO
Full-stack developer with over 12 years of experience in software engineering. Specializes in automation, bots, smart contract integrations, and Web3 infrastructure. Leo is the technical mind behind BNBGuard, leading the development of its AI-based security engine.

- [LinkedIn](https://www.linkedin.com/in/leo-schlanger-226467192/)
- [GitHub](https://github.com/leo-schlanger)
  
  
---

## 🔌 API Endpoints

| Method | Route       | Description                                 |
|--------|-------------|---------------------------------------------|
| POST   | `/analyze`  | Submits a token address for risk scoring    |
| POST   | `/audit`    | Detailed contract analysis & feedback       |

---

## 🧪 Running Tests

```bash
pytest --cov=.
```

---

## 📈 Roadmap

### ✅ Implemented Features
- [x] Core API infrastructure with FastAPI
- [x] Token metadata fetching and parsing
- [x] Static contract analysis
  - [x] Detection of dangerous functions
  - [x] Ownership and access control analysis
  - [x] Basic vulnerability detection
- [x] Dynamic analysis
  - [x] Buy/sell simulation
  - [x] Tax and fee analysis
  - [x] Honeypot detection
- [x] On-chain analysis
  - [x] Deployer history check
  - [x] Token holder distribution
  - [x] LP lock verification
- [x] Risk scoring system
  - [x] Weighted risk calculation
  - [x] Severity classification

### 🔄 In Progress
- [ ] Enhanced error handling and logging
- [ ] Rate limiting and API key management
- [ ] Comprehensive test coverage

### 📅 Planned Features
- [ ] Advanced pattern detection
  - [ ] Rug pull indicators
  - [ ] Token minting analysis
  - [ ] Fee manipulation detection
- [ ] Performance optimization
  - [ ] Caching mechanisms
  - [ ] Async processing
  - [ ] Batch processing support
- [ ] Enhanced security features
  - [ ] Input validation
  - [ ] Request signing
  - [ ] IP-based rate limiting
- [ ] Documentation
  - [ ] API reference
  - [ ] Integration guides
  - [ ] Example implementations

---

## 🤝 Contributing

Want to help secure the BNB ecosystem? Contributions are welcome!

1. Fork the repository
2. Create a feature branch: `feature/your-feature`
3. Submit a Pull Request 🚀

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for details.

---

<p align="center">
  Built with 💛 for BNB Chain — by devs who care about a safer ecosystem.
</p>
