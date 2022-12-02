import re
import csv
import json
import inspect
import datetime


def get_basic_formal_name(record):
    gender_title = "Brother" if record["sex"] == "M" else "Sister"
    family_name = record['householdMember']['household']['familyNameLocal']
    return f"{gender_title} {family_name}"

def is_birthday(birthday_str):  # in form YYYYMMDD
    if not isinstance(birthday_str, str):
        return False

    if not re.match(r"^[0-9]{8}$", birthday_str):
        return False
    now = get_time()
    month = int(birthday_str[4:6])
    day = int(birthday_str[6:])

    # Special leap day case
    if month == 2 and day == 29:
        day = 28

    if month == now.month and day == now.day:
        return True

    return False


def is_yesterday(day_str):  # in form YYYYMMDD
    if not isinstance(day_str, str):
        return False

    if not re.match(r"^[0-9]{8}$", day_str):
        return False
    yesterday = get_time() - datetime.timedelta(days=1)
    year = int(day_str[0:4])
    month = int(day_str[4:6])
    day = int(day_str[6:])

    if year == yesterday.year and month == yesterday.month and day == yesterday.day:
        return True

    return False


def split_string_len(string, length):
    return [string[i : i + length] for i in range(0, len(string), length)]


def get_first_name(full_name):
    if not isinstance(full_name, str):
        return ""

    given_names = full_name.split(", ")[1]
    first_name = given_names.split(" ")[0]
    return first_name


def scrub_table_name(table_name):
    return "".join(chr for chr in table_name if chr.isalnum())


def get_time():
    return datetime.datetime.now()


def parse_time(python_iso_str):
    return datetime.datetime.strptime(python_iso_str, "%Y-%m-%dT%H:%M:%S.%f")


def minutes_dif(time1, time2):
    return abs((time1 - time2) / datetime.timedelta(minutes=1))


def function_name():
    return inspect.getouterframes(inspect.currentframe())[1].function


def format_phone_number(phone_number):
    # strip all characters out except digits
    if phone_number is None:
        return ""
    ret_val = re.sub("[^0-9]", "", phone_number)
    # if country code is included for USA, remove it
    if (len(ret_val) == 11) and (ret_val[0] == "1"):
        ret_val = ret_val[1:]
    # if phone number is invalid, print an error message and return empty string
    if (len(ret_val) < 10) and (ret_val != ""):
        ret_val = ""
    return ret_val


def format_email(email):
    return email.lower() if email != None else ""


def create_phone_number_csv(member_list, filename):
    phone_num_set = set()
    for member in member_list:
        phone_num_set.add(member["phone"])
        phone_num_set.add(member["householdPhone"])
    phone_num_set.remove("")
    csv_writer = csv.writer(open(filename, "w"))
    csv_writer.writerow(list(phone_num_set))


def create_email_csv(member_list, filename):
    create_email_csv(member_list, open(filename, "w"))


def create_email_csv_with_file(member_list, file, include_household_email=True):
    email_set = set()
    for member in member_list:
        email_set.add(member["email"].lower() if member["email"] != None else "")
        if include_household_email:
            email_set.add(
                member["householdEmail"].lower()
                if member["householdEmail"] != None
                else ""
            )
    email_set.remove("")
    csv_writer = csv.writer(file)
    csv_writer.writerow(sorted(list(email_set)))


def JSON_to_string(json_obj):
    return json.dumps(json_obj, indent=2, sort_keys=True)


def read_ignore_file(filename):
    with open(filename) as file:
        return [line.split("#")[0].strip() for line in file.readlines()]


def get_quarter(date):
    return ((date.month - 1) // 3), date.year
