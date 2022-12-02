from subprocess import run


class termux_SMS_handler:
    def send_SMS(self, number, message):
        run(["termux-sms-send", "-n", number, message]).check_returncode()


if __name__ == "__main__":
    termux_SMS_handler().send_SMS(
        input("Input a phone number to send a test message: "), "TEST MESSAGE"
    )
