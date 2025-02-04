# Contributing to Week in Ethereum News AI Edition

We're excited that you're interested in contributing to Week in Ethereum News AI Edition! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

## How to Contribute

### Reporting Issues

- Use the GitHub issue tracker
- Check if the issue already exists
- Include detailed description and steps to reproduce
- Add relevant labels

### Making Changes

1. Fork the repository
2. Create a new branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests
5. Commit your changes (`git commit -m 'feat: Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Pull Request Guidelines

- Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification
- Include tests for new features
- Update documentation as needed
- Ensure CI passes
- Link related issues

### Development Setup

```bash
# Clone your fork
git clone https://github.com/your-username/week-in-ethereum-news-ai.git

# Install dependencies
pip install -r requirements.txt

# Set up pre-commit hooks
pre-commit install
```

### Code Style

- Follow PEP 8 guidelines
- Use type hints
- Write meaningful commit messages
- Document your code

## Project Structure

```
.
├── agents/          # AI agent implementations
├── api/            # API endpoints
├── config/         # Configuration files
├── data/           # Data storage
├── docs/           # Documentation
├── tests/          # Test suite
└── utils/          # Utility functions
```

## Getting Help

- Join our Discord community
- Check the documentation
- Ask questions in GitHub Discussions

Thank you for contributing to Week in Ethereum News AI Edition!
# Code of Conduct

## Our Pledge

We as members, contributors, and leaders pledge to make participation in our
community a harassment-free experience for everyone, regardless of age, body
size, visible or invisible disability, ethnicity, sex characteristics, gender
identity and expression, level of experience, education, socio-economic status,
nationality, personal appearance, race, religion, or sexual identity
and orientation.

## Our Standards

Examples of behavior that contributes to a positive environment:

* Demonstrating empathy and kindness toward other people
* Being respectful of differing opinions, viewpoints, and experiences
* Giving and gracefully accepting constructive feedback
* Accepting responsibility and apologizing to those affected by our mistakes
* Focusing on what is best for the community

Examples of unacceptable behavior:

* The use of sexualized language or imagery
* Trolling, insulting or derogatory comments
* Personal or political attacks
* Public or private harassment
* Publishing others' private information without permission
* Other conduct which could reasonably be considered inappropriate

## Enforcement Responsibilities

Project maintainers are responsible for clarifying and enforcing standards of
acceptable behavior and will take appropriate and fair corrective action in
response to any behavior that they deem inappropriate, threatening, offensive,
or harmful.

## Enforcement

Violations of the Code of Conduct may be reported to the project team. All
complaints will be reviewed and investigated promptly and fairly.

## Attribution

This Code of Conduct is adapted from the [Contributor Covenant](https://www.contributor-covenant.org/),
version 2.0, available at
https://www.contributor-covenant.org/version/2/0/code_of_conduct.html.
MIT License

Copyright (c) 2025 Week in Ethereum News AI Edition

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
# API Keys
OPENAI_API_KEY=your_openai_api_key
PINECONE_API_KEY=your_pinecone_api_key
TWITTER_API_KEY=your_twitter_api_key
REDDIT_API_KEY=your_reddit_api_key
SENDGRID_API_KEY=your_sendgrid_api_key

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/weinethnews
REDIS_URL=redis://localhost:6379

# Service Configuration
ENVIRONMENT=development
LOG_LEVEL=INFO
PORT=8000

# Newsletter Configuration
NEWSLETTER_FREQUENCY=weekly
NEWSLETTER_SEND_DAY=friday
NEWSLETTER_SEND_TIME=09:00UTC

# Job Posting Configuration
MIN_JOB_POSTING_PRICE=100
JOB_POSTING_CURRENCY=USD

# AI Model Configuration
CONTENT_CURATION_MODEL=gpt-4
SUMMARIZATION_MODEL=gpt-4
MODERATION_MODEL=gpt-4
