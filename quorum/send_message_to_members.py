import os
import sys

dir_name = os.path.dirname(os.path.realpath(__file__))
sys.path.append(f"{dir_name}/../common_utils")

from church_of_jesus_christ_api import ChurchOfJesusChristAPI as API
from termux_SMS_handler import termux_SMS_handler as Message_handler
from generic_utils import format_phone_number, format_email, get_basic_formal_name, read_ignore_file
import time

try:
    from set_environment import set_environment

    set_environment()
except ImportError:
    pass


def send_group_message():

    api = API(
        username=os.environ["CHURCH_USERNAME"], password=os.environ["CHURCH_PASSWORD"]
    )
    member_list = api.get_member_list()
    quorum_list = api.get_suborganization()["members"]
    missionary_ids = {missionary["missionaryIndividualId"] for missionary in api.get_full_time_missionaries()}
    message_sender = Message_handler()

    quorum_ids = {brother["id"] for brother in quorum_list if brother["id"] not in missionary_ids}

    with open("message.txt") as message_file:
        base_message = message_file.read()
    do_not_text = read_ignore_file("do_not_text.txt")

    number_member_map = {
        format_phone_number(member["phoneNumber"]): member for member in member_list \
            if member["legacyCmisId"] in quorum_ids and \
               member["phoneNumber"] != None and \
               format_phone_number(member["phoneNumber"]) not in do_not_text           
    }

    emails = {
        format_email(member["email"]) for member in member_list \
            if member["legacyCmisId"] in quorum_ids and \
               member["email"] != None and \
               format_phone_number(member["phoneNumber"]) not in do_not_text
    }

    print("Not texting", do_not_text)
    print(', '.join(emails))
    for number, member in number_member_map.items():
        name = get_basic_formal_name(member)
        message = name + ",\n" + base_message
        time.sleep(3)
        message_sender.send_SMS(number, message)
        print(message)


if __name__ == "__main__":
    os.chdir(dir_name)
    send_group_message()
