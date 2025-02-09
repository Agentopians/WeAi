# Week in Ethereum News AI Edition

[![ETH Global Hackathon](https://img.shields.io/badge/ETH%20Global-Hackathon-blue)](https://ethglobal.com)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

<p align="center">
  <img src="docs/weai169.jpg" alt="Week in Ethereum News AI Edition Logo" width="900">
</p>

> Continuing the legacy of Week in Ethereum News through AI innovation, with **Verifiable Agent Prompts and Agentic Operators**

## About

Week in Ethereum News AI Edition is a project developed during the ETH Global Agentic AI hackathon to continue the valuable service provided by Week in Ethereum News, which ceased operations at the end of 2024. The original "Week in Ethereum News" was distributed through a popular Substack page and email list, becoming a trusted source of information for the Ethereum community.  Our project aims to uphold and extend this legacy by using AI agents to curate, summarize, and deliver comprehensive weekly updates about the Ethereum ecosystem, including paid job postings from sponsors, but with a focus on **verifiability and transparency** powered by EigenLayer.

**Key Innovation: Verifiable Agent Prompts with Agentic Operators**

A core innovation of the Week in Ethereum News AI Edition is our **Verifiable Agent Prompts** system.  To ensure the trustworthiness and reliability of our AI-generated newsletter, we implement a novel approach leveraging:

*   **Agentic Operators:** A decentralized network of operators who participate in the verification process.
*   **Verification Agents (AI):** Each operator deploys a specialized AI agent, a "Verification Agent," to automatically assess and verify the instructions (prompts) given to our core newsletter generation agent.
*   **EigenLayer Autonomous Verifiable Service (AVS):** We utilize EigenLayer to create an AVS that manages the entire prompt verification workflow, ensuring cryptographic guarantees and on-chain transparency of the verification process.

This system ensures that the prompts guiding our AI content generation are **transparently and verifiably approved *before* content creation begins**, adding a crucial layer of quality control and accountability to our AI-driven newsletter.

## Features

- 🤖 **AI-Powered News Curation and Summarization:**  Leveraging advanced AI agents to efficiently gather and condense key information from across the Ethereum ecosystem.
- 📰 **Automated Weekly Newsletter Generation:**  End-to-end automation of the newsletter creation process, from content sourcing to final assembly and formatting.
- 💼 **Integrated Job Posting System for Sponsors:**  Seamlessly incorporates paid job listings from sponsors, providing value to both the community and project sustainability.
- 🔍 **Quality Control through Verifiable Agent Prompts and AI Moderation:**  Ensuring high-quality, relevant, and trustworthy content through our innovative Verifiable Agent Prompts system and additional AI moderation techniques.
- 📊 **Feedback-Driven Continuous Improvement:**  Implementing mechanisms to gather community feedback and continuously refine our AI agents and newsletter quality.

## Architecture

Our system is built upon a sophisticated multi-agent architecture, where specialized AI agents are responsible for distinct stages of the newsletter production pipeline.  A key component of our architecture is the **Verifiable Agent Prompt system**, designed for transparency and trustworthiness.

**Verifiable Agent Prompt System Components:**

*   **Newsletter Creator:**  Defines the **Agent Prompt** (the natural language instructions guiding the AI to generate the newsletter content) and a set of **Verification Policies** (rules and criteria that the prompt must satisfy).
*   **EigenLayer AVS Contract:** Smart contracts deployed as an EigenLayer AVS to manage the entire prompt verification workflow. This contract:
    *   Receives and stores Agent Prompts and Verification Policies.
    *   Coordinates the task distribution to Agentic Operators.
    *   Aggregates and records operator verdicts.
    *   Determines and immutably records the final on-chain **Verification Outcome** (Verified or Rejected).
*   **Agentic Operators:**  A network of independent entities (simulating EigenLayer operators) who participate in the AVS. Each operator:
    *   **Deploys a Verification Agent:** Runs specialized software (`prompt_operator.py` in our PoC) that embodies a **Verification Agent**.
    *   **Stakes Reputation (and potentially crypto-economic stake in a real EigenLayer deployment):** Operators are incentivized to deploy honest and policy-compliant Verification Agents to maintain their reputation and avoid potential penalties.
*   **Verification Agents (AI):**  Specialized AI agents run by each Agentic Operator. These agents are responsible for:
    *   **Automated Policy Checks:** Automatically analyzing Agent Prompts and evaluating them against the pre-defined Verification Policies. This involves techniques like keyword analysis, length checks, and potentially more advanced NLP methods.
    *   **Verdict Generation:** Based on the policy checks, each Verification Agent automatically generates a "Pass" or "Fail" verdict on the Agent Prompt.
    *   **Cryptographic Signing:**  Each Verification Agent cryptographically signs its verdict using the operator's BLS key, ensuring the verdict's authenticity and linking it to a specific operator.
*   **Aggregator:** A component within the EigenLayer AVS infrastructure (`aggregator.py` in our PoC) that:
    *   **Collects Operator Verdicts:** Gathers the signed "Pass/Fail" verdicts from the network of Verification Agents.
    *   **Aggregates Verdicts:** Implements a defined aggregation strategy (e.g., majority voting) to determine the overall consensus verdict on the Agent Prompt.
    *   **Submits Outcome to AVS Contract:**  Records the aggregated Verification Outcome (Verified or Rejected) on-chain, along with the cryptographic proof of operator attestations.
*   **Newsletter Generation Agent:**  Our core AI agent (the `manager` agent in our Autogen framework) responsible for orchestrating the newsletter creation process.  Crucially, this agent:
    *   **Executes Conditionally:** Only begins generating the newsletter content *after* the EigenLayer AVS has verifiably confirmed that its Agent Prompt has been "Verified."
    *   **Operates with Verified Instructions:**  Generates the newsletter strictly following the instructions provided in the AVS-verified Agent Prompt.

For a deeper dive into the roles and interactions of all agents within the broader newsletter generation system (beyond just the Verifiable Agent Prompt system), please see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Getting Started

### Prerequisites

- Python 3.9+
- Docker
- Access to required APIs (details in technical documentation)

### Installation

For detailed installation instructions, follow the [Installation Document](docs/INSTALLATION.md)

## Documentation

- [Vision Document](docs/VISION.md) - Project goals & value proposition
- [Architecture](docs/ARCHITECTURE.md) - System design and agent interactions
- [Technical Design](docs/TECHNICAL_DESIGN.md) - Technical implementation details
- [Features](docs/FEATURES.md) - Feature list and scope
- [Tasks](docs/TASKS.md) - Development roadmap and task breakdown

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details on how to help out.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Special thanks to Evan Van Ness and the original Week in Ethereum News team
- ETH Global hackathon organizers and mentors
- The Ethereum community for their support

## Contact

- Project Link: [https://github.com/yourusername/week-in-ethereum-news-ai](https://github.com/yourusername/week-in-ethereum-news-ai)
- Twitter: [@WeInEthNewsAI](https://twitter.com/WeInEthNewsAI)

---
Built with ❤️ for the Ethereum community
