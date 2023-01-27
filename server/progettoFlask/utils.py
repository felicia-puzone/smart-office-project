import requests

def check_auth(key: str) -> dict:
    """Check if the user has priviledges

    Keyword arguments:
    key:str - Manager secret key
    Return:dict - JSON data
    """
    url = "http://127.0.0.1:5000/botAuth"
    params = {"key": key}
    response = requests.post(url, json = params)

    return response.json()

def send_report() -> dict:
    """Get energy consumption report
    Return:dict - JSON data
    """
    url = "http://127.0.0.1:5000/botReport"
    response = requests.get(url)

    return response
