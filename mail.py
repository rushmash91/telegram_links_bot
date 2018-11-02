import smtplib
from sensitive import *


def send_mail(to, subject, body, my=me):
    smt = smtplib.SMTP('smtp.gmail.com', 587)
    smt.ehlo()
    smt.starttls()
    smt.login(user=my, password=pwd)

    sub = subject
    body = body
    message = "Subject: " + sub + "\n" + body + "\n"

    smt.sendmail(my, to, message)
    smt.quit()


def main():
    to = 'ahrfg.ksegg91@gmail.com'
    sub = 'hi'
    body = 'hello'
    send_mail(to, sub, body)


if __name__ == '__main__':
    main()
