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
