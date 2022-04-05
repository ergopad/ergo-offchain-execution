from enum import Enum
from typing import Any, List, Optional, Union
from pydantic import BaseModel

class FilterType(str, Enum):
    UTXO = "utxo"
    BLOCK = "block"

class FilterNodeType(str, Enum):
    AND = "and"
    OR = "or"
    EQUALS = "equals"
    GT = "gt"
    GTE = "gte"
    LT = "lt"
    LTE = "lte"

field_validation = {
    FilterType.UTXO: {
        "R4.renderedValue": Any
    },
    FilterType.BLOCK: {
        "timestamp": int
    }
}

class FilterNode(BaseModel):
    nodeType: FilterNodeType
    fieldName: Optional[str]
    comparisonValue: Optional[Union[str,int]]
    childNodes: Optional[List['FilterNode']]

class Filter(BaseModel):
    filterType: FilterType
    repeats: int
    topics: List[str]
    messageTemplate: str
    filterTree: FilterNode