"""
基于Flask的API框架

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

    def my_validator(*args, *kwargs):
        def validator(value):
            pass
        return validator
    api = Fighting(__name__, validators={'name': my_validator})
"""
import collections
import functools
import json
import os
import re
import textwrap
from collections import OrderedDict

from flask import abort as flask_abort
from flask import Flask, jsonify, request
from jinja2 import Template
from markdown import markdown as origin_markdown
from validr import Invalid, SchemaError, SchemaParser
from validr.schema import MarkKey

import simple_yaml as yaml

RE_DIRECTIVE = re.compile(r'[\t ]*\$\w+:')
RE_SHARED = re.compile(r'[\t ]*\@\w+:')

_DOC_PATH = os.path.join(os.path.dirname(__file__), 'document.jinja2')
with open(_DOC_PATH) as f:
    _DOC_TMPL = Template(f.read())


def dumps(v):
    return json.dumps(v, ensure_ascii=False, indent=4)


def markdown(text):
    """用Markdown解析文档"""
    extensions = ['nl2br', 'tables', 'fenced_code']
    return origin_markdown(text, extensions=extensions)


def render(desc='', shared=None, resources=None, directives=None):
    """渲染文档"""
    desc = markdown(desc)
    if shared is None:
        shared = OrderedDict()
    else:
        shared = OrderedDict([(k, dumps(v))for k, v in shared.items()])
    if resources is None:
        resources = OrderedDict()
    else:
        resources = OrderedDict(sorted(resources.items(), key=lambda x: x[0]))
    if directives is None:
        directives = OrderedDict()
    else:
        directives = OrderedDict([(k, dumps(v))for k, v in directives.items()])
    return _DOC_TMPL.render(
        desc=desc, shared=shared, directives=directives, resources=resources)


def accept_json():
    """判断客户端是否接受JSON响应"""
    mediatype = request.accept_mimetypes.best_match(
        ['text/html', 'application/json'], default='text/html')
    return mediatype == 'application/json' or 'json' in request.args


def abort(message):
    """
    Abort with 400 response

    Args:
        message (str): 错误提示
    """
    response = jsonify(message)
    response.status_code = 400
    flask_abort(400, response=response)


def get_request_data():
    """Get request data based on request mimetype"""
    if request.mimetype == 'application/json':
        try:
            data = request.get_json()
        except:
            abort("Invalid JSON content")
        if not isinstance(data, collections.Mapping):
            abort("JSON content must be object")
        return data
    else:
        return request.form


def _parse_doc(doc, mark):
    """
    Parse YAML syntax data from doc

    if doc is None, return ('', OrderedDict())
    if doc has no YAML data, return (doc, OrderedDict())
    else, parse YAML data, return (doc, data)

    Args:
        doc (str): doc to be parsed
        mark (Regex): which marks the start position of data
    Returns:
        tuple(desc, data): data is an OrderedDict contains information of doc
    """
    if doc is None:
        return '', OrderedDict()
    match = mark.search(doc)
    if not match:
        return textwrap.dedent(doc).strip(), OrderedDict()
    start = match.start()
    yamltext = textwrap.dedent(doc[start:])
    try:
        data = yaml.load(yamltext)
    except yaml.parser.ParserError as ex:
        raise SchemaError(str(ex)) from None
    return textwrap.dedent(doc[:start]).strip(), data


def parse_directive(doc):
    """Parse directive from doc"""
    desc, data = _parse_doc(doc, RE_DIRECTIVE)
    directives = OrderedDict()
    for k, v in data.items():
        if k.startswith("$"):
            directives[k[1:]] = v
        else:
            raise ValueError("Invalid directive {}".format(k))
    return desc, directives


def parse_shared(doc):
    """Parse shared from doc"""
    desc, data = _parse_doc(doc, RE_SHARED)
    shared = OrderedDict()
    for k, v in data.items():
        if k.startswith("@"):
            shared[k[1:]] = v
        else:
            raise ValueError("Invalid shared {}".format(k))
    return desc, shared


def get_title(doc):
    """Get title of doc"""
    if not doc:
        return ''
    lines = doc.strip('\n').split('\n', maxsplit=1)
    title = lines[0].strip()
    if len(title) > 20:
        title = title[:20] + '...'
    return title


def input_directive(f, meta, api):
    """$input指令"""
    def view():
        try:
            data = validate(get_request_data())
        except Invalid as ex:
            abort(str(ex))
        return f(**data)
    with MarkKey('$input'):
        validate = api.schema_parser.parse(meta)
    return view


def output_directive(f, meta, api):
    """$output指令"""
    def view(*args, **kwargs):
        return validate(f(*args, **kwargs))
    with MarkKey('$output'):
        validate = api.schema_parser.parse(meta)
    return view


class Fighting(Flask):

    def __init__(self, *args, validators=None, directives=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.config['JSON_AS_ASCII'] = False
        self._directives = {
            'input': input_directive,
            'output': output_directive
        }
        if directives:
            self._directives.update(directives)
        self._resources = {}
        self._desc, self._shared = parse_shared(
            __import__(self.import_name).__doc__)
        self.schema_parser = SchemaParser(
            validators=validators, shared=self._shared)
        self.route('/')(self._doc)

    def _doc(self):
        """API文档"""
        params = dict(
            desc=self._desc,
            resources=self._resources,
            shared=self._shared
        )
        if accept_json():
            return jsonify(params)
        else:
            return render(**params)

    def res(self, resource):
        """添加路由"""
        def decorater(f):
            action = f.__name__
            endpoint = '{}.{}'.format(resource, action)
            url = '/{}/{}'.format(resource, action)
            self._resources.setdefault(resource, [])\
                .append({'title': get_title(f.__doc__), 'url': url})
            with MarkKey(endpoint):
                view = self.make_view(f)
            return self.route(url, methods=['GET', 'POST'],
                              endpoint=endpoint)(view)
        return decorater

    def make_view(self, f):
        """将action转成view"""
        origin = f
        desc, directives = parse_directive(f.__doc__)
        for directive, meta in directives.items():
            f = self._directives[directive](f, meta, self)

        @functools.wraps(origin)
        def view():
            if request.method == 'POST':
                response = f()
                if isinstance(response, self.response_class):
                    return response
                return jsonify(response)
            elif request.method == 'GET':
                if accept_json():
                    return jsonify(desc=desc, directives=directives)
                else:
                    return render(desc=desc, directives=directives)
            else:
                flask_abort(405)
        return view
