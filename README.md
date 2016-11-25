# Fighting

A simple JSON API web framework based on Flask

- GET请求查看文档，POST请求调用API
- 校验输入，序列化输出
- 支持自定义指令，自定义校验器

Usage:

    ###
    整个API的介绍

    $shared:
        共享的数据格式
    ###
    from fighting import Fighting

    api = Fighting(__name__)   # Fighting是Flask的子类

    @api.res('resource')       # 添加路由，URL为'/resource/action'
    def action():
        ###
        文档字符串中，以$开头的YAML文本表示指令

        $input:
            输入格式
        $output:
            输出格式
        ###
        return 'Hello World'   # 自动序列化为JSON内容

Helpers:

    from fighting import abort

    abort(message)  # 状态码为400，内容为"message"

Directive:

    def my_directive(f, meta, api):
        def view():
            pass
        return view
    api = Fighting(__name__, directives={'name': my_directive})

Validator:

    def my_validator(*args, **kwargs):
        def validator(value):
            pass
        return validator
    api = Fighting(__name__, validators={'name': my_validator})
