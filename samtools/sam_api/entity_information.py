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
This is the main module that performs the calls to the SAM Entities API and returns the
 compliance information
"""

import requests
from flask import current_app

from samtools.compliance import compliance_rules
from samtools.sam_api.search_preprocessor import get_search_parameter


def search_sam_v3(search_args, host_url):
    """This is the main Sam Tool function which converts the parameters provided to the Sam Tool
    endpoint and to SAM Entities API parameters. The response from the SAM entities API is appended
    with the samToolsData section, which includes the 889 compliance, exclusions, and registration
    status information needed by the front-end.

    Args:
        search_args (dict): Sam Tools url search parameters
        host_url (str): The url of the this tool which will be included in the PDF download link

    Returns:
        dict: Contains the response data, otherwise returns the error messages
    """
    sam_api_endpoint = "https://api.sam.gov/entity-information/v3/entities"
    return _search_sam(search_args, host_url, sam_api_endpoint)


def _search_sam(search_args, host_url, sam_api_endpoint):
    data_adaptors = DataAdaptors()
    search_parameters = data_adaptors.adapt_samtools_to_sam_parameters(search_args)
    sam_response = _call_post_sam_entities_api(sam_api_endpoint, search_parameters)
    sam_response_data = sam_response.json()
    current_app.logger.info(sam_response.url)
    current_app.logger.info(sam_response.request.body)

    if not sam_response.ok:
        sam_error_message = (
            "SAM Entities API services cannot be accessed right now. Please try again later. "
            "This occurs when the SAM Entities API returns an error, is down for maintenance, "
            "or cannot be reached."
        )
        current_app.logger.error(sam_response.json())
        return {"success": False, "errors": [f"{sam_error_message}"]}

    entities = []
    for entity in sam_response_data.get("entityData"):
        eight_eight_nine = data_adaptors.adapt_sam_response_to_889_compliance(entity)
        exclusions = data_adaptors.adapt_sam_response_to_exclusions(entity)
        registration_status = data_adaptors.adapt_sam_response_to_registration_status(
            entity
        )
        entity = {
            **entity,
            **{
                "samToolsData": {
                    "isSelectable": _is_entity_selectable(
                        eight_eight_nine.is_compliant,
                        exclusions.has_exclusions,
                        registration_status.is_active,
                    ),
                    "pdfLinks": {
                        "entityPDF": f"{host_url}/api/file-download/summary?"
                        f"ueiSAM={entity['entityRegistration']['ueiSAM']}"
                        "&entityEFTIndicator="
                    },
                    "eightEightNine": {
                        "isCompliant": eight_eight_nine.is_compliant,
                        "statusText": eight_eight_nine.status_text,
                        "elaboratedStatusText": eight_eight_nine.elaborated_status_text,
                        "farProvisionDate": eight_eight_nine.far_provision_date,
                        "farText": {
                            "52.204-26.c.1": eight_eight_nine.far["52.204-26.c.1"][
                                "text"
                            ],
                            "52.204-26.c.2": eight_eight_nine.far["52.204-26.c.2"][
                                "text"
                            ],
                        },
                    },
                    "exclusions": {
                        "hasExclusions": exclusions.has_exclusions,
                        "statusText": exclusions.status_text,
                    },
                    "registration": {
                        "isActive": registration_status.is_active,
                        "statusText": registration_status.status_text,
                    },
                }
            },
        }

        entities.append(
            {
                section: entity[section]
                for section in search_parameters["includeSections"].union(
                    {"samToolsData"}
                )
            }
        )

    search_sam_response = {
        "entityData": entities,
        "totalRecords": sam_response_data["totalRecords"],
        "success": True,
    }
    return search_sam_response


def _call_post_sam_entities_api(sam_api_endpoint, search_parameters):
    """
    Users must have a Federal System Account with the “Read FOUO” permission and the respective API
    Key in SAM.gov.

    From: https://open.gsa.gov/api/entity-api

    Sensitive API Process:
    The System Account User ID and Password must be sent as "Basic Auth" under the "Authorization"
    Header.
    The combination needs to be base 64 encoded as base64(username:password).
    The API Key value must be sent as "x-api-key" under "Headers" and not directly in the request
    URL.
    The "Accept" parameter must be sent as "application/json" under "Headers".
    The "Content-Type" parameter must be sent as "application/json" under "Headers".
    All the optional search filters can be sent in the request URL or in the "Body".
    """
    header = {
        "X-api-key": _get_api_key_if_none_provided(search_parameters),
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    search_parameters.pop("api_key", None)
    return requests.post(
        sam_api_endpoint, headers=header, params=search_parameters, timeout=20
    )


def _call_get_sam_entities_api(sam_api_endpoint, search_parameters):
    search_parameters["api_key"] = _get_api_key_if_none_provided(search_parameters)
    return requests.get(sam_api_endpoint, search_parameters, timeout=20)


def _get_api_key_if_none_provided(search_args):
    sam_api_key = current_app.config["SAM_API_KEY"]
    return search_args.get("api_key", sam_api_key)


class DataAdaptors:
    """A data structure for organizational purposes only. Contains adaptors that convert from
    the SAM Entities API response to the respective Sam Tool data structures.
    """

    def adapt_samtools_to_sam_parameters(self, samtools_parameters):
        """Converts Sam Tools url parameters to SAM Entities API parameters

        Args:
            samtools_parameters (dict): SAM Tools url parameters

        Returns:
            dict: SAM Entities API url parameters
        """
        sam_parameters = dict(samtools_parameters)

        samtools_sections = samtools_parameters.get("includeSections", set([]))
        sam_parameters["includeSections"] = self._adapt_samtools_to_sam_sections(
            samtools_sections
        )

        samtools_search = sam_parameters.pop("samToolsSearch", "")
        sam_parameters.update(get_search_parameter(samtools_search))

        return sam_parameters

    def _adapt_samtools_to_sam_sections(self, samtools_sections):
        required_sections = set(["entityRegistration", "coreData", "repsAndCerts"])
        samtools_sections = self._parse_include_sections(samtools_sections)
        sam_sections = set.union(samtools_sections, required_sections)
        sam_sections.discard("samToolsData")
        return sam_sections

    @staticmethod
    def _parse_include_sections(include_sections):
        try:
            return set(include_sections.strip("[").strip("]").split(","))
        except Exception:
            return include_sections

    def adapt_sam_response_to_889_compliance(self, entity):
        """converts SAM Entities API response to a SAM Tools EightEightNine compliance object.

        Args:
            entity (dict): A single entity as returned by the SAM Entities API

        Returns:
            EightEightNine: EightEightNine compliance object
        """
        compliance = compliance_rules.EightEightNine()

        far_responses = self._get_far_responses(entity)
        if far_responses is None:
            return compliance

        far52_204_26 = self._get_far_52_204_26(far_responses)

        compliance.set_far(
            "52.204-26.c.1", self._get_far_52_204_26_c_1_answer(far52_204_26)
        )

        compliance.set_far(
            "52.204-26.c.2", self._get_far_52_204_26_c_2_answer(far52_204_26)
        )

        return compliance

    @staticmethod
    def _get_far_responses(entity):
        if "repsAndCerts" not in entity:
            return None
        if "certifications" not in entity["repsAndCerts"]:
            return None
        return entity["repsAndCerts"]["certifications"].get("fARResponses", None)

    @staticmethod
    def _get_far_52_204_26(far_responses):
        key = "provisionId"
        value = "FAR 52.204-26"
        return _get_dict_from_list_of_dicts(far_responses, key, value)

    @staticmethod
    def _get_far_52_204_26_c_1_answer(far52_204_26):
        key = "section"
        value = "52.204-26.c.1"
        return _get_dict_from_list_of_dicts(far52_204_26["listOfAnswers"], key, value)[
            "answerText"
        ]

    @staticmethod
    def _get_far_52_204_26_c_2_answer(far52_204_26):
        key = "section"
        value = "52.204-26.c.2"
        return _get_dict_from_list_of_dicts(far52_204_26["listOfAnswers"], key, value)[
            "answerText"
        ]

    @staticmethod
    def adapt_sam_response_to_exclusions(entity):
        """Convert SAM Entities API response to a SAM Tools Exclusions object.

        Args:
            entity (dict): A single entity as returned by the SAM Entities API

        Returns:
            Exclusions: Exclusions object
        """
        if "entityRegistration" not in entity:
            return compliance_rules.Exclusions()
        if "exclusionStatusFlag" not in entity["entityRegistration"]:
            return compliance_rules.Exclusions()
        flag = entity["entityRegistration"]["exclusionStatusFlag"]
        return compliance_rules.Exclusions(flag)

    @staticmethod
    def adapt_sam_response_to_registration_status(entity):
        """Convert SAM Entities API response to a SAM Tools Registration object.

        Args:
            entity (dict): A single entity as returned by the SAM Entities API

        Returns:
            RegistrationStatus: RegistrationStatus object
        """
        if "entityRegistration" not in entity:
            return compliance_rules.RegistrationStatus()
        if "registrationStatus" not in entity["entityRegistration"]:
            return compliance_rules.RegistrationStatus()
        registration_status = entity["entityRegistration"]["registrationStatus"]
        return compliance_rules.RegistrationStatus(registration_status)


def _is_entity_selectable(is_compliant, has_exclusions, is_active):
    if is_compliant and not has_exclusions and is_active:
        return True
    return False


def _get_dict_from_list_of_dicts(list_of_dicts, key_name, value):
    return next((dict_i for dict_i in list_of_dicts if dict_i[key_name] == value), None)
