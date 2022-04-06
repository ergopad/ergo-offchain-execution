from enum import Enum
from typing import Any, List, Optional, Union
from pydantic import BaseModel, ValidationError

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
    comparisonValue: Optional[Union[int,str]]
    childNodes: Optional[List['FilterNode']]

class Filter(BaseModel):
    name: str
    filterType: FilterType
    repeats: int
    topics: List[str]
    messageTemplate: str
    filterTree: FilterNode

class FilterValidationException(Exception):
    def __init__(self, node: FilterNode, message: str, *args: object) -> None:
        self.node = node
        self.message = message
        super().__init__(*args)

def validateFilterNode(filterType: FilterType, node: FilterNode) -> bool:
    if node.nodeType in [FilterNodeType.AND,FilterNodeType.OR]:
        if node.fieldName is not None:
            raise FilterValidationException(node,"fieldName should not be set for AND/OR")
        if node.comparisonValue is not None:
            raise FilterValidationException(node,"comparisonValue should not be set for AND/OR")
        if node.childNodes is None:
            raise FilterValidationException(node,"childNodes should be set for AND/OR")
    else:
        if node.fieldName is None:
            raise FilterValidationException(node,"fieldName should be set")
        if node.comparisonValue is None:
            raise FilterValidationException(node,"comparisonValue should be set")
        if node.childNodes is not None:
            raise FilterValidationException(node,"childNodes should not be set")
        if node.fieldName not in field_validation[filterType].keys():
            raise FilterValidationException(node,f"{node.fieldName} is not a supported filter field")
        if field_validation[filterType][node.fieldName] is not Any and type(node.comparisonValue) is not field_validation[filterType][node.fieldName]:
            raise FilterValidationException(node,f"{node.comparisonValue} should be of type {field_validation[filterType][node.fieldName]} but is type {type(node.comparisonValue)}")
    valid = True
    if node.childNodes is not None:
        for child in node.childNodes:
            valid = valid and validateFilterNode(filterType, child) 
    return valid