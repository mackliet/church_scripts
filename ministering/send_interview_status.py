import os
import sys

dir_name = os.path.dirname(os.path.realpath(__file__))
sys.path.append(f"{dir_name}/../common_utils")

from church_of_jesus_christ_api import ChurchOfJesusChristAPI as API
from termux_SMS_handler import termux_SMS_handler as Message_handler
from generic_utils import (
    format_phone_number,
    get_basic_formal_name,
    get_quarter,
    get_time,
)
from dateutil import parser
import time
import json

try:
    from set_environment import set_environment

    set_environment()
except ImportError:
    pass


def brother_interviewed_this_quarter(current_quarter, brother):
    return "interviews" in brother and any(
        current_quarter == get_quarter(parser.parse(interview["date"]))
        for interview in brother["interviews"]
    )


def companionship_needs_interview(current_quarter, comp):
    return not any(
        map(
            lambda brother: brother_interviewed_this_quarter(current_quarter, brother),
            comp["ministers"],
        )
    )


def companionships_that_need_interview(current_quarter, district):
    return [
        comp["ministers"]
        for comp in district["companionships"]
        if companionship_needs_interview(current_quarter, comp)
    ]


def get_supervisor_info(district, member_list):
    supervisor = next(
        member
        for member in member_list
        if member["legacyCmisId"] == district["supervisorLegacyCmisId"]
    )
    return {
        "phone": format_phone_number(supervisor["phoneNumber"]),
        "name": get_basic_formal_name(supervisor),
    }


def send_group_message():

    api = API(
        username=os.environ["CHURCH_USERNAME"], password=os.environ["CHURCH_PASSWORD"]
    )
    member_list = api.get_member_list()
    ministering_full = api.get_ministering_full()["elders"]
    current_quarter = get_quarter(get_time())

    remaining_interview_info = [
        {
            "supervisor": get_supervisor_info(district, member_list),
            "brothers": [
                [" ".join(reversed(brother["name"].split(", "))) for brother in comp]
                for comp in companionships_that_need_interview(
                    current_quarter, district
                )
            ],
        }
        for district in ministering_full
    ]

    messages_to_send = {
        info["supervisor"][
            "phone"
        ]: f'{info["supervisor"]["name"]}, you have {len(info["brothers"])} companionships left to interview this quarter:\n\n'
        + "\n".join(" and ".join(comp) for comp in info["brothers"])
        + "\n\nWhen would you like me to set up interviews for you this week?"
        for info in remaining_interview_info
        if info["brothers"]
    }

    message_sender = Message_handler()
    for number, message in messages_to_send.items():
        message_sender.send_SMS(number, message)
        time.sleep(3)


if __name__ == "__main__":
    os.chdir(dir_name)
    send_group_message()
