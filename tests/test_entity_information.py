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

import pytest
from werkzeug.datastructures import ImmutableMultiDict

from samtools.sam_api.entity_information import DataAdaptors
from samtools.compliance import compliance_rules


class TestDataAdaptors:
    class TestAdaptSamToolToSam:
        @staticmethod
        def test_no_parameters():
            parameters = ImmutableMultiDict([])
            data_adaptors = DataAdaptors()
            assert data_adaptors.adapt_samtools_to_sam_parameters(parameters) == {
                "includeSections": set(
                    ["entityRegistration", "coreData", "repsAndCerts"]
                )
            }

        @staticmethod
        def test_includes_samtools_data():
            parameters = ImmutableMultiDict(
                [
                    ("includeSections", "samToolsData,entityRegistration,coreData"),
                ]
            )
            data_adaptors = DataAdaptors()
            assert data_adaptors.adapt_samtools_to_sam_parameters(parameters) == {
                "includeSections": set(
                    ["entityRegistration", "coreData", "repsAndCerts"]
                )
            }

        @staticmethod
        def test_includes_samtools_search():
            parameters = ImmutableMultiDict(
                [
                    ("samToolsSearch", "mcmaster carr"),
                ]
            )
            data_adaptors = DataAdaptors()
            assert (
                "samToolsSearch"
                not in data_adaptors.adapt_samtools_to_sam_parameters(parameters)
            )

        @staticmethod
        def test_typical_call():
            parameters = ImmutableMultiDict(
                [
                    ("samToolsSearch", "mcmaster"),
                    ("includeSections", "samToolsData,entityRegistration,coreData"),
                    ("registrationStatus", "A"),
                    ("purposeOfRegistrationCode", "Z2~Z5"),
                    ("entityEFTIndicator", ""),
                ]
            )
            data_adaptors = DataAdaptors()
            assert data_adaptors.adapt_samtools_to_sam_parameters(parameters) == {
                "includeSections": set(
                    ["entityRegistration", "coreData", "repsAndCerts"]
                ),
                "registrationStatus": "A",
                "purposeOfRegistrationCode": "Z2~Z5",
                "entityEFTIndicator": "",
                "q": "(legalBusinessName:mcmaster* OR dbaName:mcmaster*)",
            }

    class TestAdaptSamResponcesTo889Compliance:
        @staticmethod
        @pytest.mark.parametrize(
            "entity",
            [{}, {"repsAndCerts": {}}, {"repsAndCerts": {"certifications": {}}}],
        )
        def test_no_reps_and_certs(entity):
            data_adaptors = DataAdaptors()
            assert (
                data_adaptors.adapt_sam_response_to_889_compliance(
                    entity
                )._has_far_response
                is False
            )

        @staticmethod
        def test_is_compliant():
            far_responses = [
                {
                    "provisionId": "FAR 52.204-26",
                    "listOfAnswers": [
                        {
                            "section": "52.204-26.c.1",
                            "answerText": "No",
                        },
                        {
                            "section": "52.204-26.c.2",
                            "answerText": "No",
                        },
                    ],
                }
            ]
            entity = {
                "repsAndCerts": {"certifications": {"fARResponses": far_responses}}
            }
            data_adaptors = DataAdaptors()
            assert (
                data_adaptors.adapt_sam_response_to_889_compliance(entity).is_compliant
                is True
            )

        @staticmethod
        @pytest.mark.parametrize(
            "answers", [("Yes", "Yes"), ("Yes", "No"), ("No", "Yes")]
        )
        def test_not_compliant(answers):
            far_responses = [
                {
                    "provisionId": "FAR 52.204-26",
                    "listOfAnswers": [
                        {
                            "section": "52.204-26.c.1",
                            "answerText": answers[0],
                        },
                        {
                            "section": "52.204-26.c.2",
                            "answerText": answers[1],
                        },
                    ],
                }
            ]
            entity = {
                "repsAndCerts": {"certifications": {"fARResponses": far_responses}}
            }
            data_adaptors = DataAdaptors()
            assert (
                data_adaptors.adapt_sam_response_to_889_compliance(entity).is_compliant
                is False
            )

    class TestAdaptSamResponcesToExclusions:
        @staticmethod
        @pytest.mark.parametrize("exclusion_status_flag", ["N"])
        def test_does_not_have_exclusions(exclusion_status_flag):
            data_adaptors = DataAdaptors()
            entity = {
                "entityRegistration": {"exclusionStatusFlag": exclusion_status_flag}
            }
            assert (
                data_adaptors.adapt_sam_response_to_exclusions(entity).has_exclusions
                is False
            )

        @staticmethod
        @pytest.mark.parametrize("exclusion_status_flag", ["Y", 1])
        def test_has_exclusions(exclusion_status_flag):
            data_adaptors = DataAdaptors()
            entity = {
                "entityRegistration": {"exclusionStatusFlag": exclusion_status_flag}
            }
            assert (
                data_adaptors.adapt_sam_response_to_exclusions(entity).has_exclusions
                is True
            )

    class TestAdaptSamResponcesToRegistrationStatus:
        @staticmethod
        def test_registration_is_active():
            data_adaptors = DataAdaptors()
            entity = {"entityRegistration": {"registrationStatus": "Active"}}
            assert (
                data_adaptors.adapt_sam_response_to_registration_status(
                    entity
                ).is_active
                is True
            )

        @staticmethod
        @pytest.mark.parametrize("registration_status", ["Inactive", 1])
        def test_registration_is_not_active(registration_status):
            data_adaptors = DataAdaptors()
            entity = {"entityRegistration": {"registrationStatus": registration_status}}
            assert (
                data_adaptors.adapt_sam_response_to_registration_status(
                    entity
                ).is_active
                is False
            )
