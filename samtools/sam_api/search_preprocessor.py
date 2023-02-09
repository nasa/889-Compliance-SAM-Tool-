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
search_preprocessor.py

Module for generating SAM Entities API query parameters from a user input string.

"""

import re
import shlex
import warnings
from urllib.parse import urlparse


def get_search_parameter(search_input=""):
    """Generate SAM API query parameters from a user input string.

    There are business names that are also valid NCAGE codes. Therefore we search both fields
    in this case.

    Currently there is no way to directly search the entityURL field, however a general 'q'
    search will search all fields including entityURL. We prefer not to do general 'q' searches
    because there are usually too many irrelevant results (apple returns results from appleton
    WI, entities on apple road etc.). For websites, the word.domain structure required prevents
    these false positives in our testing.

    Args:
        search_input (str, optional): User input search expression. Defaults to "".

    Returns:
        dict: Contains keys of either "cageCode", "ueiSAM", or "q"
    """
    if search_input is None:
        return {}

    search_input = " ".join(_split_and_preserve_quotes(search_input))

    if len(search_input) == 0:
        return {}

    if _is_sam_unique_entity_id(search_input):
        return {"ueiSAM": search_input}

    if _is_us_cage_code(search_input):
        return {"cageCode": search_input}

    if _is_potential_ncage_code(search_input):
        business_name = _get_cleaned_and_prepared_business_name(search_input)
        return {
            "q": f"(legalBusinessName:{business_name} OR "
            f"dbaName:{business_name} OR cageCode:{search_input})"
        }

    if _is_potential_website(search_input):
        website = _get_cleaned_and_prepared_website(search_input)
        return {"q": f"(*{website}*)"}

    business_name = _get_cleaned_and_prepared_business_name(search_input)
    return {"q": f"(legalBusinessName:{business_name} OR dbaName:{business_name})"}


def _is_sam_unique_entity_id(search_input):
    """
    SAM Unique Entity Identifier: Twelve-position alphanumeric, does not have leading
    zeros, ends with numeric checksum, excludes the letters I and O.
    """
    sam_uei_regex = r"(?i)^[A-HJ-NP-Z1-9][A-HJ-NP-Z0-9]{10}[0-9]$"
    if re.match(sam_uei_regex, search_input):
        return True
    return False


def _is_us_cage_code(search_input):
    """
    cage code: Five-position alphanumeric, numeric in the first and last positions,
        excludes the letters I and O.
    """
    united_states_cage_code_regex = r"(?i)^[0-9][A-HJ-NP-Z0-9]{3}[0-9]$"
    if re.match(united_states_cage_code_regex, search_input):
        return True
    return False


def _is_potential_ncage_code(search_input):
    """
    NATO cage code: Five-position alphanumeric, excludes the letters I and O,
    with the exception of I***# codes for the NATO & international code.
    (# = numeral, * = alpha/numerical)
    First and last characters indicate the country.
    Note: Tier 1 NATO countries use S***# codes in SAM.
    References:
    - https://www.nato.int/structur/AC/135/main/pdf/NCS_codes_chart.pdf
    - https://www.nato.int/structur/AC/135/main/links/codsp3.htm
    """
    nato_cage_code_regex = (
        r"(?i)"
        r"(^[I][A-HJ-NP-Z0-9]{3}[0-9]$)|"  # NATO & International Org.
        r"(^[S][A-HJ-NP-Z0-9]{3}[0-9]$)|"  # Non-NATO Nations
        r"(^[A][A-HJ-NP-Z0-9]{3}[H]$)|"  # NATO - Albania
        r"(^[B][A-HJ-NP-Z0-9]{3}[0-9]$)|"  # NATO - Belgium
        r"(^[0-9][A-HJ-NP-Z0-9]{3}[U]$)|"  # NATO - Bulgaria
        r"(^[0-9L][A-HJ-NP-Z0-9]{3}[0-9]$)|"  # NATO - Canada
        r"(^[A][A-HJ-NP-Z0-9]{3}[B]$)|"  # NATO - Croatia
        r"(^[0-9][A-HJ-NP-Z0-9]{3}[G]$)|"  # NATO - Czech Republicv
        r"(^[R][A-HJ-NP-Z0-9]{3}[0-9]$)|"  # NATO - Denmark
        r"(^[0-9][A-HJ-NP-Z0-9]{3}[J]$)|"  # NATO - Estonia
        r"(^[FM][A-HJ-NP-Z0-9]{3}[0-9]$)|"  # NATO - France
        r"(^[CD][A-HJ-NP-Z0-9]{3}[0-9]$)|"  # NATO - Germany
        r"(^[G][A-HJ-NP-Z0-9]{3}[0-9]$)|"  # NATO - Greece
        r"(^[0-9][A-HJ-NP-Z0-9]{3}[V]$)|"  # NATO - Hungary
        r"(^[S][A-HJ-NP-Z0-9]{3}[0-9]$)|"  # NATO - Iceland
        r"(^[A][A-HJ-NP-Z0-9]{3}[0-9]$)|"  # NATO - Italy
        r"(^[A][A-HJ-NP-Z0-9]{3}[D]$)|"  # NATO - Latvia
        r"(^[0-9][A-HJ-NP-Z0-9]{3}[R]$)|"  # NATO - Lithuania
        r"(^[B][A-HJ-NP-Z0-9]{3}[0-9]$)|"  # NATO - Luxembourg
        r"(^[A][A-HJ-NP-Z0-9]{3}[W]$)|"  # NATO - Montenegro  <--
        r"(^[H][A-HJ-NP-Z0-9]{3}[0-9]$)|"  # NATO - Netherlands
        r"(^[A][A-HJ-NP-Z0-9]{3}[C]$)|"  # NATO - North Macedonia  <--
        r"(^[N][A-HJ-NP-Z0-9]{3}[0-9]$)|"  # NATO - Norway
        r"(^[0-9][A-HJ-NP-Z0-9]{3}[H]$)|"  # NATO - Poland
        r"(^[P][A-HJ-NP-Z0-9]{3}[0-9]$)|"  # NATO - Portugal
        r"(^[0-9][A-HJ-NP-Z0-9]{3}[L]$)|"  # NATO - Romania
        r"(^[0-9][A-HJ-NP-Z0-9]{3}[M]$)|"  # NATO - Slovakia
        r"(^[0-9][A-HJ-NP-Z0-9]{3}[Q]$)|"  # NATO - Slovenia
        r"(^[0-9][A-HJ-NP-Z0-9]{3}[B]$)|"  # NATO - Spain
        r"(^[T][A-HJ-NP-Z0-9]{3}[0-9]$)|"  # NATO - Turkey
        r"(^[UK][A-HJ-NP-Z0-9]{3}[0-9]$)|"  # NATO - United Kingdom
        r"(^[0-9][A-HJ-NP-Z0-9]{3}[0-9]$)|"  # NATO - United States
        r"(^[W][A-HJ-NP-Z0-9]{3}[0-9]$)|"  # Tier 2 - Argentina
        r"(^[Z][A-HJ-NP-Z0-9]{3}[0-9]$)|"  # Tier 2 - Australia
        r"(^[0-9][A-HJ-NP-Z0-9]{3}[N]$)|"  # Tier 2 - Austria
        r"(^[0-9][A-HJ-NP-Z0-9]{3}[K]$)|"  # Tier 2 - Brazil
        r"(^[A][A-HJ-NP-Z0-9]{3}[Z]$)|"  # Tier 2 - Colombia
        r"(^[A][A-HJ-NP-Z0-9]{3}[G]$)|"  # Tier 2 - Finland
        r"(^[0-9][A-HJ-NP-Z0-9]{3}[Y]$)|"  # Tier 2 - India
        r"(^[0-9][A-HJ-NP-Z0-9]{3}[Z]$)|"  # Tier 2 - Indonesia
        r"(^[0-9][A-HJ-NP-Z0-9]{3}[A]$)|"  # Tier 2 - Israel
        r"(^[J][A-HJ-NP-Z0-9]{3}[0-9]$)|"  # Tier 2 - Japan
        r"(^[A][A-HJ-NP-Z0-9]{3}[X]$)|"  # Tier 2 - Jordan
        r"(^[0-9][A-HJ-NP-Z0-9]{3}[F]$)|"  # Tier 2 - Korea, Republic of
        r"(^[Y][A-HJ-NP-Z0-9]{3}[0-9]$)|"  # Tier 2 - Malaysia
        r"(^[A][A-HJ-NP-Z0-9]{3}[M]$)|"  # Tier 2 - Morocco
        r"(^[E][A-HJ-NP-Z0-9]{3}[0-9]$)|"  # Tier 2 - New Zealand
        r"(^[A][A-HJ-NP-Z0-9]{3}[S]$)|"  # Tier 2 - Serbia
        r"(^[Q][A-HJ-NP-Z0-9]{3}[0-9]$)|"  # Tier 2 - Singapore
        r"(^[A][A-HJ-NP-Z0-9]{3}[N]$)|"  # Tier 2 - Sweden
        r"(^[A][A-HJ-NP-Z0-9]{3}[J]$)|"  # Tier 2 - Ukraine
        r"(^[0-9][A-HJ-NP-Z0-9]{3}[W]$)"  # Tier 2 - United Arab Emirates
    )
    if re.match(nato_cage_code_regex, search_input):
        return True
    return False


def _get_cleaned_and_prepared_business_name(search_input):
    search_input = _replace_forbidden_characters_with_whitespace(search_input)
    search_input = _remove_commas(search_input)
    search_input = _remove_llc(search_input)
    search_input = _remove_trailing_periods(search_input)
    search_input = _add_wildcards(search_input)
    return search_input


def _is_potential_website(search_input):
    top_level_domains = set(["com", "org", "net", "int", "edu", "gov", "mil", "us"])

    if "." not in search_input:
        return False

    if search_input.startswith("http://") or search_input.startswith("https://"):
        return True

    potential_netloc = _get_website_netloc(search_input)
    if potential_netloc is None:
        return False

    split_potential_netloc = potential_netloc.split(".")
    if len(split_potential_netloc) <= 1:
        return False

    top_level_domain = split_potential_netloc[-1]
    if top_level_domain not in top_level_domains:
        return False

    return True


def _get_cleaned_and_prepared_website(search_input):
    search_input = search_input.replace("http://", "")
    search_input = search_input.replace("https://", "")

    potential_netloc = _get_website_netloc(search_input)
    if potential_netloc is None:
        return search_input

    potential_netloc = _replace_forbidden_characters_with_whitespace(potential_netloc)
    return potential_netloc


def _get_website_netloc(search_input):
    try:
        return urlparse(f"http://{search_input}").netloc
    except ValueError as value_error:
        warnings.warn(f"{search_input}: {value_error}")
    return None


def _add_wildcards(search_inputs):
    sentence = []
    for word in _split_and_preserve_quotes(search_inputs):
        if word[0] == '"' and word[-1] == '"':
            sentence.append(word)
        elif len(word) <= 2:
            sentence.append(word)
        else:
            sentence.append(f"{word}*")
    return " ".join(sentence)


def _split_and_preserve_quotes(search_input):
    try:
        lex = shlex.shlex(search_input, posix=False)
        lex.quotes = '"'
        lex.whitespace_split = True
        lex.commenters = ""
        return list(lex)
    except ValueError:
        return search_input.split()


def _replace_forbidden_characters_with_whitespace(search_input):
    forbidden_characters = r"-&|{}^\\"
    return search_input.translate(
        str.maketrans(forbidden_characters, " " * len(forbidden_characters))
    )


def _remove_commas(search_input):
    return search_input.replace(",", "")


def _remove_trailing_periods(search_input):
    """User searches like 'apple inc.' can perform better without the period in 'inc'"""
    sentence = []
    for word in _split_and_preserve_quotes(search_input):
        sentence.append(word.rstrip("."))
    return " ".join(sentence)


def _remove_llc(search_input):
    "User searches like 'Thermo Fisher L.L.C.' perform better without 'L.L.C."
    sentence = []
    for word in _split_and_preserve_quotes(search_input):
        if word.upper() not in ("L.L.C", "L.L.C.", "LLC"):
            sentence.append(word)
    return " ".join(sentence)
