from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime


class FileInfo(BaseModel):
    model_config = ConfigDict(extra='allow')
    
    url: Optional[str] = None
    mimetype: Optional[str] = None
    size: Optional[int] = None
    height: Optional[int] = None
    width: Optional[int] = None
    
    
class Resource(BaseModel):
    model_config = ConfigDict(extra='allow')
    
    url: str
    files: List[List[FileInfo]] = Field(default_factory=list)
    caption: Optional[str] = None
    pdf: Optional[str] = None
    image: Optional[str] = None
    
    
class Pagination(BaseModel):
    model_config = ConfigDict(extra='allow')
    
    from_: int = Field(alias="from")
    to: int
    total: int
    current: int
    perpage: int
    next: Optional[str] = None
    previous: Optional[str] = None
    
    
class SearchResult(BaseModel):
    model_config = ConfigDict(extra='allow')
    
    id: str
    title: Optional[str] = None
    date: Optional[str] = None
    digitized: bool = False
    original_format: Optional[List[str]] = None
    online_format: Optional[List[str]] = None
    
    
class Item(BaseModel):
    model_config = ConfigDict(extra='allow')
    
    id: str
    title: str
    date: Optional[str] = None
    contributors: Optional[Union[List[str], List[Dict[str, str]]]] = Field(default_factory=list)
    subjects: Optional[List[str]] = Field(default_factory=list)
    format: Optional[Union[List[str], List[Dict[str, str]]]] = Field(default_factory=list)
    language: Optional[List[str]] = Field(default_factory=list)
    locations: Optional[List[str]] = Field(default_factory=list)
    rights: Optional[Union[str, List[str]]] = None
    medium: Optional[Union[str, List[str]]] = None
    call_number: Optional[Union[str, List[str]]] = None
    digital_id: Optional[List[str]] = Field(default_factory=list)
    library_of_congress_control_number: Optional[str] = None
    number_lccn: Optional[List[str]] = Field(default_factory=list)
    source_collection: Optional[List[str]] = Field(default_factory=list)
    description: Optional[List[str]] = Field(default_factory=list)
    notes: Optional[List[str]] = Field(default_factory=list)
    
    @field_validator('contributors', 'format', mode='before')
    def normalize_dict_lists(cls, v):
        if isinstance(v, list) and v and isinstance(v[0], dict):
            # Extract the first key from each dict
            return [list(d.keys())[0] if d else None for d in v]
        return v
    
    @field_validator('rights', 'medium', 'call_number', mode='before')
    def normalize_list_to_string(cls, v):
        if isinstance(v, list):
            return v[0] if v else None
        return v
    
    
class ItemResponse(BaseModel):
    model_config = ConfigDict(extra='allow')
    
    item: Item
    resources: List[Resource] = Field(default_factory=list)
    cite_this: Optional[Dict[str, Any]] = None
    
    
class SearchResponse(BaseModel):
    model_config = ConfigDict(extra='allow')
    
    results: List[SearchResult]
    pagination: Pagination
    facets: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    
    
class Collection(BaseModel):
    model_config = ConfigDict(extra='allow')
    
    id: str
    title: str
    description: Optional[str] = None
    item_count: Optional[int] = None