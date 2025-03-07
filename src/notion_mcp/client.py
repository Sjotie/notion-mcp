"""Notion API client implementation."""

import os
import logging
from typing import Any, Dict, List, Optional
import httpx
from .models.notion import Database, Page, SearchResults, PropertyValue

# Set up logging
logger = logging.getLogger('notion_mcp.client')

class NotionClient:
    """Client for interacting with the Notion API."""
    
    def __init__(self, api_key: str):
        """Initialize the Notion client.
        
        Args:
            api_key: Notion API key
        """
        self.api_key = api_key
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
    
    async def list_databases(self) -> List[Database]:
        """List all databases the integration has access to."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/search",
                headers=self.headers,
                json={
                    "filter": {
                        "property": "object",
                        "value": "database"
                    },
                    "page_size": 100,
                    "sort": {
                        "direction": "descending",
                        "timestamp": "last_edited_time"
                    }
                }
            )
            response.raise_for_status()
            data = response.json()
            if not data.get("results"):
                return []
            return [Database(**db) for db in data["results"]]
    
    async def query_database(
        self,
        database_id: str,
        filter: Optional[Dict[str, Any]] = None,
        sorts: Optional[List[Dict[str, Any]]] = None,
        start_cursor: Optional[str] = None,
        page_size: int = 100
    ) -> Dict[str, Any]:
        """Query a database."""
        body = {
            "page_size": page_size
        }
        if filter:
            body["filter"] = filter
        if sorts:
            body["sorts"] = sorts
        if start_cursor:
            body["start_cursor"] = start_cursor
            
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/databases/{database_id}/query",
                headers=self.headers,
                json=body
            )
            response.raise_for_status()
            return response.json()
    
    async def create_page(
        self,
        parent_id: str,
        properties: Dict[str, Any],
        children: Optional[List[Dict[str, Any]]] = None
    ) -> Page:
        """Create a new page."""
        body = {
            "parent": {"database_id": parent_id},
            "properties": properties
        }
        if children:
            body["children"] = children
            
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/pages",
                headers=self.headers,
                json=body
            )
            response.raise_for_status()
            return Page(**response.json())
    
    async def update_page(
        self,
        page_id: str,
        properties: Dict[str, Any],
        archived: Optional[bool] = None
    ) -> Page:
        """Update a page."""
        body = {"properties": properties}
        if archived is not None:
            body["archived"] = archived
            
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{self.base_url}/pages/{page_id}",
                headers=self.headers,
                json=body
            )
            response.raise_for_status()
            return Page(**response.json())
            
    async def create_database(
        self,
        parent_id: str,
        title: List[Dict[str, Any]],
        properties: Dict[str, Any],
        icon: Optional[Dict[str, Any]] = None,
        cover: Optional[Dict[str, Any]] = None
    ) -> Database:
        """Create a new database.
        
        Args:
            parent_id: ID of the parent page
            title: Database title as rich text array
            properties: Database properties schema
            icon: Optional icon for the database
            cover: Optional cover for the database
            
        Returns:
            The created database
        """
        # Ensure parent_id is properly formatted (remove dashes if present)
        parent_id = parent_id.replace("-", "")
        
        body = {
            "parent": {
                "type": "page_id",
                "page_id": parent_id
            },
            "title": title,
            "properties": properties
        }
        
        # Set default emoji if icon is specified but emoji is empty
        if icon and icon.get("type") == "emoji" and not icon.get("emoji"):
            icon["emoji"] = "📄"  # Default document emoji
            body["icon"] = icon
        elif icon:
            body["icon"] = icon
            
        if cover:
            body["cover"] = cover
            
        # Log the request body for debugging
        logger.info(f"Creating database with body: {body}")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/databases",
                headers=self.headers,
                json=body
            )
            response.raise_for_status()
            return Database(**response.json())
            
    async def update_database(
        self,
        database_id: str,
        title: Optional[List[Dict[str, Any]]] = None,
        description: Optional[List[Dict[str, Any]]] = None,
        properties: Optional[Dict[str, Any]] = None
    ) -> Database:
        """Update an existing database.
        
        Args:
            database_id: ID of the database to update
            title: Optional new title as rich text array
            description: Optional new description as rich text array
            properties: Optional updated properties schema
            
        Returns:
            The updated database
        """
        body = {}
        
        if title is not None:
            body["title"] = title
            
        if description is not None:
            body["description"] = description
            
        if properties is not None:
            body["properties"] = properties
            
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{self.base_url}/databases/{database_id}",
                headers=self.headers,
                json=body
            )
            response.raise_for_status()
            return Database(**response.json())
    
    async def get_page(self, page_id: str) -> Page:
        """Retrieve a page by its ID.
        
        Args:
            page_id: The ID of the page to retrieve
            
        Returns:
            The page object
        """
        # Ensure page_id is properly formatted (remove dashes if present)
        page_id = page_id.replace("-", "")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/pages/{page_id}",
                headers=self.headers
            )
            response.raise_for_status()
            return Page(**response.json())
    
    async def get_block_children(
        self, 
        block_id: str,
        start_cursor: Optional[str] = None,
        page_size: int = 100
    ) -> Dict[str, Any]:
        """Retrieve the children blocks of a block.
        
        Args:
            block_id: The ID of the block (page or block)
            start_cursor: Cursor for pagination
            page_size: Number of results per page
            
        Returns:
            Dictionary containing the block children
        """
        # Ensure block_id is properly formatted (remove dashes if present)
        block_id = block_id.replace("-", "")
        
        params = {"page_size": page_size}
        if start_cursor:
            params["start_cursor"] = start_cursor
            
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/blocks/{block_id}/children",
                headers=self.headers,
                params=params
            )
            response.raise_for_status()
            return response.json()
    
    async def append_block_children(
        self,
        block_id: str,
        children: List[Dict[str, Any]],
        after: Optional[str] = None
    ) -> Dict[str, Any]:
        """Append blocks to a parent block.
        
        Args:
            block_id: The ID of the parent block (page or block)
            children: List of block objects to append
            after: Optional ID of an existing block to append after
            
        Returns:
            Dictionary containing the response with newly created blocks
        """
        # Ensure block_id is properly formatted (remove dashes if present)
        block_id = block_id.replace("-", "")
        
        # Prepare request body
        body = {"children": children}
        if after:
            body["after"] = after.replace("-", "")  # Ensure after ID is properly formatted
            
        # Log the request for debugging
        logger.info(f"Appending {len(children)} blocks to {block_id}" + 
                   (f" after {after}" if after else ""))
        
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{self.base_url}/blocks/{block_id}/children",
                headers=self.headers,
                json=body
            )
            response.raise_for_status()
            return response.json()
            
    async def update_block(
        self,
        block_id: str,
        block_type: str,
        content: Dict[str, Any],
        archived: Optional[bool] = None
    ) -> Dict[str, Any]:
        """Update a block's content or archive status.
        
        Args:
            block_id: The ID of the block to update
            block_type: The type of block (paragraph, heading_1, to_do, etc.)
            content: The content for the block based on its type
            archived: Whether to archive (true) or restore (false) the block
            
        Returns:
            Dictionary containing the updated block
        """
        # Ensure block_id is properly formatted (remove dashes if present)
        block_id = block_id.replace("-", "")
        
        # Prepare request body
        body = {block_type: content}
        if archived is not None:
            body["archived"] = archived
            
        # Log the request for debugging
        logger.info(f"Updating block {block_id} of type {block_type}")
        
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{self.base_url}/blocks/{block_id}",
                headers=self.headers,
                json=body
            )
            response.raise_for_status()
            return response.json()
            
    async def get_block(self, block_id: str) -> Dict[str, Any]:
        """Retrieve a block by its ID.
        
        Args:
            block_id: The ID of the block to retrieve
            
        Returns:
            Dictionary containing the block
        """
        # Ensure block_id is properly formatted (remove dashes if present)
        block_id = block_id.replace("-", "")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/blocks/{block_id}",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
    
    async def search(
        self,
        query: str = "",
        filter: Optional[Dict[str, Any]] = None,
        sort: Optional[Dict[str, Any]] = None,
        start_cursor: Optional[str] = None,
        page_size: int = 100
    ) -> SearchResults:
        """Search Notion for pages or databases.
        
        Args:
            query: Search query string
            filter: Optional filter criteria
            sort: Optional sort criteria
            start_cursor: Cursor for pagination
            page_size: Number of results per page
            
        Returns:
            SearchResults object containing the results
        """
        body = {
            "query": query,
            "page_size": page_size
        }
        if filter:
            body["filter"] = filter
        if sort:
            body["sort"] = sort
        if start_cursor:
            body["start_cursor"] = start_cursor
            
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/search",
                headers=self.headers,
                json=body
            )
            response.raise_for_status()
            data = response.json()
            
            # Convert results based on their object type
            results = []
            for item in data.get("results", []):
                if item["object"] == "database":
                    results.append(Database(**item))
                elif item["object"] == "page":
                    # Pages already have the right property structure
                    results.append(Page(**item))
            
            return SearchResults(
                object="list",
                results=results,
                next_cursor=data.get("next_cursor"),
                has_more=data.get("has_more", False)
            ) 
