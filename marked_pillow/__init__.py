'''
    Marked Pillow 是一个利用html+css标记语言来实现更方便绘图效果的一个绘图工具

    你可以通过html+css更加简单的来实现更加丰富的绘图效果

    针对于自封闭标签，此模块要求必须使用/>来结束标签

    Written by Little_Jiu

'''

__version__ = '0.1.0'
__author__ = 'Little_Jiu'
__license__ = 'LGPL-3.0'

# from PIL import Image, ImageDraw, ImageFont
from . import html as lh
from . import css
import os

def parserHTML(content:str, prefix_for_css:str = ""):
    document = lh.Document()
    document.parserHTML(content)

    def _getAllStyleElement():
        rets:list[lh.Element] = []
        def callback(root:lh.Element):
            if root.name == "style":
                rets.append(root)
            elif(root.name == "link" and root.attributes.get("rel") == "stylesheet"):
                rets.append(root)
            return False # 不停止遍历
        document._dfs(document.root, callback)
        return rets
    
    # 获得所有的样式
    rules:list[css.CSSRules] = []
    for styleElement in _getAllStyleElement():        
        if(styleElement.name == "style"):
            rules.extend(css.parseString(styleElement.InnerText))
        elif(styleElement.name == "link"):
            path = os.path.join(prefix_for_css, str(styleElement.attributes.get("href", "")))
            rules.extend(css.parseFile(path))
    
    for rule in rules:
        for selector in rule.selectors:
            _, spec = selector
            elements = document._querySelectorAll(selector)
            if(not elements):
                continue
            for element in elements:
                for prop in rule.properties:
                    if(prop.name in element.style):
                        # 比较特异性
                        if(prop.priority != ""):
                            # ！important
                            element.style[prop.name] = (prop.value, prop.priority, spec)
                            continue
                        
                        inline_spec, ids_spec, classes_spec, tag_spec = spec
                        inline_element, ids_element, classes_element, tag_element = element.style[prop.name][2]
                        if(inline_spec > inline_element):
                            element.style[prop.name] = (prop.value, prop.priority, spec)
                            continue
                        elif(inline_spec == inline_element):
                            if(ids_spec > ids_element):
                                element.style[prop.name] = (prop.value, prop.priority, spec)
                                continue
                            elif(ids_spec == ids_element):
                                if(classes_spec > classes_element):
                                    element.style[prop.name] = (prop.value, prop.priority, spec)
                                    continue
                                elif(classes_spec == classes_element):
                                    if(tag_spec > tag_element):
                                        element.style[prop.name] = (prop.value, prop.priority, spec)
                                        continue
                    else:
                        element.style[prop.name] = (prop.value, prop.priority, spec)
    return document




        


                                


    

        
    





    


    
    
