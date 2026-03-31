import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
URL_BASE = "https://xeon.spskladno.cz/~trzyniek/"

def login_user(username, password):
    try:
        url = f"{URL_BASE.rstrip('/')}/index.php"
        response = requests.post(
            url, 
            data={'username': username, 'password': password, 'login_user': '1'}, 
            timeout=10,
            verify=False,
            allow_redirects=False 
        )
        if response.status_code == 302:
            return {"status": "success", "username": username}
        return {"status": "error", "message": "Neplatné jméno nebo heslo!"}
    except:
        return {"status": "error", "message": "Chyba připojení k serveru"}

def update_high_score(username, score):
    try:
        url = f"{URL_BASE.rstrip('/')}/save_score.php"
        data_to_send = {'username': username, 'score': int(score)}
        requests.post(url, data=data_to_send, timeout=5, verify=False)
    except:
        pass