import requests, json, pytest, time, multiprocessing
from functools import partial

# POST_TESTS
#========================================================#
'''
    1 - a normal request that should work
    2 - a request with a non existing column
    3 - a request with an empty json
    4 - a request with no json at all
'''
@pytest.mark.parametrize('body,expected', [
    ({'username': 'gabi', 'password': '123456'}, 200),
    ({'username': 'gabi', 'paword': '123456'}, 400),
    ({}, 400),
    (None, 400)
    ])
def test_post_json_variations(body, expected):
    url = 'http://localhost/users/admins'
    headers = {'Content-Type': 'application/json'}
    
    resp = requests.post(url=url, headers=headers, data=json.dumps(body,indent=4))       
    
    # Validate response headers and body contents, e.g. status code.
    assert resp.status_code == expected
    
    # print response full body as text
    print(resp.text)

'''
    1 - a normal url that should work
    2 - a url to a non existing table
    3 - a url that doesnt contain a table
    4 - a url already containing a record id
'''
@pytest.mark.parametrize('url,expected', [
    ('http://localhost/users/admins', 200),
    ('http://localhost/users/admi', 400),
    ('http://localhost/users', 404),
    ('http://localhost/users/admins/13', 405 ),
    ])
def test_post_url_variations(url,expected):
    # assigning a json header as a default case
    headers = {'Content-Type': 'application/json'}
    # assigning a json load as a default case as this is a url test
    body = {'username': 'ori', 'password': 1234}
    resp = requests.post(url=url, headers=headers, data=json.dumps(body,indent=4))       
    
    # Validate response headers and body contents, e.g. status code.
    assert resp.status_code == expected
#========================================================#
# PUT_TESTS
#========================================================#
'''
    1 - put request with a normal json
    2 - put request with deformed json
    3 - put request with an empty json
    4 - put request with no json
'''
@pytest.mark.parametrize('body,expected', [
    ({'username': 'pytested', 'password': '1pytested1'}, 200),
    ({'username': 'gabi', 'paword': '123456'}, 400),
    ({}, 400),
    (None, 400)
    ])
def test_put_json_variations(body,expected):
    url = 'http://localhost/users/admins/1'
    headers = {'Content-Type': 'application/json'}
    
    resp = requests.put(url=url, headers=headers, data=json.dumps(body,indent=4))       
    
    # Validate response headers and body contents, e.g. status code.
    assert resp.status_code == expected

'''
    1 - a normal url that should work 
    2 - a url to a non existing table with an id
    3 - a url without an id
    4 - same as above but with small variation
    3 - a url that doesnt contain a table
    4 - same as above but with small variation
'''
@pytest.mark.parametrize('url,expected', [
    ('http://localhost/users/admins/1', 200),
    ('http://localhost/users/admin/1', 400),
    ('http://localhost/users/admins/', 404),
    ('http://localhost/users/admins', 405),
    ('http://localhost/users/', 404),
    ('http://localhost/users', 404),
    ])
def test_put_url_variations(url,expected):
    # assigning a json header as a default case
    headers = {'Content-Type': 'application/json'}
    # assigning a json load as a default case as this is a url test
    body = {'username': 'ori', 'password': 1234}
    resp = requests.put(url=url, headers=headers, data=json.dumps(body,indent=4))       
    
    # Validate response headers and body contents, e.g. status code.
    assert resp.status_code == expected
#========================================================#
# DELETE_TESTS
#========================================================#
'''
    1 - requesting a delete with a normal expected url
    2 - requesting a delete without assigning an id
    3 - requesting a delete without assigning an id, formatting the url a little different
    4 - requesting a delete without assigning an id to a non existing table
    5 - requesting a delete with an id to a non existing table
    6 - requesting a delete without assigning a table
    7,8 - same as above with little variations 
'''
@pytest.mark.parametrize('url,expected', [
    ('http://localhost/users/admins/1', 200),
    ('http://localhost/users/admins/134634463346436', 200),
    ('http://localhost/users/admins', 405),
    ('http://localhost/users/admins/', 404),
    ('http://localhost/users/admi', 405),
    ('http://localhost/users/admi/12', 400),
    ('http://localhost/users', 404),
    ('http://localhost/user', 404),
    ('http://localhost/users/', 404),
    ])
def test_delete_url_variations(url, expected):
    resp = requests.delete(url=url)

    # Validate response headers and body contents, e.g. status code.
    assert resp.status_code == expected
#========================================================#
# GET_TESTS
#========================================================#
'''
    1 - a request with a normal expected json, containing one filter
    2 - a request with an empty json, no filter  - returning the whole table
    3 - a request with a deformed json
    4 - a request with no json.
'''
@pytest.mark.parametrize('body,expected', [
    ({"username": "ori"}, 200),
    ({}, 200),
    ({"usernme": "ori"}, 400),
    (None, 400)
    ])
def test_get_json_variations(body, expected):
    url = 'http://localhost/users/admins'
    headers = {'Content-Type': 'application/json'}
    
    resp = requests.get(url=url, headers=headers, data=json.dumps(body,indent=4))       
    
    # Validate response headers and body contents, e.g. status code.
    assert resp.status_code == expected


@pytest.mark.parametrize('url,expected', [
    ('http://localhost/users/admins/2', 200),
    ('http://localhost/users/admin/1', 400),
    ('http://localhost/users/admins/', 404),
    ('http://localhost/users/admins', 200),
    ('http://localhost/users/', 404),
    ('http://localhost/users', 404),
    ])
def test_get_url_variations(url,expected):
    # assigning a json header as a default case
    headers = {'Content-Type': 'application/json'}
    # assigning a json load as a default case as this is a url test
    body = {'username': 'ori'}
    resp = requests.get(url=url, headers=headers, data=json.dumps(body,indent=4))       
    
    # Validate response headers and body contents, e.g. status code.
    assert resp.status_code == expected


#========================================================#
# PERFORMANCE_TESTS
#========================================================#


def send_req():
    body = {'username': 'gabi', 'password': '123456'}

    url = 'http://localhost/users/admins'
    headers = {'Content-Type': 'application/json'}
    
    resp = requests.post(url=url, headers=headers, data=json.dumps(body,indent=4))

def test_performance_many_at_once():
    start_time = time.time()

    pool = multiprocessing.Pool()
    for _ in range(500):
        pool.apply_async(send_req)
    pool.close()
    pool.join()

    elapsed_time = time.time() - start_time
    assert elapsed_time <= 15