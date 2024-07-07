## marked_pillow

这是一个基于`pillow`模块，使用`html+css`进行绘图的模块，当然你也可以使用它在脱离浏览器的环境下对html文档内容进行解析绘制。

**项目正在开发中，在本仓库使用tag正式发布前，请不要使用本模块。**

如果您有任何问题或建议，欢迎提交issue。

如果您有兴趣参与开发，欢迎fork本仓库并提交pull request，但请注意，您应当fork `dev`分支，并且在提交pr时，应当向`feature`分支提交，请不要直接向`dev`分支和`main`提交pr。

本仓库不欢迎以任何形式的搬运转载，本仓库明确声明，任何在非github.com/LittleJiu-furry/marked_pillow仓库下的代码均不是本仓库的代码，本仓库不对这些代码的安全性和合法性负责。

Copyright (c) 2024 LittleJiu All rights reserved.

## 解析说明
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

