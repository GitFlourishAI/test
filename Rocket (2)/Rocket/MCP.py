import os
from typing import Any, Dict, List, Optional

def MCP(sender: str, recipient: str, content: Dict[str, Any], context_refs: Optional[List[str]] = None) -> Dict[str, Any]:

  return {
    "sender": sender,
    "recipient": recipient,
    "content": content,
    "context_refs":context_refs or [],
  }


