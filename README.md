# Notion MCP - Enhanced Notion Integration for AI Assistants

A powerful Model Context Protocol (MCP) implementation that enables AI assistants to interact with your Notion workspace through function calling.

## 🚀 Features

- **Database Operations** - Create, query, update, and list databases
- **Page Management** - Create, retrieve, update, and search pages
- **Block Operations** - Get, update, and append content blocks
- **Rich Content Support** - Work with various Notion block types
- **Robust Error Handling** - Detailed error messages with troubleshooting guidance
- **Type-Safe Implementation** - Built with Pydantic models for reliability

## 📋 Prerequisites

- Python 3.10 or higher
- A Notion integration with appropriate capabilities
- Notion API key

## 🔧 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Sjotie/notion-mcp.git
   cd notion-mcp
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv-notion
   ```

3. Activate the virtual environment:
   - Windows: `.venv-notion\Scripts\activate`
   - macOS/Linux: `source .venv-notion/bin/activate`

4. Install dependencies:
   ```bash
   pip install -e .
   ```

5. Create a `.env` file in the project root with your Notion API key:
   ```
   NOTION_API_KEY=your_notion_integration_token
   ```

## 🔌 Integration with Claude Desktop

To use with Claude Desktop, update your `claude_desktop_config.json` file:

```json
"notion-mcp": {
    "command": "C:\\path\\to\\notion-mcp\\.venv-notion\\Scripts\\python", 
    "args": ["-m", "notion_mcp"],
    "cwd": "C:\\path\\to\\notion-mcp"
}
```

Adjust the paths according to your system:
- Windows: `.venv-notion\\Scripts\\python`
- macOS/Linux: `.venv-notion/bin/python`

## 🛠️ Available Tools

| Tool | Description |
|------|-------------|
| `list_databases` | List all accessible Notion databases |
| `query_database` | Query items from a database with filtering and sorting |
| `create_database` | Create a new database with custom schema |
| `update_database` | Update a database's title, description, or schema |
| `create_page` | Create a new page in a database with properties and content |
| `update_page` | Update a page's properties or archive status |
| `get_page` | Retrieve a specific page by ID |
| `get_page_content` | Retrieve the content blocks of a page |
| `append_page_content` | Add content blocks to a page or block |
| `get_block` | Retrieve a specific block by ID |
| `update_block` | Update a block's content or archive status |
| `search` | Search for pages or databases by title or content |

## 🧪 Testing

To verify the server is running correctly:

```bash
python -m notion_mcp
```

The server should start without errors and be ready to accept connections.

## 📁 Project Structure

```
notion-mcp/
├── src/
│   └── notion_mcp/
│       ├── models/
│       │   ├── __init__.py
│       │   └── notion.py
│       ├── __init__.py
│       ├── __main__.py
│       ├── client.py
│       └── server.py
├── .env
├── .gitignore
├── pyproject.toml
└── README.md
```

## 🔐 Setting Up Notion Integration

1. Go to [Notion Integrations](https://www.notion.so/my-integrations)
2. Create a new integration
3. Grant the necessary capabilities (read, update, insert content)
4. Copy the integration token to your `.env` file
5. Share the Notion pages/databases you want to access with your integration

## 👥 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- Original implementation by [ccabanillas](https://github.com/ccabanillas/notion-mcp)
- Inspired by [danhilse's notion-mcp-server](https://github.com/danhilse/notion-mcp-server)
- Built to work with Claude Desktop and other AI assistants
