from utils.models import Filter, FilterNode, FilterNodeType
import re
import logging

levelname = logging.DEBUG
logging.basicConfig(format='{asctime}:{name:>8s}:{levelname:<8s}::{message}', style='{', level=levelname)

class FilterValidator():
    def __init__(self, filter: Filter) -> None:
        self.filter: Filter = Filter.from_orm(filter)

    def process(self,message):
        self.wildcards = {}
        if self.processNode(self.filter.filterTree,message):
            logging.info("Found a match")
            logging.info(self.filter)
            logging.info(message)

    def processNode(self,node: FilterNode, message) -> bool:
        if node.nodeType is FilterNodeType.AND:
            result = True
            for child in node.childNodes:
                result = result and self.processNode(child,message)
                if not result:
                    return result
            return result
        if node.nodeType is FilterNodeType.OR:
            result = False
            for child in node.childNodes:
                result = result or self.processNode(child,message)
                if result:
                    return result
            return result
        cleanedFieldName = node.fieldName
        for wildcard in self.wildcards.keys():
            cleanedFieldName = cleanedFieldName.replace(wildcard,self.wildcards[wildcard])
        wildcardMatch: re.Match = re.search("(%.*%)",cleanedFieldName)
        if wildcardMatch is not None:
            wildcard = wildcardMatch.group()
            fieldNames = cleanedFieldName.split(f'.{wildcard}')
            searchArray = FilterValidator.getValue(message,fieldNames[0])
            for i in range(len(searchArray)):
                if len(fieldNames) > 1:
                    value = FilterValidator.getValue(searchArray[i],fieldNames[1][1:])
                else:
                    value = searchArray[i]
                if value is not None:
                    if self.processComparison(value,node.comparisonValue,node.nodeType):
                        self.wildcards[wildcard] = i
                        return True
            return False
        else:
            value = FilterValidator.getValue(message,cleanedFieldName)
            if value is not None:
                return self.processComparison(value,node.comparisonValue,node.nodeType)
            else:
                return False
                
    def processComparison(self,value,comparisonValue,compareType: FilterNodeType) -> bool:
        if compareType is FilterNodeType.EQUALS:
            return value == comparisonValue
        if compareType is FilterNodeType.GT:
            return value > comparisonValue
        if compareType is FilterNodeType.GTE:
            return value >= comparisonValue
        if compareType is FilterNodeType.LT:
            return value < comparisonValue
        if compareType is FilterNodeType.LTE:
            return value <= comparisonValue
        return False


    def getValue(utxo,fieldName):
        indices = fieldName.split('.')
        returnValue = utxo
        for index in indices:
            if type(returnValue) not in [list,dict]:
                returnValue = eval(returnValue)
            if type(returnValue) is list:
                index = int(index)
                if index >= len(returnValue):
                    return None
            else:
                if index not in returnValue:
                    return None
            
            returnValue = returnValue[index]
        
        return returnValue