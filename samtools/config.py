# ------------------------------------------------------------------------------
# Copyright 2022 by the U. S. Government as represented by the Administrator of
# the National Aeronautics and Space Administration.  All Other Rights Reserved.

# The 889 Compliance SAM Tool is licensed under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with the
# License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0.

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
# ------------------------------------------------------------------------------

"""
This module sets up the constants that will be used by the Flask application.
It reads in the last data a commit was added to the code from last_updated.txt.
The API key and contact email can be imported either from environment variables,
or from instance/samtools.cfg.
"""
from os import environ
import datetime
import pathlib
import json


def _get_version_string():
    version_file_name = "last_updated.txt"
    try:
        with open(version_file_name, "r", encoding="utf-8") as version_file:
            date_from_file = version_file.read().replace("Date:", "").strip()
        file_date_format = "%a %b %d %H:%M:%S %Y %z"
        return_date_format = "%B %d, %Y"
        formatted_datetime = (
            datetime.datetime.strptime(date_from_file, file_date_format)
            .astimezone(tz=datetime.timezone(datetime.timedelta(hours=-5)))
            .strftime(return_date_format)
        )
        return f"Website last updated {formatted_datetime}"
    except Exception as exception:
        raise Exception(
            f"Cannot read date string from file: {version_file_name}."
        ) from exception


def _get_recent_website_update_messages():
    messages_file_name = "recent_website_update_messages.json"
    if not pathlib.Path(messages_file_name).is_file:
        return None

    try:
        with open(messages_file_name, "r", encoding="utf-8") as messages_file:
            messages = json.load(messages_file)
    except Exception as exception:
        raise ValueError(f"Error in file {messages_file_name}") from exception

    try:
        messages[0]
    except Exception as exception:
        raise ValueError(f"{messages} is not a list") from exception

    for message in messages:
        if "message" not in message:
            raise ValueError(f"{message} does not contain key: 'message")

        if "expiration_date" not in message:
            raise ValueError(f"{message} does not contain key: 'expiration_date")

        try:
            message["expiration_date"] = datetime.datetime.strptime(
                message["expiration_date"], "%Y/%m/%d"
            )
        except Exception as exception:
            raise ValueError(
                f"expiration_date: '{message['expiration_date']}' "
                f"is not formatted as YYYY/MM/DD in {messages_file_name}"
            ) from exception

        if message.keys() != {"message", "expiration_date"}:
            raise ValueError(
                f"Unexpected key in {messages_file_name}: "
                f"{set(message.keys()).difference(set(['message', 'expiration_date']))}"
            )

    return messages


class Default:
    """Default constants for the application"""

    SAM_API_KEY = environ.get("SAM_API_KEY")
    CONTACT_EMAIL = environ.get("CONTACT_EMAIL", "")
    STATIC_FOLDER = "static"
    TEMPLATES_FOLDER = "templates"
    VERSION_STRING = _get_version_string()
    RECENT_WEBSITE_UPDATE_MESSAGES = _get_recent_website_update_messages()
    EXTERNAL_LINKS = {
        "SAM.GOV": "https://sam.gov",
        "SAM_ENTITIES_API_DOCS": "https://open.gsa.gov/api/entity-api/",
        "NF1883": "https://forms.neacc.nasa.gov/documents/11002/305376/NF1883.pdf",
    }
