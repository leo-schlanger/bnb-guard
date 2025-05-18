<p align="center">
  <img src="./assets/logo.png" alt="BNBGuard Logo" width="200"/>
</p>


<p align="center">
  🛡️ Automated Security for the BNB Smart Chain — detect risks before they detect you.
</p>

---

## 🚀 Overview

**BNBGuard** is a fully automated **security analysis platform** focused exclusively on the **BNB Smart Chain (BSC)**. It was created to protect investors, developers, and regular users from scams, malicious contracts, honeypots, and fraudulent tokens.

Every day, hundreds of new tokens are launched on the BSC—many with malicious intent and no audit whatsoever. BNBGuard addresses this problem by providing deep, accessible security analysis via browser extension or API.

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

### 👨‍💻 Bruno Weber — CEO
Experienced web and backend developer passionate about security and distributed systems. As CEO of BNBGuard, Bruno leads strategy, product vision, and ecosystem integrations to bring automated security to the BNB Chain.

- [LinkedIn](https://www.linkedin.com/in/brunolweber/)
- [GitHub](https://github.com/Bruno-Weber)

### 👨‍💻 Leo Schlanger — CTO
Full-stack developer with over 12 years of experience in software engineering. Specializes in automation, bots, smart contract integrations, and Web3 infrastructure. Leo is the technical mind behind BNBGuard, leading the development of its AI-based security engine.

- [LinkedIn](https://www.linkedin.com/in/leo-schlanger-226467192/)
- [GitHub](https://github.com/leo-schlanger)
  
  
---

## 📦 Local Installation (for developers)

```bash
git clone https://github.com/your-org/bnbguard.git
cd bnbguard
cp .env.example .env
# Add your BscScan API_KEY
uvicorn app.main:app
```

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

- [x] Static contract analysis
- [x] PancakeSwap simulation
- [x] Token risk scoring
- [ ] Browser extension
- [ ] AI agent integration
- [ ] PRO dashboard & alerts
- [ ] Auto LP/KYC verification

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