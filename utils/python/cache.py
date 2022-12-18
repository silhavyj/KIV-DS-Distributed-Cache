import sys
import requests

if __name__ == '__main__':
    #argc = len(sys.argv)
    #if argc != 3:
    #    print("Invalid number of arguments")
    
    argv = sys.argv
    ip_addr = argv[1]
    op = argv[2].lower()
    
    if op == 'put':
        key = argv[3]
        value = argv[4]
        try:
            response = requests.put(f'http://{ip_addr}:5000/data', json = {'key' : key, 'value' : value})
            print(f'status_code: {response.status_code}')
            print(f'data: {response.json()}')
        except Exception as e:
            print(e)
    elif op == 'del':
        key = argv[3]
        try:
            response = requests.delete(f'http://{ip_addr}:5000/data', json = {'key' : key})
            print(f'status_code: {response.status_code}')
            print(f'data: {response.json()}')
        except Exception as e:
            print(e)
    elif op == 'get':
        key = argv[3]
        try:
            response = requests.get(f'http://{ip_addr}:5000/data', json = {'key' : key})
            print(f'status_code: {response.status_code}')
            print(f'data: {response.json()}')
        except Exception as e:
            print(e)