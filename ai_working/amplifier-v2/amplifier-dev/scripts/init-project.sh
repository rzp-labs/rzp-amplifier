#!/bin/bash
# Initialize a new Amplifier project

set -e

PROJECT_NAME="${1:-my-project}"

echo "Initializing Amplifier project: $PROJECT_NAME"
echo "==========================================="

# Create project directory
if [ -d "$PROJECT_NAME" ]; then
    echo "Error: Directory '$PROJECT_NAME' already exists"
    exit 1
fi

mkdir -p "$PROJECT_NAME"
cd "$PROJECT_NAME"

# Create project structure
mkdir -p .amplifier/transcripts
mkdir -p .amplifier/plugins
mkdir -p .amplifier/data

# Create default configuration
cat > .amplifier/config.toml << 'EOF'
# Amplifier Project Configuration

[session]
orchestrator = "loop-basic"
context = "context-simple"

[context.config]
max_tokens = 200_000
compact_threshold = 0.92

# Add your providers here
# [[providers]]
# module = "provider-anthropic"
# name = "anthropic"
# config = { api_key = "${ANTHROPIC_API_KEY}" }

# Basic tools
[[tools]]
module = "tool-filesystem"
config = { allowed_paths = ["."], require_approval = false }

# Add more configuration as needed
EOF

# Create README
cat > README.md << EOF
# $PROJECT_NAME

An Amplifier AI agent project.

## Setup

1. Set up your API keys:
\`\`\`bash
export ANTHROPIC_API_KEY="your-key"
export OPENAI_API_KEY="your-key"
\`\`\`

2. Configure providers in \`.amplifier/config.toml\`

3. Run Amplifier:
\`\`\`bash
amplifier chat
\`\`\`

## Project Structure

- \`.amplifier/\` - Configuration and data
  - \`config.toml\` - Project configuration
  - \`transcripts/\` - Conversation backups
  - \`plugins/\` - Project-specific plugins
  - \`data/\` - Project data

## Documentation

See the [Amplifier documentation](https://github.com/microsoft/amplifier) for more information.
EOF

# Create .gitignore
cat > .gitignore << 'EOF'
# Amplifier
.amplifier/transcripts/
.amplifier/data/
*.log

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv
.env

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db
EOF

# Create CLAUDE.md memory file
cat > CLAUDE.md << EOF
# Project: $PROJECT_NAME

## Overview
This is an Amplifier project initialized on $(date).

## Conventions
- Follow the project's coding standards
- Use clear, descriptive names
- Document important decisions
- Test before committing

## Project-Specific Information
Add project-specific context here that should persist across sessions.
EOF

echo ""
echo "✅ Project initialized successfully!"
echo ""
echo "Next steps:"
echo "1. cd $PROJECT_NAME"
echo "2. Edit .amplifier/config.toml to add your providers"
echo "3. Set your API keys as environment variables"
echo "4. Run: amplifier chat"
echo ""
echo "For more information, see README.md"
