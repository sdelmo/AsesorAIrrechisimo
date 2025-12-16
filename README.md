# El Asesor AIrrecho - AI Portfolio Manager

> A Streamlit-based portfolio management application powered by Claude AI, featuring a uniquely entertaining Venezuelan financial advisor personality that delivers professional-grade analysis with humor.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.31+-red.svg)](https://streamlit.io)
[![Claude AI](https://img.shields.io/badge/AI-Claude%20Sonnet%204-purple.svg)](https://www.anthropic.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Overview

This project started as a personalized Christmas gift for my dad - combining AI technology with financial portfolio management. What makes it unique is the custom AI personality system: a sarcastic but brilliant Venezuelan financial advisor who provides professional market analysis while keeping conversations engaging and memorable.

The application demonstrates advanced prompt engineering techniques to create a consistent, entertaining AI personality that never compromises on the quality of financial advice.

## Key Features

### **Conversational AI Advisor**
- Natural language portfolio analysis
- Real-time market research via web search
- Context-aware recommendations based on risk profile
- Maintains conversation history for coherent multi-turn dialogues

### **Portfolio Management**
- Track multiple asset types (ETFs, stocks, bonds, mutual funds)
- Visual asset allocation breakdown
- Calculate total portfolio value
- Export/import via CSV

### **Quick Analysis Tools**
- One-click risk assessment
- Sector diversification analysis
- Performance tracking
- Rebalancing recommendations
- Market outlook summaries

### **Custom AI Personality**
- Engineered system prompts for consistent character
- Venezuelan expressions and cultural references
- Sarcastic humor while maintaining analytical rigor
- Demonstrates advanced prompt engineering capabilities

## Quick Start

### Prerequisites
- Python 3.8 or higher
- Anthropic API key ([Get one here](https://console.anthropic.com/))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/sdelmo/AsesorAIrrechisimo.git
   cd portfolio-manager
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   streamlit run portfolio_manager.py
   ```

4. **Configure**
   - Open http://localhost:8501 in your browser
   - Enter your Anthropic API key in the sidebar
   - Set your risk profile
   - Start adding portfolio holdings!

## Example Interactions

### Portfolio Analysis
```
User: "How's my portfolio looking?"

Advisor: "Ey chamo, déjame ver tu portafolio...

Vale, tienes $32,500 invertidos. Tu diversificación está decente pana, 
60% acciones / 40% bonos. Para tu perfil conservador, eso está arrecho.

VTI está sólido (+0.9% hoy), AGG tranquilo como siempre, y AAPL subió 
1.5%. Después de sobrevivir la economía venezolana, esto me parece 
pan comido vale. Todo bien! 🏖️"
```

### Market Research
```
User: "Should I buy more AAPL?"

Advisor: "Coño chamo, déjame buscar esa vaina...

[searches web for current AAPL data]

Vale mira: AAPL está en $175.50 (subió 15% en 3 meses, arrecho!). 
Los analistas tienen precio objetivo de $200. PERO pana, ya tienes 
13.5% de tu portafolio en una sola acción.

Mi consejo: No compres más. Si quieres más tech, considera un ETF 
como QQQ para diversificar. No pongas todos los huevos en la misma 
cesta vale!"
```

## Architecture

### Tech Stack
- **Frontend**: Streamlit (Python-based web framework)
- **AI Engine**: Anthropic Claude Sonnet 4 (via API)
- **Data Processing**: Pandas
- **Web Search**: Anthropic's integrated web search tool
- **State Management**: Streamlit session state

### Key Components

```
portfolio_manager.py
├── Portfolio Data Management
│   ├── Add/remove holdings
│   ├── Calculate valuations
│   └── Export/import CSV
├── AI Integration
│   ├── Claude API client
│   ├── Custom system prompts
│   ├── Web search tool integration
│   └── Chat history management
└── UI Components
    ├── Chat interface
    ├── Portfolio management tab
    ├── Quick analysis buttons
    └── Risk profile configuration
```

### AI Prompt Engineering

The core innovation is the system prompt that creates a consistent AI personality:

**Key Techniques:**
- **Strict personality constraints**: Forces specific opening phrases and expressions
- **Cultural embedding**: Venezuelan references create authentic character
- **Structural requirements**: Mandates response format (greeting → humor → data → recommendation)
- **Tone enforcement**: Prohibits formal corporate language
- **Example-driven learning**: Multiple response templates ensure consistency

This demonstrates how careful prompt engineering can create a memorable user experience while maintaining professional functionality.

## Use Cases

- **Personal Finance**: Manage individual investment portfolios
- **Education**: Learn about investing through conversational AI
- **Portfolio Analysis**: Get quick insights on diversification and risk
- **Market Research**: Access real-time market data through natural language
- **AI Experimentation**: Study prompt engineering and personality systems

## Security & Privacy

- API keys stored only in session memory (never persisted to disk)
- Portfolio data remains local on user's machine
- No data transmitted except to Claude API for analysis
- `.gitignore` configured to prevent accidental key commits
- CSV export for user-controlled backups

## Cost Considerations

The application uses the Claude API which is pay-as-you-go:

**Typical Usage Costs:**
- Simple chat message: ~$0.01-0.02
- Portfolio analysis: ~$0.03-0.05
- Market research query: ~$0.02-0.04
- **Monthly (regular use)**: ~$3-8

Much more affordable than buying a beer for your buddy that knows all about finance.

## Learning Outcomes

This project demonstrates:

1. **AI Integration**: Working with modern LLM APIs
2. **Prompt Engineering**: Creating consistent AI personalities
3. **Full-Stack Development**: UI + Backend + AI in one application
4. **State Management**: Handling complex application state
5. **API Design**: Error handling, retries, tool use
6. **UX Design**: Making financial tools accessible and engaging
7. **Data Visualization**: Portfolio charts and metrics

## Configuration

### Adjusting AI Personality

The personality can be tuned by modifying the system prompt in `portfolio_manager.py` (lines ~59-220):

```python
# For more professional tone:
- Reduce Venezuelan expressions
- Remove comparisons to Venezuela
- Use formal greeting patterns

# For more humor:
- Increase cultural references
- Add more example responses
- Emphasize sarcastic elements
```

### API Settings

```python
# Adjust response length
max_tokens=4096  # Increase for longer responses

# Change AI model
model="claude-sonnet-4-20250514"  # Use latest model
```

## Contributing

Contributions are welcome! Areas for improvement:

- [ ] Add more asset types (crypto, commodities)
- [ ] Historical performance tracking
- [ ] Integration with broker APIs (auto-import holdings)
- [ ] Multiple portfolio support
- [ ] Tax-loss harvesting suggestions
- [ ] Benchmark comparisons (S&P 500, etc.)
- [ ] Mobile-responsive design improvements
- [ ] Additional AI personality options

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Anthropic's Claude AI](https://www.anthropic.com/)
- UI powered by [Streamlit](https://streamlit.io/)
- Inspired by the need for accessible, engaging financial tools
- Special thanks to my dad for being the inspiration and first user!

## My Contact Info

- GitHub: [@sdelmo](https://github.com/sdelmo)
- LinkedIn: [Me](https://linkedin.com/in/sebastian-a-delgado)
- Email: sebastian.adm0@gmail.com

## Why This Project?

Financial tools are often intimidating and boring. I wanted to create something that:
- Makes portfolio management **accessible** through natural conversation
- Proves AI can be **entertaining** while being useful
- Demonstrates that **good UX** can exist in finance
- Shows how **personality** enhances engagement without compromising quality
- My dad complains that he has no time to do research into these things, might as well make it accessible and fun.

The result is a tool my dad actually *enjoys* using to manage his investments - and that's the ultimate success metric.

---

**⭐ If you find this project interesting, please consider starring it!**

*Built with ❤️ and lots of coffee*