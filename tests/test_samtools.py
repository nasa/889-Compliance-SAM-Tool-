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
import json
import requests

from samtools import create_app


@pytest.fixture
def client():
    app = create_app()
    yield app.test_client()


@pytest.fixture
def my_app():
    app = create_app()
    yield app


def test_external_links(my_app):
    for external_link in my_app.config["EXTERNAL_LINKS"].values():
        response = requests.get(external_link, timeout=10)
        assert response.ok


def _entities_api_url(search_term):
    return (
        "/api/entity-information/v3/entities?"
        f"samToolsSearch={search_term}"
        "&includeSections=samToolsData,entityRegistration,coreData"
        "&registrationStatus=A"
        "&purposeOfRegistrationCode=Z2~Z5"
        "&entityEFTIndicator="
    )


class TestEntitiesSearch:
    @staticmethod
    @pytest.mark.parametrize(
        "get_call",
        [
            (
                "/api/entity-information/v3/entities?"
                "samToolsSearch={}"
                "&includeSections=samToolsData,entityRegistration,coreData"
                "&registrationStatus=A"
                "&purposeOfRegistrationCode=Z2~Z5"
                "&entityEFTIndicator="
            ),
            (
                "/api/entity-information/v3/entities?"
                "samToolsSearch={}"
                "&includeSections=samToolsData"
                "&includeSections=entityRegistration"
                "&includeSections=coreData"
                "&registrationStatus=A"
                "&purposeOfRegistrationCode=Z2~Z5"
                "&entityEFTIndicator="
            ),
            (
                "/api/entity-information/v3/entities?"
                "samToolsSearch={}"
                "&includeSections=[samToolsData,entityRegistration,coreData]"
                "&registrationStatus=A"
                "&purposeOfRegistrationCode=Z2~Z5"
                "&entityEFTIndicator="
            ),
        ],
    )
    def test_different_api_get_call_styles(client, get_call):
        response = client.get(get_call.format("grainger"))
        data = json.loads(response.data)
        assert "DBQGN324ULK3" in [
            entity["entityRegistration"]["ueiSAM"] for entity in data["entityData"]
        ]

    @staticmethod
    @pytest.mark.parametrize(
        "search_term,sam_uei",
        [
            ("mcmaster carr", "QJ8GDNZ7RMC5"),
            ("grainger", "DBQGN324ULK3"),
            ("office depot", "DL92XLEBJHE1"),
            ("b h photo", "DXUNWV7UH817"),
            ("cdw", "PHZDZ8SJ5CM1"),
            ("newegg", "VYGGEBDMC155"),
            ("8020", "VD8SDL4UWTN1"),
            (
                "priority worldwide",
                "P5FDDF13ZZ68",
            ),  # It is not clear why the SAM Entities API does not return any results for this entity unless this name is placed in quotes
            ("msc direct", "NTP7NWDS9Y49"),
        ],
    )
    def test_find_common_business_name_searches(client, search_term, sam_uei):
        response = client.get(_entities_api_url(search_term))
        data = json.loads(response.data)
        assert sam_uei in [
            entity["entityRegistration"]["ueiSAM"] for entity in data["entityData"]
        ]

    @staticmethod
    @pytest.mark.parametrize(
        "search_term,sam_uei",
        [
            ("fisher scientific company l.l.c.", "F5TEGZ32EJ38"),
            ("omega engineering inc.", "U2LWMEYC3MP1"),
            ("w. w. grainger, inc.", "DBQGN324ULK3"),
            ("office timeline, llc", "CD65M3FP1MX7"),
        ],
    )
    def test_find_businesses_with_common_words(client, search_term, sam_uei):
        response = client.get(_entities_api_url(search_term))
        data = json.loads(response.data)
        assert sam_uei in [
            entity["entityRegistration"]["ueiSAM"] for entity in data["entityData"]
        ]

    @staticmethod
    @pytest.mark.parametrize(
        "search_term,sam_uei",
        [
            ("lowe's", "QXMMLB757QB8"),
            ("white's boots", "GL3GMLPBUDB4"),
            ("hop's place", "HPLLX3YYEZ63"),
            ('"priority worldwide"', "P5FDDF13ZZ68"),
            ('"electrical equipment company"', "SLU2DN6TSP47"),
            ('"national instruments"', "LKXHMX1K3AC5"),
        ],
    )
    def test_find_business_names_with_quotations(client, search_term, sam_uei):
        response = client.get(_entities_api_url(search_term))
        data = json.loads(response.data)
        assert sam_uei in [
            entity["entityRegistration"]["ueiSAM"] for entity in data["entityData"]
        ]

    @staticmethod
    @pytest.mark.parametrize(
        "search_term,sam_uei",
        [
            ("mcmaster-carr", "QJ8GDNZ7RMC5"),
            ("digi-key", "FAHMKDSUM9H9"),
            ("n+1 technologies", "PKFMLN9M7KE4"),
        ],
    )
    def test_find_business_names_with_nonalphanumeric_characters(
        client, search_term, sam_uei
    ):
        response = client.get(_entities_api_url(search_term))
        data = json.loads(response.data)
        assert sam_uei in [
            entity["entityRegistration"]["ueiSAM"] for entity in data["entityData"]
        ]

    @staticmethod
    @pytest.mark.parametrize(
        "search_term,sam_uei",
        [
            ("advex", "JM2GNDJLDWL5"),
            ("arcus", "E5RSJGBH7CU8"),
            ("ansys", "TY4MJLKVJJ27"),
        ],
    )
    def test_find_business_names_that_resemble_cage_codes(client, search_term, sam_uei):
        response = client.get(_entities_api_url(search_term))
        data = json.loads(response.data)
        assert sam_uei in [
            entity["entityRegistration"]["ueiSAM"] for entity in data["entityData"]
        ]

    @staticmethod
    @pytest.mark.parametrize(
        "search_term,sam_uei",
        [
            ("https://www.amazon.com", "TMKBFBRHFKH3"),
            ("apple.com/", "HJAKCN4NEU95"),
            ("skygeek.com", "QNKHHDVTRKK4"),
            ("http://www.cdwg.com/product/example", "PHZDZ8SJ5CM1"),
        ],
    )
    def test_find_website_searches(client, search_term, sam_uei):
        response = client.get(_entities_api_url(search_term))
        data = json.loads(response.data)
        assert sam_uei in [
            entity["entityRegistration"]["ueiSAM"] for entity in data["entityData"]
        ]

    @staticmethod
    @pytest.mark.parametrize(
        "search_term,sam_uei",
        [
            ("0s392", "HMZ5L9ZNW988"),
            ("54968", "WFYWL6SQ6FB8"),
            ("1yes6", "KU9CQ383DAQ9"),
        ],
    )
    def test_find_us_cage_code_searches(client, search_term, sam_uei):
        response = client.get(_entities_api_url(search_term))
        data = json.loads(response.data)
        assert sam_uei in [
            entity["entityRegistration"]["ueiSAM"] for entity in data["entityData"]
        ]

    @staticmethod
    @pytest.mark.parametrize(
        "search_term,sam_uei",
        [
            ("fbhl7", "GXQGMZP28CW3"),
        ],
    )
    def test_find_nato_cage_code_searches(client, search_term, sam_uei):
        response = client.get(_entities_api_url(search_term))
        data = json.loads(response.data)
        assert sam_uei in [
            entity["entityRegistration"]["ueiSAM"] for entity in data["entityData"]
        ]

    @staticmethod
    @pytest.mark.parametrize(
        "search_term,sam_uei",
        [
            ("ygzmmvqkvfh1", "YGZMMVQKVFH1"),
            ("e2jqucnkle93", "E2JQUCNKLE93"),
            ("k3b5je3zs915", "K3B5JE3ZS915"),
            ("K3B5jE3zS915", "K3B5JE3ZS915"),
        ],
    )
    def test_find_sam_uei_searches(client, search_term, sam_uei):
        response = client.get(_entities_api_url(search_term))
        data = json.loads(response.data)
        assert sam_uei in [
            entity["entityRegistration"]["ueiSAM"] for entity in data["entityData"]
        ]

    @staticmethod
    @pytest.mark.parametrize("sam_uei", [("UFVMHT6U79Y8"), ("L5DKR5BE6LS7")])
    def test_known_noncompliant_entities(client, sam_uei):
        response = client.get(_entities_api_url(sam_uei))
        data = json.loads(response.data)
        assert (
            data["entityData"][0]["samToolsData"]["eightEightNine"]["isCompliant"]
            is False
        )

    @staticmethod
    @pytest.mark.parametrize("sam_uei", [("C1FCEKJP7F91"), ("NTP7NWDS9Y49")])
    def test_known_compliant_entities(client, sam_uei):
        response = client.get(_entities_api_url(sam_uei))
        data = json.loads(response.data)
        assert (
            data["entityData"][0]["samToolsData"]["eightEightNine"]["isCompliant"]
            is True
        )

    @staticmethod
    @pytest.mark.parametrize("sam_uei", [("C1FCEKJP7F91"), ("NTP7NWDS9Y49")])
    def test_known_entities_without_exclusions(client, sam_uei):
        response = client.get(_entities_api_url(sam_uei))
        data = json.loads(response.data)
        assert (
            data["entityData"][0]["samToolsData"]["exclusions"]["hasExclusions"]
            is False
        )
