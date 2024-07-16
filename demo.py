import marked_pillow as mp
from PIL import (
    Image, ImageDraw, ImageFont
)
s = ""
with open("test.html", "r") as f:
    s = f.read()
    
document = mp.parserHTML(s)
# document.getElementsByClassName("box")[0].render().show()
document.getElementsByTagName("div")[0].render().show()

