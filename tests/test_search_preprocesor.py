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

from samtools.sam_api.search_preprocessor import get_search_parameter


class TestSearchPreprocessor:
    @staticmethod
    def test_input_empty():
        assert get_search_parameter() == {}

    @staticmethod
    @pytest.mark.parametrize("whitespace", ["", " ", "\t", "\n", "  \t\t\n\n"])
    def test_input_only_whitespace(whitespace):
        assert get_search_parameter(whitespace) == {}

    @staticmethod
    @pytest.mark.parametrize("cage_code", ["12345", "2BcD4"])
    def test_input_cage_code(cage_code):
        assert get_search_parameter(cage_code) == {"cageCode": cage_code}

    @staticmethod
    @pytest.mark.parametrize("ncage_code", ["fBhL7", "SKCM3"])
    def test_input_ncage_code(ncage_code):
        assert get_search_parameter(ncage_code) == {
            "q": f"(legalBusinessName:{ncage_code}* OR "
            f"dbaName:{ncage_code}* OR cageCode:{ncage_code})"
        }

    @staticmethod
    @pytest.mark.parametrize(
        "resembles_ncage_code",
        [
            "advex",
            "adyen",
            "aesub",
            "alhdd",
            "ampad",
            "ansys",
            "arcus",
            "atlas",
            "ayden",
        ],
    )
    def test_input_five_char_resembles_ncage_code(resembles_ncage_code):
        assert get_search_parameter(resembles_ncage_code) == {
            "q": f"(legalBusinessName:{resembles_ncage_code}* OR "
            f"dbaName:{resembles_ncage_code}* OR cageCode:{resembles_ncage_code})"
        }

    @staticmethod
    @pytest.mark.parametrize(
        "not_ncage_code",
        [
            "adept",
            "alpha",
            "anker",
            "apple",
            "arata",
            "astra",
            "avent",
            "avery",
            "aveva",
            "avnet",
            "aztek",
            "baker",
            "bandh",
            "beamq",
            "beats",
            "bestb",
            "black",
            "brady",
            "braun",
            "bruel",
            "cable",
            "cerex",
            "chase",
            "clark",
            "crane",
            "crest",
            "cvent",
            "cytec",
            "dance",
            "dataq",
            "delta",
            "dewey",
            "dmark",
            "durex",
            "dwyer",
            "dynex",
            "eagle",
            "ebags",
            "eckel",
            "eflux",
            "eksma",
            "elmet",
            "emrax",
            "endaq",
            "enmet",
            "erlab",
            "ersad",
            "ettus",
            "excel",
            "extec",
            "fabas",
            "fastc",
            "fedex",
            "fetch",
            "fluke",
            "fully",
            "futek",
            "genex",
            "ghent",
            "glass",
            "grahl",
            "huber",
            "human",
            "hunts",
            "jabra",
            "jakar",
            "jewel",
            "kmart",
            "kpaul",
            "laser",
            "lemke",
            "lprcs",
            "madge",
            "magna",
            "maple",
            "meyer",
            "nemal",
            "neweg",
            "nlyte",
            "padua",
            "parts",
            "pater",
            "pchub",
            "pcmag",
            "prusa",
            "quest",
            "ratta",
            "rcats",
            "rexel",
            "sager",
            "sampe",
            "seals",
            "sears",
            "seeed",
            "sepac",
            "sharp",
            "shell",
            "spark",
            "stamp",
            "steam",
            "sweet",
            "taber",
            "talas",
            "tattu",
            "tdarr",
            "tesla",
            "tnutz",
            "trace",
            "trane",
            "uhaul",
            "ussfp",
            "utmel",
            "valve",
            "veeam",
            "versa",
            "watec",
            "watts",
            "wawak",
            "zaber",
            "zazzl",
            "zemax",
            "zubax",
            "zuken",
        ],
    )
    def test_input_five_char_non_ncage_code(not_ncage_code):
        assert get_search_parameter(not_ncage_code) == {
            "q": f"(legalBusinessName:{not_ncage_code}* OR dbaName:{not_ncage_code}*)"
        }

    @staticmethod
    @pytest.mark.parametrize("whitespace", ["", " ", "\t", "\n", "  \t\t\n\n"])
    def test_input_cage_code_with_whitespace(whitespace):
        _id = "12345"
        assert get_search_parameter(f"{whitespace}{_id}{whitespace}") == {
            "cageCode": _id
        }

    @staticmethod
    @pytest.mark.parametrize(
        "uei_sam", ["123456789012", "ABCDEFGHJKL4", "12AB56789012"]
    )
    def test_input_uei_sam(uei_sam):
        assert get_search_parameter(uei_sam) == {"ueiSAM": uei_sam}

    @staticmethod
    def test_input_single_word_vendor_name():
        assert get_search_parameter("  name \t") == {
            "q": "(legalBusinessName:name* OR dbaName:name*)"
        }

    @staticmethod
    def test_input_multiple_word_vendor_name():
        assert get_search_parameter("  name \tof    company") == {
            "q": "(legalBusinessName:name* of company* OR dbaName:name* of company*)"
        }

    @staticmethod
    def test_input_vendor_name_with_apostrophe1():
        assert get_search_parameter("lowe's") == {
            "q": "(legalBusinessName:lowe's* OR dbaName:lowe's*)"
        }

    @staticmethod
    def test_input_vendor_name_with_apostrophe2():
        assert get_search_parameter("ben's and godfrey's company") == {
            "q": "(legalBusinessName:ben's* and* godfrey's* company* OR dbaName:ben's* and* godfrey's* company*)"
        }

    @staticmethod
    def test_input_vendor_name_in_double_quotes():
        assert get_search_parameter(f'"name of  company"   sci') == {
            "q": '(legalBusinessName:"name of  company" sci* OR dbaName:"name of  company" sci*)'
        }

    @staticmethod
    def test_input_vendor_name_in_uneven_quotes():
        assert get_search_parameter('"name of  company"   "sci') == {
            "q": '(legalBusinessName:"name* of company"* "sci* OR dbaName:"name* of company"* "sci*)'
        }

    @staticmethod
    @pytest.mark.parametrize(
        "forbidden_character", ["-", "&", "|", "{", "}", "^", "\\"]
    )
    def test_input_vendor_name_with_forbidden_character(forbidden_character):
        name = f"company{forbidden_character}name"
        assert get_search_parameter(name) == {
            "q": "(legalBusinessName:company* name* OR dbaName:company* name*)"
        }

    @staticmethod
    @pytest.mark.parametrize("llc", ["llc", "LLC", "L.L.C.", "l.l.c."])
    def test_input_vendor_name_with_llc(llc):
        name = f"company name {llc}"
        assert get_search_parameter(name) == {
            "q": "(legalBusinessName:company* name* OR dbaName:company* name*)"
        }

    @staticmethod
    @pytest.mark.parametrize(
        "website", ["name.com", "www.name.com", "name.org", "name.gov", "name.us"]
    )
    def test_input_website(website):
        assert get_search_parameter(website) == {"q": f"(*{website}*)"}

    @staticmethod
    def test_input_website_with_endpoint():
        assert get_search_parameter("name.com/name") == {"q": "(*name.com*)"}

    @staticmethod
    @pytest.mark.parametrize("http", ["http://", "https://"])
    def test_input_website_with_http(http):
        assert get_search_parameter(f"{http}www.name.com") == {"q": "(*www.name.com*)"}

    @staticmethod
    def test_input_with_commas():
        assert get_search_parameter("test, company , inc in,c") == {
            "q": "(legalBusinessName:test* company* inc* inc* OR dbaName:test* company* inc* inc*)"
        }

    @staticmethod
    def test_input_with_periods_at_end_of_words():
        assert get_search_parameter("test company. inc.") == {
            "q": "(legalBusinessName:test* company* inc* OR dbaName:test* company* inc*)"
        }
