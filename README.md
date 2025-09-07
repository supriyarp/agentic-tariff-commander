<<<<<<< HEAD
# ATIS - Agentic Tariff Intelligence System

A comprehensive demo application showcasing automated tariff impact analysis and supply chain optimization for automotive components.

## 🚀 Features

- **Real-time Tariff Monitoring**: Automated detection of tariff changes and regulatory updates
- **Supply Chain Optimization**: Multi-tier supplier analysis with cost, lead time, and compliance scoring
- **Duty-on-Duty Calculations**: Complex multi-border tariff scenarios and duty stacking analysis
- **HTS Classification Review**: Automated confidence scoring with human-in-the-loop approval
- **Policy-Driven Automation**: Business rule engine for automated decision making
- **Interactive Demo Interface**: Streamlit-based web application for scenario testing

## 📊 Data Overview

The system includes comprehensive synthetic data covering:

- **22 BOM Components** across 10 SKUs (brake systems, engines, transmissions, steering, glass, seating, batteries, wheels)
- **26 Suppliers** from 8 countries (China, Mexico, Germany, Vietnam, Thailand, India, Brazil, US)
- **16 Shipping Routes** including direct and multi-leg trade paths
- **29 Tariff Scenarios** with base rates, future increases, and USMCA preferences
- **15 Test Scenarios** for comprehensive analysis and demonstration

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- pip package manager

### Setup
```bash
# Clone the repository
git clone <your-repo-url>
cd atis_project

# Install dependencies
pip install -r requirements.txt

# Run the Streamlit application
streamlit run app_streamlit.py
```

## 🎯 Usage

### Local Development
1. Start the Streamlit app: `streamlit run app_streamlit.py`
2. Open your browser to `http://localhost:8501`
3. Select a scenario (1-3) and click "Run Watcher"
4. Review the automated decisions and compliance queue

### Demo Scenarios
- **Scenario 1**: CN auto parts tariff increase (+15pp to 25%)
- **Scenario 2**: Multi-border duty stacking (CN→VN→US)
- **Scenario 3**: HTS classification review (confidence < 0.90)

## 📁 Project Structure

```
atis_project/
├── app_streamlit.py          # Main Streamlit application
├── atis/                     # Core ATIS modules
│   ├── __init__.py
│   ├── cost_engine.py        # Cost calculation engine
│   ├── data_loader.py        # Data loading and management
│   ├── models.py             # Data models and schemas
│   ├── orchestrator.py       # Event handling and orchestration
│   ├── policy.py             # Business policy engine
│   ├── sourcing.py           # Supplier sourcing logic
│   ├── watcher.py            # Tariff monitoring system
│   └── watcher_demo.py       # Demo event simulation
├── data/                     # Sample data files
│   ├── bom.csv              # Bill of Materials
│   ├── suppliers.csv        # Supplier information
│   ├── routes.csv           # Shipping routes
│   ├── tariffs.csv          # Tariff rates
│   ├── scenarios.csv        # Test scenarios
│   └── policy.yaml          # Business rules
├── tests/                    # Unit tests
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🔧 Core Components

### Data Models
- **BOM**: Component specifications with HTS codes, suppliers, and costs
- **Suppliers**: Performance metrics including lead times, quality, and compliance scores
- **Routes**: Shipping paths with multi-leg support for duty-on-duty scenarios
- **Tariffs**: Rate structures with effective dates and country-specific rules
- **Scenarios**: Test cases for tariff impact analysis

### Business Logic
- **Policy Engine**: Automated decision making based on configurable thresholds
- **Cost Engine**: Comprehensive cost calculations including tariffs, logistics, and supplier costs
- **Sourcing Engine**: Multi-criteria supplier evaluation and optimization
- **Watcher System**: Real-time monitoring of regulatory changes

## 🌐 Deployment

### Streamlit Community Cloud
1. Push your code to a GitHub repository
2. Connect your GitHub account to Streamlit Community Cloud
3. Deploy directly from the repository
4. The app will be available at `https://your-app-name.streamlit.app`

### Local Deployment
```bash
# Run with custom port
streamlit run app_streamlit.py --server.port 8501

# Run in headless mode
streamlit run app_streamlit.py --server.headless true
```

## 🧪 Testing

Run the test suite:
```bash
pytest tests/
```

## 📈 Key Metrics

The system tracks and optimizes:
- **Cost Impact**: Tariff effects on total landed cost
- **Lead Time**: Supplier and logistics timing
- **Compliance Risk**: Regulatory and quality scores
- **Margin Impact**: Business impact analysis
- **Supplier Risk**: Diversification and dependency analysis

## 🔍 Example Analysis

### Multi-Border Scenario (CN→VN→US)
- **Base Route**: CN→US (10% tariff)
- **Alternative Route**: CN→VN→US (3% + 5% = 8% total)
- **Savings**: 2% tariff reduction
- **Trade-offs**: Additional lead time and complexity

### USMCA Optimization
- **CN Supplier**: 6.5% tariff on transmission parts
- **MX Supplier**: 0% tariff under USMCA
- **Decision**: Automatic preference for MX supplier

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For questions or issues:
- Create an issue in the GitHub repository
- Check the documentation in the `docs/` folder
- Review the test cases for usage examples

---

**Built for WWC Conference Demo** - Showcasing advanced supply chain intelligence and automated tariff optimization.
=======
# agentic-tariff-commander
>>>>>>> origin/dev
