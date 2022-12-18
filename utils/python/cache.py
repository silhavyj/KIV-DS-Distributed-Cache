import sys
import requests


def print_help():
    print('GET:    python3 cache.py <ip_addr> get <key>')
    print('PUT:    python3 cache.py <ip_addr> put <key> <value>')
    print('DELETE: python3 cache.py <ip_addr> delete <key>')


if __name__ == '__main__':
    try:
        argv = sys.argv
        ip_addr = argv[1]
        op = argv[2].lower()
        key = argv[3]
        
        if op == 'get':
            response = requests.get(f'http://{ip_addr}:5000/data?key={key}')
        elif op == 'put':
            value = argv[4]
            response = requests.put(f'http://{ip_addr}:5000/data?key={key}&value={value}')
        elif op == 'delete':
            response = requests.delete(f'http://{ip_addr}:5000/data?key={key}')
        else:
            print("Invalid arguments")
            print_help()
            exit()
            
        print(f'status_code: {response.status_code}')
        print(f'data: {response.text.strip()}')
    except Exception as e:
        print(e)
        print()
        print_help()