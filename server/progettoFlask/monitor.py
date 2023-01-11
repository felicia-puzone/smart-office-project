import schedule


def day_report():
    print("I'm working...")
    #chiedo un report
    #se vi è troppo consumo, mettiamo in risparmio energetico

    return



schedule.every(1).days.do(day_report())

while True:
    schedule.run_pending()
    #time.sleep(60) # wait one minute