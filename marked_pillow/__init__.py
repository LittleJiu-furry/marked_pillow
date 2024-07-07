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

# def parserHTML(content:str, prefix_for_css:str = ""):
#     document = lh.Document()
#     document.parserHTML(content)

#     def _getAllStyleElement():
#         rets:list[lh.Element] = []
#         def callback(root:lh.Element):
#             if root.name == "style":
#                 rets.append(root)
#             elif(root.name == "link" and root.attributes.get("rel") == "stylesheet"):
#                 rets.append(root)
#             return False # 不停止遍历
#         document.__dfs(document.root, callback)
#         return rets
#     for styleElement in _getAllStyleElement():
#         styles = None
#         if(styleElement.name == "style"):
#             styles = css.parseString(styleElement.InnerText)
#         elif(styleElement.name == "link"):
#             styles = css.parseFile(f"{prefix_for_css}/{styleElement.attributes.get('href')}")
#         if(not styles):
#             continue # 无法解析
#         for style in styles:
#             hit_element:list[lh.Element] = []
#             for selector in style.selectors:
#                 for selector_nodes, spec in selector:
#                     for selector_node in selector_nodes: #type: ignore
#                         if(hasattr(selector_node, "tag")):
#                             hit_element.extend(document.getElementsByTagName(selector_node.tag))
#                             for class_name in selector_node.classes:
#                                 hit_element.extend(document.getElementsByClassName(class_name))
#                             id_element = document.getElementById(selector_node.ids)
#                             if(id_element and id_element not in hit_element):
#                                 hit_element.append(id_element)
#                             hit_element = 


                                


    

        
    





    


    
    
