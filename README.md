# Fighting

[![travis-ci](https://api.travis-ci.org/ncuhome/fighting.svg)](https://travis-ci.org/ncuhome/fighting) [![codecov](https://codecov.io/gh/ncuhome/fighting/branch/master/graph/badge.svg)](https://codecov.io/gh/ncuhome/fighting)

A simple JSON API web framework based on Flask

- GET请求查看文档，POST请求调用API
- 校验输入，序列化输出
- 支持自定义指令，自定义校验器

注意：仅支持Python3.3+

## Install

```
pip install fighting
```

## Quickstart:

```python
"""
整个API的介绍，以@开头的YAML文本表示共享的数据格式

@message:
    hello?str: 欢迎信息
"""
from fighting import Fighting

app = Fighting(__name__)   # Fighting是Flask的子类


@app.res('resource')       # 添加路由，URL为'/resource/action'
def action(name):
    """
    文档字符串中，以$开头的YAML文本表示指令

    $input:
        name?str&default="world": 你的名字
    $output: @message
    """
    return {'hello': name}   # 自动序列化为JSON格式


if __name__ == '__main__':
    app.run(debug=True)
```

Schema语法:  http://restaction-zh-cn.readthedocs.io/schema/

工具函数:

```python
from fighting import abort

abort(message)  # 状态码为400，内容为"message"
```

## 高级用法

#### 自定义指令:

```python
def my_directive(f, meta, app):
    """
    自定义`$my`指令
    
    Args:
        f:    使用指令的函数
        meta: 指令附带的数据
        app:  Fighting对象
    """
    def view():
        pass
    return view
app = Fighting(__name__, directives={'name': my_directive})
```

注: 指令可理解为装饰器，这些装饰器会自动应用到被`app.res`装饰的函数上。

#### 自定义校验器:

```python
def my_validator(*args, **kwargs):
    def validator(value):
        pass
    return validator
app = Fighting(__name__, validators={'name': my_validator})
```

参考:  https://github.com/guyskk/validr#custom-validator

#### 调用远程API

```python
from fighting import Res, ResError                  # 请求失败会抛出ResError

res = Res('http://127.0.0.1:5000/')                 # 设置URL前缀
data = res.post('resource/action', {'name': 'kk'})  # 发送请求
print(data)                                         # {'hello': 'kk'}
```
