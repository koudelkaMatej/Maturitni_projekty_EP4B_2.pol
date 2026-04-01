import requests

def login_do_hry():
    username = input("Zadej jméno: ")
    password = input("Zadej heslo: ")
    
    payload = {'username': username, 'password': password}
    response = requests.post("https://xeon.spskladno.cz/~podrazkj/space_invaders/check_login.php", data=payload)
    
    if response.text == "OK":
        print("Přihlášení úspěšné! Startuji motory...")
        return username
    else:
        print("Chyba přihlášení!")
        exit()

# Na konci hry pak pošleš skóre
def posli_skore(username, score):
    payload = {'username': username, 'score': score}
    requests.post("https://xeon.spskladno.cz/~podrazkj/space_invaders/save_score.php", data=payload)