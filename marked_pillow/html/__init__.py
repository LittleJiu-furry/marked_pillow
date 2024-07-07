from html.parser import HTMLParser
from typing import (
    Union, Any, Callable, Optional
)
from marked_pillow.css import parseStyle, parseFile, parseURL

class ElementClassList(list):...

class Element:
    # python中不存在提升规则，因此这里暂时忽略提前引用导致的类型检查错误
    def __init__(self, from_tree:"ElementTree"):
        self.name = ""
        self.attributes:dict[str, Union[tuple[Any], list[Any], Any]] = {}
        self.children:list[Element] = []
        self.classList = ElementClassList()
        self.InnerText = ""
        self.id = ""
        self.__tree = from_tree
        # css样式
        self.style = {}
        self.offsetWidth = 0
        self.offsetHeight = 0
        
        self.offsetX = 0
        self.offsetY = 0

        self.parent: Optional[Element] = None
    
    def getAttribute(self, key:str) -> Union[Any, None]:
        return self.attributes.get(key, None)
    
    def setAttribute(self, key:str, value:Any):
        self.attributes[key] = value

    def removeAttribute(self, key:str):
        if key in self.attributes:
            del self.attributes[key]

    def hasAttribute(self, key:str) -> bool:
        return key in self.attributes
    
    def __str__(self) -> str:
        return f"<Element {self.name} id:'{self.id}' classList:{self.classList}, innerText:'{self.InnerText}'>"
    
    def getElementById(self, _id:str) -> Union["Element", None]:
        def callback(root:Element):
            return root.id == _id
        return self.__tree.__dfs(self, callback)
    
    def getElementsByClassName(self, className:str) -> list["Element"]:
        results:list["Element"] = []
        def callback(root:Element):
            if className in root.classList:
                results.append(root)
            return False # 不停止遍历
        self.__tree.__dfs(self, callback)
        return results
    
    def getElementsByTagName(self, tagName:str) -> list["Element"]:
        results:list["Element"] = []
        def callback(root:Element):
            if root.name == tagName:
                results.append(root)
            return False
        self.__tree.__dfs(self, callback)
        return results

class ElementTree:
    def __init__(self):
        # 根节点应当是一个空节点
        self.root = Element(self)
        self.current = self.root
    
    def append(self, element:Element):
        self.current.children.append(element)
        element.parent = self.current
    
    # 这是一个普通多叉树
    # 深度优先遍历
    def __dfs(self, root:Element, callback:Callable[[Element], bool]) -> Union[Element, None]:
        # 深度优先遍历
        # callback用来返回布尔值，用来判断是否找到了目标节点
        if callback(root):
            return root
        for child in root.children:
            res = self.__dfs(child, callback)
            if res:
                return res
        return None
    
    def getElementById(self, _id:str) -> Union[Element, None]:
        def callback(root:Element):
            return root.id == _id
        return self.__dfs(self.root, callback)
    
    def getElementsByClassName(self, className:str) -> list[Element]:
        results:list[Element] = []
        def callback(root:Element):
            if className in root.classList:
                results.append(root)
            return False # 不停止遍历
        self.__dfs(self.root, callback)
        return results

    def getElementsByTagName(self, tagName:str) -> list[Element]:
        results:list[Element] = []
        def callback(root:Element):
            if root.name == tagName:
                results.append(root)
            return False # 不停止遍历
        self.__dfs(self.root, callback)
        return results
    
    # # 遍历并输出所有节点
    # def traverse(self):
    #     index = 0
    #     with open("output.txt", "w", encoding="utf-8") as f:
    #         def _dfs(root:Element, index:int):
    #             # print(f"{'|'*index}{root}")
    #             f.write(f"{'|'*index}{root}\n")
    #             for child in root.children:
    #                 _dfs(child, index+1)
    #         _dfs(self.root, index)
    
class Document(ElementTree):
    def __init__(self):
        super().__init__()
        self.parser = Parser(self)

    def parserHTML(self, html:str):
        self.parser.parse(html)
        try:
            self.documentElement = self.getElementsByTagName("html")[0]
            try:
                self.head = self.getElementsByTagName("head")[0]
            except IndexError:
                self.head = None

            try:
                self.body = self.getElementsByTagName("body")[0]
            except IndexError:
                self.body = None
        except IndexError:
            self.documentElement = None
            self.head = None
            self.body = None
        
        del self.parser



class Parser(HTMLParser):
    def __init__(self, document:Document):
        super().__init__()
        self.tree = document
        self.stack = [self.tree.current]
        self.supported_self_closing_tags = ["br", "img", "input", "hr", "meta", "link"]

    def handle_starttag(self, tag: str, attrs: list[tuple[str, Union[str, None]]]) -> None:
        element = Element(self.tree)
        element.name = tag
        for key, value in attrs:
            if(key == "class"):
                element.classList = ElementClassList(str(value).split(" "))
            elif(key == "id"):
                element.id = str(value)
            else:
                element.setAttribute(key, value)
        
        element.parent = self.stack[-1]
        self.tree.append(element)
        self.stack.append(element)
        self.tree.current = element
        # 在堆栈中针对于自封闭标签的处理
        # if tag in self.supported_self_closing_tags:
        #     self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        self.stack.pop()
        self.tree.current = self.stack[-1]


    def handle_data(self, data: str) -> None:
        self.tree.current.InnerText = data

    def parse(self, html:str):
        self.feed(html)
        self.close()
        del self.stack
