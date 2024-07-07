from html.parser import HTMLParser
from typing import (
    Union, Any, Callable, Optional
)
from marked_pillow.css import parseStyle, parseFile, parseURL, CssSelector, CssSelectorNode

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
    
    def querySelectorAll(self, selector:CssSelector) -> Union[list[Element], None]:
        results:list[Element] = []
        temp_tag:set[Element] = set()
        temp_class:set[Element] = set()
        temp_id:set[Element] = set()
        temp_attr:set[Element] = set()
        def deal(resule:Optional[list[Element]] = None):
            if(not resule):
                selector_nodes, _ = selector
                selector_node = selector_nodes[0] #type: ignore
                if(hasattr(selector_node, "tag") and type(selector_node) == CssSelectorNode):
                    temp_tag.update(self.getElementsByTagName(selector_node.tag))
                    for class_name in selector_node.classes:
                        temp_class.update(self.getElementsByClassName(class_name))
                    id_element = self.getElementById(selector_node.ids) if selector_node.ids != "" else None
                    if(id_element):
                        temp_id.add(id_element)
                    def callback(root:Element):   
                        for attr, value in selector_node.attrs:
                            if(value == None or value == "" or value == "*"):
                                if(root.hasAttribute(attr)):
                                    temp_attr.add(root)
                            else:
                                if(root.getAttribute(attr) == value):
                                    temp_attr.add(root)
                        return False
                    self.__dfs(self.root, callback)
                # 排除上面的空集合
                temp_set = set()
                if(temp_tag):
                    temp_set.update(temp_tag)
                if(temp_class):
                    temp_set.update(temp_class)
                if(temp_id):
                    temp_set.update(temp_id)
                if(temp_attr):
                    temp_set.update(temp_attr)
                result = list(temp_set.copy())
                temp_tag.clear()
                temp_class.clear()
                temp_id.clear()
                temp_attr.clear()
            else:
                _tag = set()
                _class = set()
                _id = set()
                _attr = set()
                for element in resule:
                    for selector_nodes, spec in selector:
                        for selector_node in selector_nodes: #type: ignore
                            if(hasattr(selector_node, "tag")):
                                ...




        deal()
        # 再次遍历选择器列表，敲定元素
        # return deal(resule = results)
        return results

    
    # 遍历并输出所有节点
    def traverse(self):
        index = 0
        with open("output.txt", "w", encoding="utf-8") as f:
            def _dfs(root:Element, index:int):
                # print(f"{'|'*index}{root}")
                f.write(f"{'|'*index}{root}\n")
                for child in root.children:
                    _dfs(child, index+1)
            _dfs(self.root, index)
    
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
    
    def parserPath(self, path:str):
        with open(path, "r", encoding="utf-8") as f:
            self.parserHTML(f.read())
    



class Parser(HTMLParser):
    def __init__(self, document:Document):
        super().__init__()
        self.tree = document
        self.stack = [self.tree.current]
        self.supported_self_closing_tags = ["br", "img", "input", "hr", "meta", "link"]
        self.default_style = {}
        rules = None
        with open("a.txt", mode="r", encoding="utf-8") as f:
            rules = parseStyle(f.read())
        for rule in rules.properties:
            self.default_style[rule.name] = (rule.value, rule.priority, (0,-1,-1,-1))


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
        self.add_default_style(element)

    def add_default_style(self, element:Element):
        # 添加默认样式
        element.style = self.default_style.copy()
        

    def handle_endtag(self, tag: str) -> None:
        self.stack.pop()
        self.tree.current = self.stack[-1]


    def handle_data(self, data: str) -> None:
        self.tree.current.InnerText = data

    def parse(self, html:str):
        self.feed(html)
        self.close()
        del self.stack
