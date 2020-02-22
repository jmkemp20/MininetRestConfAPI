import json

def is_integer(n):
    try:
        float(n)
    except ValueError:
        return False
    else:
        return float(n).is_integer()


def get_parser(url, get_data):

    if (url == '/'):
        return get_data

    data = json.loads(get_data)
    print(url[1:].split("/"))
    fields = url[1:].split("/")

    #return json.dumps(data['hosts'])
    ret = ""
    print(len(fields))

    try:
        if len(fields) == 1:
            ret = data[fields[0]]
        elif len(fields) == 2:
            if is_integer(fields[1]):
                ret = data[fields[0]][int(fields[1])]
            else:
                ret = data[fields[0]][fields[1]]
        elif len(fields) == 3:
            if is_integer(fields[1]):
                ret = data[fields[0]][int(fields[1])][fields[2]]
            else:
                ret = data[fields[0]][fields[1]][fields[2]]
        elif len(fields) == 4:
            if is_integer(fields[1]) & is_integer(fields[3]):
                ret = data[fields[0]][int(fields[1])][fields[2]][int(fields[3])]
            else:
                ret = data[fields[0]][int(fields[1])][fields[2]][fields[3]]
        elif len(fields) == 5:
            if is_integer(fields[3]):
                ret = data[fields[0]][int(fields[1])][fields[2]][int(fields[3])][fields[4]]
            else:
                ret = data[fields[0]][int(fields[1])][fields[2]][fields[3]][fields[4]]
        else:
            ret = data
    except:
        return "ERROR 400: Bad Request"

    print(ret)
    return json.dumps(ret)