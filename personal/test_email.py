import smtplib

sender = "Private Person <mailtrap@demomailtrap.com>"
receiver = "A Test User <yash.aggy@gmail.com>"

message = f"""\
Subject: Hi Mailtrap
To: {receiver}
From: {sender}

This is a test e-mail message."""

with smtplib.SMTP("live.smtp.mailtrap.io", 587) as server:
    server.starttls()
    server.login("api", "0c51efc1b8ee06372e37b2b4085cca8e")
    server.sendmail(sender, receiver, message)