import os
import sys

dir_name = os.path.dirname(os.path.realpath(__file__))
sys.path.append(f"{dir_name}/../common_utils")

from termux_SMS_handler import termux_SMS_handler as Message_handler
import time
import json
from generic_utils import format_phone_number, format_email, read_ignore_file
from collections import defaultdict

try:
    from set_environment import set_environment

    set_environment()
except ImportError:
    pass


def get_first_name(person):
    return person["name"].split(", ")[1].split(" ")[0]


def send_group_message():
    with open("mission_prep_youth.json") as youth_file:
        youth_list = json.load(youth_file)
    do_not_text = [
        format_phone_number(number) for number in read_ignore_file("do_not_text.txt")
    ]
    do_not_email = [email.lower() for email in read_ignore_file("do_not_email.txt")]

    number_person_map = defaultdict(list)
    all_emails = set()
    number_skipped = 0
    for person in youth_list:
        numbers = set(format_phone_number(number) for number in [person.get("phone"), person.get("household_phone")] if number != None)
        emails = set(format_email(email) for email in [person.get("email"), person.get("household_email")] if email != None)

        if any(number in do_not_text for number in numbers) or any(
            email in do_not_email for email in emails
        ):
            print(f'Skipping {person["name"]}')
            number_skipped += 1
            continue

        for number in numbers:
            number_person_map[number].append(get_first_name(person))
        all_emails = all_emails.union(emails)

    print(",".join(all_emails))
    print(f"{len(youth_list)} people in the text/email list")
    print(f"{len(do_not_text)} numbers ignored")
    print(f"{len(all_emails)} emails sent each week")
    print(f"{len(number_person_map)} texts sent each week")

    num_people = len(youth_list) - number_skipped
    print(f"{num_people} each week")

    with open("message.txt") as message_file:
        message = message_file.read()

    print(message)
    message_sender = Message_handler()
    for number, names in number_person_map.items():
        names_string = "/".join(names)
        message_to_send = "\n".join([names_string, message])
        time.sleep(3)
        message_sender.send_SMS(number, message_to_send)
        print(message_to_send)


if __name__ == "__main__":
    os.chdir(dir_name)
    send_group_message()
