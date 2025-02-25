"""Pydantic models for Notion API objects."""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from datetime import datetime
import json

class NotionObject(BaseModel):
    """Base class for Notion objects."""
    object: str
    id: str
    created_time: datetime
    last_edited_time: Optional[datetime] = None
    url: Optional[str] = None
    public_url: Optional[str] = None

class RichText(BaseModel):
    """Model for rich text content."""
    type: str
    text: Dict[str, Any]
    annotations: Optional[Dict[str, Any]] = None
    plain_text: Optional[str] = None
    href: Optional[str] = None

class PropertyValue(BaseModel):
    """Model for property values."""
    id: str
    type: str
    title: Optional[List[RichText]] = None
    rich_text: Optional[List[RichText]] = None
    select: Optional[Dict[str, Any]] = None
    multi_select: Optional[List[Dict[str, Any]]] = None
    url: Optional[str] = None
    checkbox: Optional[bool] = None
    number: Optional[float] = None
    date: Optional[Dict[str, Any]] = None

class Page(NotionObject):
    """Model for a Notion page."""
    parent: Dict[str, Any]
    archived: bool = False
    properties: Dict[str, PropertyValue]

class DatabaseProperty(BaseModel):
    """Model for database property configuration."""
    id: str
    name: str
    type: str

class Database(NotionObject):
    """Model for a Notion database."""
    title: List[RichText]
    description: List[RichText] = Field(default_factory=list)
    properties: Dict[str, DatabaseProperty]
    archived: bool = False

class SearchResults(BaseModel):
    """Model for search results."""
    object: str = "list"
    results: List[Union[Database, Page]]
    next_cursor: Optional[str] = None
    has_more: bool = False
    
def rich_text_to_markdown(rich_text_list: List[Dict[str, Any]]) -> str:
    """Convert rich text to markdown.
    
    Args:
        rich_text_list: List of rich text objects
        
    Returns:
        Markdown string
    """
    markdown = ""
    for rt in rich_text_list:
        text = rt.get("text", {}).get("content", "")
        annotations = rt.get("annotations", {})
        
        # Apply annotations
        if annotations.get("bold"):
            text = f"**{text}**"
        if annotations.get("italic"):
            text = f"*{text}*"
        if annotations.get("strikethrough"):
            text = f"~~{text}~~"
        if annotations.get("code"):
            text = f"`{text}`"
        if rt.get("href"):
            text = f"[{text}]({rt.get('href')})"
            
        markdown += text
    
    return markdown

def block_to_markdown(block: Dict[str, Any]) -> str:
    """Convert a block to markdown.
    
    Args:
        block: Block object
        
    Returns:
        Markdown string
    """
    block_type = block.get("type")
    if not block_type:
        return ""
    
    content = block.get(block_type, {})
    rich_text = content.get("rich_text", [])
    text = rich_text_to_markdown(rich_text)
    
    if block_type == "paragraph":
        return f"{text}\n\n"
    elif block_type == "heading_1":
        return f"# {text}\n\n"
    elif block_type == "heading_2":
        return f"## {text}\n\n"
    elif block_type == "heading_3":
        return f"### {text}\n\n"
    elif block_type == "bulleted_list_item":
        return f"* {text}\n"
    elif block_type == "numbered_list_item":
        return f"1. {text}\n"
    elif block_type == "to_do":
        checked = content.get("checked", False)
        checkbox = "[x]" if checked else "[ ]"
        return f"{checkbox} {text}\n"
    elif block_type == "code":
        language = content.get("language", "")
        return f"```{language}\n{text}\n```\n\n"
    elif block_type == "quote":
        return f"> {text}\n\n"
    elif block_type == "divider":
        return "---\n\n"
    else:
        return f"{text}\n\n"
