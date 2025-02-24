"""MCP server implementation for Notion integration."""

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent, EmbeddedResource
from typing import Any, Dict, List, Optional, Sequence
import os
from datetime import datetime
import logging
import json
from pathlib import Path
from dotenv import load_dotenv

from .client import NotionClient
from .models.notion import Database, Page, SearchResults

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('notion_mcp')

# Find and load .env file from project root
project_root = Path(__file__).parent.parent.parent
env_path = project_root / '.env'
if not env_path.exists():
    raise FileNotFoundError(f"No .env file found at {env_path}")
load_dotenv(env_path)

# Initialize server
server = Server("notion-mcp")

# Configuration with validation
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
if not NOTION_API_KEY:
    raise ValueError("NOTION_API_KEY not found in .env file")

# Initialize Notion client
notion_client = NotionClient(NOTION_API_KEY)

@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available Notion tools."""
    return [
        Tool(
            name="list_databases",
            description="List all accessible Notion databases",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="query_database",
            description="Query items from a Notion database",
            inputSchema={
                "type": "object",
                "properties": {
                    "database_id": {
                        "type": "string",
                        "description": "ID of the database to query"
                    },
                    "filter": {
                        "type": "object",
                        "description": "Optional filter criteria"
                    },
                    "sorts": {
                        "type": "array",
                        "description": "Optional sort criteria"
                    }
                },
                "required": ["database_id"]
            }
        ),
        Tool(
            name="create_page",
            description="Create a new page in a database",
            inputSchema={
                "type": "object",
                "properties": {
                    "database_id": {
                        "type": "string",
                        "description": "ID of the database to create the page in"
                    },
                    "properties": {
                        "type": "object",
                        "description": "Page properties"
                    },
                    "children": {
                        "type": "array",
                        "description": "Optional page content blocks"
                    }
                },
                "required": ["database_id", "properties"]
            }
        ),
        Tool(
            name="update_page",
            description="Update an existing page",
            inputSchema={
                "type": "object",
                "properties": {
                    "page_id": {
                        "type": "string",
                        "description": "ID of the page to update"
                    },
                    "properties": {
                        "type": "object",
                        "description": "Updated page properties"
                    },
                    "archived": {
                        "type": "boolean",
                        "description": "Whether to archive the page"
                    }
                },
                "required": ["page_id", "properties"]
            }
        ),
        Tool(
            name="search",
            description="Search Notion content",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    },
                    "filter": {
                        "type": "object",
                        "description": "Optional filter criteria"
                    },
                    "sort": {
                        "type": "object",
                        "description": "Optional sort criteria"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="create_database",
            description="Create a new database in Notion",
            inputSchema={
                "type": "object",
                "properties": {
                    "parent_id": {
                        "type": "string",
                        "description": "ID of the parent page where the database will be created"
                    },
                    "title": {
                        "type": "string",
                        "description": "Title of the database"
                    },
                    "properties": {
                        "type": "object",
                        "description": "Schema definition for database properties (e.g., {\"Name\": {\"title\": {}}, \"Description\": {\"rich_text\": {}}})"
                    },
                    "icon": {
                        "type": "object",
                        "description": "Optional icon for the database (e.g., {\"type\": \"emoji\", \"emoji\": \"🔍\"})"
                    },
                    "cover": {
                        "type": "object",
                        "description": "Optional cover image for the database"
                    }
                },
                "required": ["parent_id", "title", "properties"]
            }
        ),
        Tool(
            name="update_database",
            description="Update an existing database in Notion",
            inputSchema={
                "type": "object",
                "properties": {
                    "database_id": {
                        "type": "string",
                        "description": "ID of the database to update"
                    },
                    "title": {
                        "type": "string",
                        "description": "New title for the database (optional)"
                    },
                    "description": {
                        "type": "string",
                        "description": "New description for the database (optional)"
                    },
                    "properties": {
                        "type": "object",
                        "description": "Updated schema definition for database properties. To remove a property, set its value to null."
                    }
                },
                "required": ["database_id"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent | EmbeddedResource]:
    """Handle tool calls for Notion operations."""
    try:
        if name == "list_databases":
            databases = await notion_client.list_databases()
            return [
                TextContent(
                    type="text",
                    text=SearchResults(results=databases).model_dump_json(indent=2)
                )
            ]
            
        elif name == "query_database":
            if not isinstance(arguments, dict):
                raise ValueError("Invalid arguments")
                
            database_id = arguments.get("database_id")
            if not database_id:
                raise ValueError("database_id is required")
                
            results = await notion_client.query_database(
                database_id=database_id,
                filter=arguments.get("filter"),
                sorts=arguments.get("sorts")
            )
            return [
                TextContent(
                    type="text",
                    text=SearchResults(results=results["results"]).model_dump_json(indent=2)
                )
            ]
            
        elif name == "create_page":
            if not isinstance(arguments, dict):
                raise ValueError("Invalid arguments")
                
            database_id = arguments.get("database_id")
            properties = arguments.get("properties")
            if not database_id or not properties:
                raise ValueError("database_id and properties are required")
                
            page = await notion_client.create_page(
                parent_id=database_id,
                properties=properties,
                children=arguments.get("children")
            )
            return [
                TextContent(
                    type="text",
                    text=page.model_dump_json(indent=2)
                )
            ]
            
        elif name == "update_page":
            if not isinstance(arguments, dict):
                raise ValueError("Invalid arguments")
                
            page_id = arguments.get("page_id")
            properties = arguments.get("properties")
            if not page_id or not properties:
                raise ValueError("page_id and properties are required")
                
            page = await notion_client.update_page(
                page_id=page_id,
                properties=properties,
                archived=arguments.get("archived")
            )
            return [
                TextContent(
                    type="text",
                    text=page.model_dump_json(indent=2)
                )
            ]
            
        elif name == "search":
            if not isinstance(arguments, dict):
                raise ValueError("Invalid arguments")
                
            query = arguments.get("query", "")
            results = await notion_client.search(
                query=query,
                filter=arguments.get("filter"),
                sort=arguments.get("sort")
            )
            return [
                TextContent(
                    type="text",
                    text=results.model_dump_json(indent=2)
                )
            ]
            
        elif name == "create_database":
            if not isinstance(arguments, dict):
                raise ValueError("Invalid arguments")
                
            parent_id = arguments.get("parent_id")
            title_text = arguments.get("title")
            properties = arguments.get("properties")
            
            if not parent_id or not title_text or not properties:
                raise ValueError("parent_id, title, and properties are required")
            
            # Convert simple title string to rich text array format
            title = [{"type": "text", "text": {"content": title_text, "link": None}}]
            
            # Ensure icon has a valid emoji if type is emoji
            icon = arguments.get("icon")
            if icon and isinstance(icon, dict) and icon.get("type") == "emoji" and not icon.get("emoji"):
                icon["emoji"] = "📄"  # Default document emoji
            
            try:
                database = await notion_client.create_database(
                    parent_id=parent_id,
                    title=title,
                    properties=properties,
                    icon=icon,
                    cover=arguments.get("cover")
                )
                
                return [
                    TextContent(
                        type="text",
                        text=database.model_dump_json(indent=2)
                    )
                ]
            except Exception as e:
                error_msg = str(e)
                logger.error(f"Database creation error: {error_msg}")
                
                # Try to provide more helpful error information
                if "400" in error_msg:
                    return [
                        TextContent(
                            type="text",
                            text=f"Error 400: Bad Request. Common issues include:\n"
                                 f"1. Invalid parent_id format (should be 32 characters without dashes)\n"
                                 f"2. Missing required fields in properties\n"
                                 f"3. Invalid property configurations\n\n"
                                 f"Original error: {error_msg}\n\n"
                                 f"Request data:\n"
                                 f"parent_id: {parent_id}\n"
                                 f"title: {title_text}\n"
                                 f"properties: {json.dumps(properties, indent=2)}"
                        )
                    ]
                else:
                    return [
                        TextContent(
                            type="text",
                            text=f"Error: {error_msg}"
                        )
                    ]
            
            return [
                TextContent(
                    type="text",
                    text=database.model_dump_json(indent=2)
                )
            ]
            
        elif name == "update_database":
            if not isinstance(arguments, dict):
                raise ValueError("Invalid arguments")
                
            database_id = arguments.get("database_id")
            if not database_id:
                raise ValueError("database_id is required")
            
            title = None
            if "title" in arguments and arguments["title"]:
                title_text = arguments["title"]
                title = [{"type": "text", "text": {"content": title_text, "link": None}}]
                
            description = None
            if "description" in arguments and arguments["description"]:
                desc_text = arguments["description"]
                description = [{"type": "text", "text": {"content": desc_text, "link": None}}]
            
            database = await notion_client.update_database(
                database_id=database_id,
                title=title,
                description=description,
                properties=arguments.get("properties")
            )
            
            return [
                TextContent(
                    type="text",
                    text=database.model_dump_json(indent=2)
                )
            ]
            
        else:
            raise ValueError(f"Unknown tool: {name}")
            
    except Exception as e:
        logger.error(f"Error in tool {name}: {str(e)}")
        return [
            TextContent(
                type="text",
                text=f"Error: {str(e)}"
            )
        ]

async def main():
    """Run the server."""
    if not NOTION_API_KEY:
        raise ValueError("NOTION_API_KEY environment variable is required")
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
