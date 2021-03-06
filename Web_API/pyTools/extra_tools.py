# extra tools that can be useful in any project #


'''
    a function that parses a yml and returns a value
    corresponding to the key/keychain supplied
    example for execution: 

 admin_cred = get_Conf(['DBs','products','db_cred'])
 will return admin mysql cred to access the db named products
 in a .yml that looks like this
 DBs:
    products:
        db_cred:
        host: localhost
        user: ori
        password: 123456
        tables:
        - music
        - movies
'''
def get_conf(*key_list):
    import yaml
    conf = yaml.safe_load(open('./config.yml'))
    try:
        for key in list(key_list[0]):
            conf = conf[key]
    except KeyError:
        return "ERROR: one of the keys given does NOT exist"
    return conf

def fix_json_quotings(string):
    from json import loads
    fixed_string = string.replace("'", '"')
    fixed_json = loads(fixed_string)
    return(fixed_json)

def list_of_tuples_to_list_of_lists(lst):
    new_list = []
    for tup in lst:
        new_list.append(list(tup))
    return new_list