import requests
import schedule

def update():
    try:
        requests.post('http://127.0.0.1:5000/systemUpdate/',data={'pippo':2})
    except requests.exceptions.RequestException as e:
        print("Non ho aggiornato")

    return 0






schedule.every(30).days.do(update)

#schedule.every(60/time_constant).minutes.do(hour_count)
while True:
    schedule.run_pending()







