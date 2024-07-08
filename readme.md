## marked_pillow

**你当前正在查看dev分支，如果您正在寻找正式发布的内容，请切换至`main`分支 [快速切换](https://github.com/LittleJiu-furry/marked_pillow)**

本仓库的dev分支不会发布预览内容，预览内容在`preview`分支中发布

html解析下不支持的内容
- `<br>`标签的强制换行
- 文字和标签在同一元素下的混排

html解析下需要注意的的内容
- 自封闭标签必须使用`/>`闭合

css解析下不支持的内容
- 所有以`@`起始的css规则
- css变量
- 伪类和伪元素
- css中的所有函数
