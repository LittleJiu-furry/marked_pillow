import cssutils as cu
from cssutils.util import Item as cuItem
from typing import (
    Union, NewType, Optional
)


class CssSelectorNode:
    tag:str
    classes:list[str]
    ids:str
    attrs:list[tuple[str, str]]
    isUniversal:bool = False
    def __init__(self, tag:str, classes:list[str], ids:str, attrs:list[tuple[str, str]], isUniversal:bool = False) -> None:
        self.tag = tag
        self.classes = classes
        self.ids = ids
        self.attrs = attrs
        self.isUniversal = isUniversal

    def __repr__(self):
        return (f"<marked_pillow.css.CSSSelector(tag={self.tag}, "
            f"classes={self.classes}, ids={self.ids}, attrs={self.attrs}, "
            f"isUniversal={self.isUniversal})>")
    
class CssSelectorComplex:
    typ: str
    c:str

    def __init__(self, typ:str, c:str) -> None:
        self.typ = typ
        self.c = c

    def __repr__(self) -> str:
        return f"<marked_pillow.css.CSSSelectorComplex(typ={self.typ}, c={self.c})>"

# (解析后的选择器[CssSelectorNode, CssSelectorComplex]，选择器的特异性(0,0,0,0))
CssSelector = NewType("CssSelector", tuple[list[Union[CssSelectorNode, CssSelectorComplex]],tuple[int,...]])


class CSSRules:
    selectors:list[CssSelector]
    properties:cu.css.Property
    
    def __init__(self) -> None:
        self.selectors = []
        self.properties = cu.css.Property()

    def __repr__(self) -> str:
        return (f"<marked_pillow.css.CSSRules(selectors={self.selectors}, "
            f"properties={self.properties})>")



def _parseSelector(cssSelectors:cu.css.Selector) -> list[CssSelector]:
    ret:list[CssSelector] = []
    for selector in cssSelectors:
        selector:cu.css.Selector = selector

        temp_selector = CssSelectorNode("", [], "", [])
        node_and_complex:list[Union[CssSelectorNode, CssSelectorComplex]] = [temp_selector]

        complex_type = ["child", "adjacent-sibling", "following-sibling", "descendant"]
        attrs_type = ["attribute-start", "attribute-end", "attribute-selector",
                    "attribute-value", "equals", "STRIING"]
        temp_attrs = []
        for item in selector.seq:
            item: cuItem = item
            if(item.type == "type-selector"):
                temp_selector.tag = item.value[1]
            elif(item.type == "class"):
                temp_selector.classes.append(str(item.value)[1:])
            elif(item.type == "id"):
                temp_selector.ids = str(item.value)[1:]
            elif(item.type in attrs_type):
                if(item.type == "equals"):
                    continue
                elif(item.type == "attribute-start"):
                    temp_attrs = []
                elif(item.type == "attribute-end"):
                    temp_selector.attrs.append(tuple(temp_attrs))
                    temp_attrs = []
                elif(item.type == "attribute-selector" 
                    or item.type == "attribute-value"
                    or item.type == "STRING"
                    ):
                    temp_attrs.append(item.value)
            elif(item.type in complex_type):
                # continue # 暂不处理复杂选择器
                node_and_complex.append(CssSelectorComplex(item.type, item.value))
                temp_selector = CssSelectorNode("", [], "", [])
            elif(item.type == "universal"):
                temp_selector.isUniversal = True
        if(temp_selector not in node_and_complex):
            node_and_complex.append(temp_selector)
        spec:tuple[int,...] = tuple(selector.specificity)
        d = (node_and_complex, spec)
        ret.append(CssSelector(d))
    return ret


def _parseRule(rules:list[cu.css.CSSStyleRule]) -> list[CSSRules]:
    rets:list[CSSRules] = []
    for rule in rules:
        if(rule.type != rule.STYLE_RULE):
            continue
        temp_rule = CSSRules()
        temp_rule.selectors = _parseSelector(rule.selectorList)
        style:cu.css.CSSStyleDeclaration = rule.style
        temp_rule.properties = style.getProperties()
        rets.append(temp_rule)
    return rets

def _getCssParserClass() -> cu.CSSParser:
    return cu.CSSParser(log= None, loglevel = 999) # 关闭日志输出

# 解析css字符串
def parseString(css_string) -> list[CSSRules]:
    sheet:cu.css.CSSStyleSheet = _getCssParserClass().parseString(css_string)
    return _parseRule(sheet.cssRules)

# 解析css文件
def parseFile(file_path:str) -> list[CSSRules]:
    sheet = _getCssParserClass().parseFile(file_path)
    return _parseRule(sheet.cssRules)

def parseStyle(style_content:str) -> CSSRules:
    csr = CSSRules()
    csr.properties = _getCssParserClass().parseStyle(style_content).getProperties()
    return csr

def parseURL(url:str) -> list[CSSRules]:
    sheet = _getCssParserClass().parseUrl(url)
    if(not sheet):
        raise Exception("Can't parse the url")
    return _parseRule(sheet.cssRules)

if __name__ == '__main__':
    print(parseString("""
        body h1{
            color: red;
        }
    """))
    

        
        

                


