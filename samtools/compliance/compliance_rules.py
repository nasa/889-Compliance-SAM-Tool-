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
This module contains all of the compliance objects
"""
from collections import defaultdict


class EightEightNine:
    """An object that contains the vendor 889 compliance information."""

    def __init__(self):
        self._far_provision = {
            "52.204-26.c.1": "(1) The Offeror represents that it {answer} "
            "provide covered telecommunications equipment or services as "
            "a part of its offered products or services to the Government "
            "in the performance of any contract, subcontract, or other "
            "contractual instrument.",
            "52.204-26.c.2": "(2) After conducting a reasonable inquiry for "
            "purposes of this representation, the offeror represents that "
            "it {answer} use covered telecommunications equipment or "
            "services, or any equipment, system, or service that uses "
            "covered telecommunications equipment or services.",
        }
        self._answer_to_provision_text_mapping = {
            "No".title(): "DOES NOT",
            "Yes".title(): "DOES",
        }
        self._far = defaultdict(lambda: {"text": None, "answer": None})

    def set_far(self, provision_id, provision_answer):
        """Set a far provision in the EightEightNine object

        Args:
            provision_id (str): The far provision to be set. For example: '52.204-26.c.1
            provision_answer (str): 'Yes' or 'No'.

        Raises:
            ValueError:
        """
        if provision_id not in self._far_provision:
            raise ValueError(f"{provision_id} not in {self._far_provision.keys()}")

        answer = self._answer_to_provision_text_mapping[provision_answer.title()]

        self._far[provision_id]["answer"] = answer
        self._far[provision_id]["text"] = self._far_provision[provision_id].format(
            answer=answer
        )

    @property
    def is_compliant(self):
        """Is the entity 889 compliant.

        Returns:
            Bool:
        """
        if self._has_far_part_c1 and self._has_far_part_c2:
            if (
                self.far["52.204-26.c.1"]["answer"] == "DOES NOT"
                and self.far["52.204-26.c.2"]["answer"] == "DOES NOT"
            ):
                return True
        return False

    @property
    def far(self):
        """The FAR text with answers as submitted by the entity

        Returns:
            str: Complete FAR text with answers
        """
        return self._far.copy()

    @property
    def status_text(self):
        """Summary of if the entity is compliant and it not, provide a brief description of why now

        Returns:
            str: Brief description of the entity compliance status
        """
        if self.is_compliant:
            return "COMPLIANT"
        if not self._has_far_response:
            return "NO REPS & CERTS"
        if not self._has_far_part_c2:
            return "OUTDATED FAR (No part (C)(2))"
        if (
            self.far["52.204-26.c.1"]["answer"] == "DOES"
            and self.far["52.204-26.c.2"]["answer"] == "DOES"
        ):
            return "PROVIDES AND USES COVERED TELECOMMUNICATIONS"
        if self.far["52.204-26.c.1"]["answer"] == "DOES":
            return "PROVIDES COVERED TELECOMMUNICATIONS"
        if self.far["52.204-26.c.2"]["answer"] == "DOES":
            return "USES COVERED TELECOMMUNICATIONS"
        return "UNSPECIFIED"

    @property
    def elaborated_status_text(self):
        """Clarifies noncompliant status text

        Returns:
            str: if noncompliant adds NONCOMPLIANT to return string
        """
        if self.is_compliant:
            return self.status_text
        return f"NONCOMPLIANT - {self.status_text}"

    @property
    def far_provision_date(self):
        """The first update to the FAR in DEC 2019 contained only part C1 for 52.204-26.
        Later in OCT 2020 part C2 was added to 52.204-26

        Returns:
            _type_: _description_
        """
        if self._has_far_part_c1 and not self._has_far_part_c2:
            return "DEC 2019"
        if self._has_far_part_c1 and self._has_far_part_c2:
            return "OCT 2020"
        return None

    @property
    def _has_far_response(self):
        if self._has_far_part_c1 or self._has_far_part_c2:
            return True
        return False

    @property
    def _has_far_part_c1(self):
        return self._far_has("52.204-26.c.1")

    @property
    def _has_far_part_c2(self):
        return self._far_has("52.204-26.c.2")

    def _far_has(self, provision_id):
        if self._far[provision_id]["answer"] is not None:
            return True
        return False


class Exclusions:
    """An object that contains the entity exclusion status information"""

    def __init__(self, sam_exclusion_status_flag=""):
        self._sam_exclusion_status_flag = sam_exclusion_status_flag

    @property
    def has_exclusions(self):
        """
        Returns:
            bool:
        """
        if self._sam_exclusion_status_flag == "N":
            return False
        return True

    @property
    def status_text(self):
        """

        Returns:
            str: Returns No, Yes, or Unspecified
        """
        if not self.has_exclusions:
            return "No"
        if self._sam_exclusion_status_flag == "Y":
            return "Yes"
        return "Unspecified"


class RegistrationStatus:
    """An object that contains the registration status information"""

    def __init__(self, registration_status="Unspecified"):
        self.registration_status = registration_status

    @property
    def is_active(self):
        """

        Returns:
            bool:
        """
        if self.registration_status == "Active":
            return True
        return False

    @property
    def status_text(self):
        """

        Returns:
            str: Returns the registration status provided by the SAM Entities API
        """
        return self.registration_status
