# 对选择器单独处理
# 利用状态机进行解析
from enum import IntEnum
import re


class State(IntEnum):
    INIT = 0 # 初始状态
    TAG = 1 # 标签选择器
    CLASS = 2 # 类选择器
    ID = 3 # ID选择器
    ATTR_START = 4 # 属性选择器开始
    ATTR_SELECTOR = 5 # 属性选择器
    ATTR_VALUE = 6 # 属性选择器的值
    ATTR_END = 7 # 属性选择器结束
    COMPLEX = 8 # 进入复杂选择器
    COMPLEX_SYMBOL = 9 # 复杂选择器的符号
    CLASS_START = 10 # 类选择器开始
    ID_START = 11 # ID选择器开始
    ATTR_EQUAL = 12 # 属性选择器的等号

# 状态转移表
STATE_TABLE = {
    State.INIT: {
        0: { # 可以直接查表转移的状态
            ".": State.CLASS_START,
            "#": State.ID_START,
            "[": State.ATTR_START,
        },
        1: { # 通过正则整合的
            re.compile(r'[a-zA-Z0-9]|\-|\_'): State.TAG
        }
    },
    State.TAG: {
        0: {
            ".": State.CLASS_START,
            "#": State.ID_START,
            "[": State.ATTR_START,
            " ": State.COMPLEX,
            ">": State.COMPLEX_SYMBOL,
            "+": State.COMPLEX_SYMBOL,
            "~": State.COMPLEX_SYMBOL,
            ",": State.COMPLEX_SYMBOL
        },
        1: {
            re.compile(r'[a-zA-Z0-9]|\-|\_'): State.TAG
        }
    },
    State.CLASS: {
        0: {
            ".": State.CLASS_START,
            "#": State.ID_START,
            "[": State.ATTR_START,
            " ": State.COMPLEX,
            ">": State.COMPLEX_SYMBOL,
            "+": State.COMPLEX_SYMBOL,
            "~": State.COMPLEX_SYMBOL,
            ",": State.COMPLEX_SYMBOL
        },
        1: {
            re.compile(r'[a-zA-Z0-9]|\-|\_'): State.CLASS
        }
    },
    State.ID: {
        0: {
            ".": State.CLASS_START,
            "#": State.ID_START,
            "[": State.ATTR_START,
            " ": State.COMPLEX,
            ">": State.COMPLEX_SYMBOL,
            "+": State.COMPLEX_SYMBOL,
            "~": State.COMPLEX_SYMBOL,
            ",": State.COMPLEX_SYMBOL
        },
        1: {
            re.compile(r'[a-zA-Z0-9]|\-|\_'): State.ID
        }
    },
    State.ATTR_START: {
        0: {
            "]": State.ATTR_END
        },
        1: {
            re.compile(r'[a-zA-Z0-9]|\-|\_'): State.ATTR_SELECTOR
        }
    },
    State.ATTR_SELECTOR: {
        0: {
            "=": State.ATTR_EQUAL,
            "]": State.ATTR_END
        },
        1: {
            re.compile(r'[a-zA-Z0-9]|\-|\_'): State.ATTR_SELECTOR
        }
    },
    State.ATTR_VALUE: {
        0: {
            "]": State.ATTR_END
        },
        1: {
            re.compile(r'[a-zA-Z0-9]|\-|\_|\'|\"'): State.ATTR_VALUE
        }
    },
    State.ATTR_END: {
        0: {
            ".": State.CLASS_START,
            "#": State.ID_START,
            "[": State.ATTR_START,
            " ": State.COMPLEX,
            ">": State.COMPLEX_SYMBOL,
            "+": State.COMPLEX_SYMBOL,
            "~": State.COMPLEX_SYMBOL,
            ",": State.COMPLEX_SYMBOL
        },
        1: {
            re.compile(r'[a-zA-Z0-9]|\-|\_'): State.TAG
        }
    },
    State.COMPLEX: {
        0: {
            ">": State.COMPLEX_SYMBOL,
            "+": State.COMPLEX_SYMBOL,
            "~": State.COMPLEX_SYMBOL,
            ".": State.CLASS_START,
            "#": State.ID_START,
            "[": State.ATTR_START,
            ",": State.COMPLEX_SYMBOL
        },
        1: {
            re.compile(r'[a-zA-Z0-9]|\-|\_'): State.TAG
        }
    },
    State.COMPLEX_SYMBOL: {
        0: {
            ".": State.CLASS_START,
            "#": State.ID_START,
            "[": State.ATTR_START,
            " ": State.COMPLEX,
        },
        1: {
            re.compile(r'[a-zA-Z0-9]|\-|\_'): State.TAG
        }
    },
    State.CLASS_START: {
        0: {},
        1: {
            re.compile(r'[a-zA-Z0-9]|\-|\_'): State.CLASS
        }
    },
    State.ID_START: {
        0: {},
        1: {
            re.compile(r'[a-zA-Z0-9]|\-|\_'): State.ID
        }
    },
    State.ATTR_EQUAL: {
        0: {},
        1: {
            re.compile(r'[a-zA-Z0-9]|\-|\_|\'|\"'): State.ATTR_VALUE
        }
    }
}

# 根据状态转移表进行解析
def tokenlize(selector_content:str) -> list[tuple[State, str]]:
    tokens:list[tuple[State, str]] = [] # 保存解析后的token
    temp = '' # 临时保存字符，用来构建

    # 计算状态转移
    def parse(state:State, char:str) -> State:
        if(char in STATE_TABLE[state][0]):
            return STATE_TABLE[state][0][char]
        for key in STATE_TABLE[state][1]:
            if(key.match(char)):
                return STATE_TABLE[state][1][key]
        raise Exception("解析错误")
    
    state = State.INIT
    for c in selector_content:
        _new_state = parse(state, c)
        if(_new_state == state):
            temp += c
        else:
            if(temp):
                tokens.append((state, temp))
            temp = c
        state = _new_state
    if(temp):
        tokens.append((state, temp))

    return tokens


# 测试
for token in tokenlize("div.test.test1[attr='value'][attr1=value2][attr2] > .test2 + #test3 ~ [attr4]"):
    if(token[0] == State.TAG):
        print(token)