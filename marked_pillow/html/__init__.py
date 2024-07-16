from html.parser import HTMLParser
from typing import (
    Union, Any, Callable, Optional, Generator
)
from marked_pillow.css import (
    parseStyle, parseFile, parseURL, parseString,
    CssSelector, CssSelectorNode, CssSelectorComplex
)
from PIL import (
    Image, ImageDraw, ImageFont
)

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
        self.style:dict[str, tuple[str, str, tuple[int,...]]] = {}
        self.offsetWidth = 0
        self.offsetHeight = 0
        
        self.offsetX = 0
        self.offsetY = 0

        self.parent: Optional[Element] = None
    
    def render(self) -> Image.Image:
        # 如果他有子元素，则调用子元素的render方法，拿到子元素绘制的图片对象
        childrenImages:list[Image.Image] = []
        if self.children:
            for child in self.children:
                childrenImages.append(child.render())
            temp_img = None
            ret_img = childrenImages[0]
            for child in childrenImages[1:]:
                width = max(ret_img.width, child.width)
                height = ret_img.height + child.height
                temp_img = Image.new("RGB", (width, height), (255,255,255))
                temp_img.paste(ret_img, (0, 0))
                temp_img.paste(child, (0, ret_img.height))
                ret_img = temp_img.copy()
                temp_img = None
            
            # temp_img = Image.new("RGB", (ret_img.width + 10, ret_img.height + 10), (255,255,255))
            # temp_img.paste(ret_img, (5, 5))
            # ret_img = temp_img.copy()
            # temp_img = None
            return ret_img
        else:
            fontSize = self.style.get("font-size", ("20px","",(0)))[0]
            if(fontSize.endswith("px")):
                fontSize = float(fontSize[:-2])
            else:
                fontSize = float(fontSize)
            font = ImageFont.truetype("simhei.ttf",size = float(fontSize))
            textbox = ImageDraw.Draw(Image.new("RGB", (1, 1))).textbbox((0, 0), self.InnerText, font=font)
            temp_img = Image.new("RGB", (textbox[2], textbox[3]), (255, 255, 255))
            ImageDraw.Draw(temp_img).text((0, 0), self.InnerText, fill=(0, 0, 0), font=font)
            return temp_img
    
    
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
        return f"<Element {self.name} id:'{self.id}' classList:{self.classList}, innerText:'{self.InnerText}' style:{self.style}>"
    
    def __repr__(self) -> str:
        return f"<Element {self.name} id:'{self.id}' classList:{self.classList}, innerText:'{self.InnerText}' style:{self.style}>"

    def getElementById(self, _id:str) -> Union["Element", None]:
        def callback(root:Element):
            return root.id == _id
        return self.__tree._dfs(self, callback)
    
    def getElementsByClassName(self, className:str) -> list["Element"]:
        results:list["Element"] = []
        def callback(root:Element):
            if className in root.classList:
                results.append(root)
            return False # 不停止遍历
        self.__tree._dfs(self, callback)
        return results
    
    def getElementsByTagName(self, tagName:str) -> list["Element"]:
        results:list["Element"] = []
        def callback(root:Element):
            if root.name == tagName:
                results.append(root)
            return False
        self.__tree._dfs(self, callback)
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
    def _dfs(self, root:Element, callback:Callable[[Element], bool]) -> Union[Element, None]:
        # 深度优先遍历
        # callback用来返回布尔值，用来判断是否找到了目标节点
        if callback(root):
            return root
        for child in root.children:
            res = self._dfs(child, callback)
            if res:
                return res
        return None
    
    def getElementById(self, _id:str) -> Union[Element, None]:
        def callback(root:Element):
            return root.id == _id
        return self._dfs(self.root, callback)
    
    def getElementsByClassName(self, className:str) -> list[Element]:
        results:list[Element] = []
        def callback(root:Element):
            if className in root.classList:
                results.append(root)
            return False # 不停止遍历
        self._dfs(self.root, callback)
        return results

    def getElementsByTagName(self, tagName:str) -> list[Element]:
        results:list[Element] = []
        def callback(root:Element):
            if root.name == tagName:
                results.append(root)
            return False # 不停止遍历
        self._dfs(self.root, callback)
        return results
    
    def querySelectorAll(self, selector:str) -> Union[list[Element], None]:
        # 将str转换为CssSelector
        css_selector = parseString(selector + " {\n}")
        return self._querySelectorAll(css_selector[0].selectors[0])

    def _querySelectorAll(self, selector:CssSelector) -> Union[list[Element], None]:
        results:list[Element] = []
        temp_tag:set[Element] = set()
        temp_class:set[Element] = set()
        temp_id:set[Element] = set()
        temp_attr:set[Element] = set()
        
        def deal_complex(resule:list[Element]):
            temp_resule:set[Element] = set()
            # 处理复杂选择器
            selector_nodes, _ = selector
            for selector_node in selector_nodes[1:]:
                if(type(selector_node) == CssSelectorComplex):
                    if(selector_node.c =="+"):
                        # 相邻兄弟选择器
                        for e in resule:
                            if(e.parent):
                                # 应当选中这个元素在父元素中的下一个元素
                                index = e.parent.children.index(e)
                                if(index+1 < len(e.parent.children)):
                                    temp_resule.add(e.parent.children[index+1])
                    elif(selector_node.c == "~"):
                        # 后续兄弟选择器
                        for e in resule:
                            if(e.parent):
                                # 应当选中这个元素在父元素中的下一个元素
                                index = e.parent.children.index(e)
                                if(index + 1 < len(e.parent.children)):
                                    temp_resule.update(e.parent.children[index+1:])
                    elif(selector_node.c == ">"):
                        # 直接子元素选择器
                        for e in resule:
                            temp_resule.update(e.children)
                    elif(selector_node.c == " "):
                        # 后代选择器
                        def callback(root:Element):
                            temp_resule.add(root)
                            return False
                        for e in resule:
                            self._dfs(e, callback)
                if(type(selector_node) == CssSelectorNode):
                    # 从temp_resule中筛选
                    for item in temp_resule:
                        if(selector_node.tag):
                            if(item.name == selector_node.tag):
                                temp_tag.add(item)
                        if(selector_node.classes):
                            for class_name in selector_node.classes:
                                if class_name in item.classList:
                                    temp_class.add(item)
                        if(selector_node.ids):
                            if(item.id == selector_node.ids):
                                temp_id.add(item)
                        if(selector_node.attrs):
                            for attr, value in selector_node.attrs:
                                if(value == None or value == "" or value == "*"):
                                    if(item.hasAttribute(attr)):
                                        temp_attr.add(item)
                                else:
                                    if(item.getAttribute(attr) == value):
                                        temp_attr.add(item)
                    temp_set = set()
                    # 全部添加进去
                    temp_set.update(temp_tag)
                    temp_set.update(temp_class)
                    temp_set.update(temp_id)
                    temp_set.update(temp_attr)
                    # 排除空集，按照集合数量由大到小排序
                    temp_sets = []
                    if(temp_tag):
                        temp_sets.append(temp_tag)
                    if(temp_class):
                        temp_sets.append(temp_class)
                    if(temp_id):
                        temp_sets.append(temp_id)
                    if(temp_attr):
                        temp_sets.append(temp_attr)
                    temp_sets.sort(key=lambda x:len(x), reverse=True)
                    # 取交集
                    for _set in temp_sets:
                        temp_set &= _set
                    temp_resule &= temp_set
            nonlocal results
            results = list(temp_resule.copy())

        # 对第一个节点进行处理
        def deal():
            selector_nodes, _ = selector
            selector_node = selector_nodes[0]
            if(type(selector_node) == CssSelectorNode):
                temp_tag.update(self.getElementsByTagName(selector_node.tag)) if selector_node.tag != "" else None
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
                self._dfs(self.root, callback)

            temp_set = set()
            # 全部添加进去
            temp_set.update(temp_tag)
            temp_set.update(temp_class)
            temp_set.update(temp_id)
            temp_set.update(temp_attr)
            # 排除空集，按照集合数量由大到小排序
            temp_sets = []
            if(temp_tag):
                temp_sets.append(temp_tag)
            if(temp_class):
                temp_sets.append(temp_class)
            if(temp_id):
                temp_sets.append(temp_id)
            if(temp_attr):
                temp_sets.append(temp_attr)
            temp_sets.sort(key=lambda x:len(x), reverse=True)
            # 取交集
            for _set in temp_sets:
                temp_set &= _set
            nonlocal results
            results = list(temp_set.copy())
            temp_tag.clear()
            temp_class.clear()
            temp_id.clear()
            temp_attr.clear()

            if(len(selector_nodes) > 1):
                deal_complex(results)

        deal()
        return results
    
    # 遍历所有节点，并以生成器方式返回
    def travel(self, start_element: Element) -> Generator[Element, None, None]:
        def _dfs(root:Element):
            if(root != start_element):
                yield root
            for child in root.children:
                yield from _dfs(child)
        yield from _dfs(start_element)
    
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
    
    def render(self, start_element: Optional[Element] = None) -> Image.Image:
        if(start_element == None):
            start_element = self.body if self.body != None else self.root
        return start_element.render()

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
