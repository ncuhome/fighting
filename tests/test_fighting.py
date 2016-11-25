"""
@message:
    message?str: Message
"""
import json

import pytest

from fighting import Fighting


@pytest.fixture
def api():
    api = Fighting(__name__)

    @api.res('resource')
    def action(name):
        """
        测试

        $input:
            name?str: Name
        $output: @message
        """
        return {'message': name}
    return api


@pytest.fixture
def client(api):
    with api.test_client() as c:
        yield c


def test_invalid(api):

    with pytest.raises(Exception):
        @api.res('resource')
        def invalid1(name):
            """
            测试

            $input:
            invalid YAML
            """
            pass

    with pytest.raises(Exception):
        @api.res('resource')
        def invalid2(name):
            """
            测试

            $unknown:
                name?str: Name
            """
            pass


def test_basic(client):
    resp = client.get('/resource/action')
    assert resp.status_code == 200
    resp = client.post('/resource/action', data={'name': 'kk'})
    assert resp.status_code == 200
    assert json.loads(resp.data.decode('utf-8')) == {'message': 'kk'}
    data = json.dumps({'name': 'kk'}, ensure_ascii=False).encode('utf-8')
    headers = {'content-type': 'application/json'}
    resp = client.post('/resource/action', data=data, headers=headers)
    assert resp.status_code == 200
    assert json.loads(resp.data.decode('utf-8')) == {'message': 'kk'}


def test_doc(client):
    resp = client.get('/')
    assert resp.status_code == 200
    resp = client.get('/?json')
    assert resp.status_code == 200
    assert resp.mimetype == 'application/json'
    headers = {'accept': 'application/json'}
    resp = client.get('/', headers=headers)
    assert resp.status_code == 200
    assert resp.mimetype == 'application/json'


def test_invalid_json(client):
    headers = {'content-type': 'application/json'}
    resp = client.post('/resource/action', data='', headers=headers)
    assert resp.status_code == 400
    resp = client.post('/resource/action', data='[1,2,3]', headers=headers)
    assert resp.status_code == 400
