import schedule
import time




def job(t):
    print("I'm working...", t)
    #chiedo un report
    #se vi è troppo consumo, mettiamo in risparmio energetico

    return





schedule.every(2).seconds.do(job,'It is 01:00')

while True:
    schedule.run_pending()
    #time.sleep(60) # wait one minute