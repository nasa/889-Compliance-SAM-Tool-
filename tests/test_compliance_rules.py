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

from samtools.compliance import compliance_rules


@pytest.fixture
def empty_entity():
    return compliance_rules.EightEightNine()


@pytest.fixture
def compliant_entity():
    compliance = compliance_rules.EightEightNine()
    compliance.set_far("52.204-26.c.1", "No")
    compliance.set_far("52.204-26.c.2", "No")
    return compliance


@pytest.fixture
def entity_provides_covered_tele():
    compliance = compliance_rules.EightEightNine()
    compliance.set_far("52.204-26.c.1", "Yes")
    compliance.set_far("52.204-26.c.2", "No")
    return compliance


@pytest.fixture
def entity_uses_covered_tele():
    compliance = compliance_rules.EightEightNine()
    compliance.set_far("52.204-26.c.1", "No")
    compliance.set_far("52.204-26.c.2", "Yes")
    return compliance


@pytest.fixture
def entity_provides_and_uses_covered_tele():
    compliance = compliance_rules.EightEightNine()
    compliance.set_far("52.204-26.c.1", "Yes")
    compliance.set_far("52.204-26.c.2", "Yes")
    return compliance


@pytest.fixture
def entity_provides_and_no_c2():
    compliance = compliance_rules.EightEightNine()
    compliance.set_far("52.204-26.c.1", "Yes")
    return compliance


@pytest.fixture
def entity_does_not_provide_and_no_c2():
    compliance = compliance_rules.EightEightNine()
    compliance.set_far("52.204-26.c.1", "No")
    return compliance


class TestEightEightNineNotSet:
    def test_is_compliant(self, empty_entity):
        assert empty_entity.is_compliant is False

    def test_status_text(self, empty_entity):
        assert empty_entity.status_text == "NO REPS & CERTS"

    def test_far_provision_date(self, empty_entity):
        assert empty_entity.far_provision_date is None

    def test_far_text_c1(self, empty_entity):
        assert empty_entity.far["52.204-26.c.1"]["text"] is None


class TestEightEightNineCompliant:
    def test_is_compliant(self, compliant_entity):
        assert compliant_entity.is_compliant is True

    def test_status_text(self, compliant_entity):
        assert compliant_entity.status_text == "COMPLIANT"

    def test_far_provision_date(self, compliant_entity):
        assert compliant_entity.far_provision_date == "OCT 2020"

    def test_far_text_c1(self, compliant_entity):
        assert (
            compliant_entity.far["52.204-26.c.1"]["text"]
            == "(1) The Offeror represents that it DOES NOT provide covered "
            + "telecommunications equipment or services as a part of its offered "
            + "products or services to the Government in the performance of any "
            + "contract, subcontract, or other contractual instrument."
        )

    def test_far_text_c2(self, compliant_entity):
        assert (
            compliant_entity.far["52.204-26.c.2"]["text"]
            == "(2) After conducting a reasonable inquiry for purposes of this "
            + "representation, the offeror represents that it DOES NOT use covered "
            + "telecommunications equipment or services, or any equipment, system, "
            + "or service that uses covered telecommunications equipment or "
            + "services."
        )


class TestEightEightNineProvides:
    def test_is_compliant(self, entity_provides_covered_tele):
        assert entity_provides_covered_tele.is_compliant is False

    def test_status_text(self, entity_provides_covered_tele):
        assert (
            entity_provides_covered_tele.status_text
            == "PROVIDES COVERED TELECOMMUNICATIONS"
        )

    def test_far_provision_date(self, entity_provides_covered_tele):
        assert entity_provides_covered_tele.far_provision_date == "OCT 2020"

    def test_far_text_c1(self, entity_provides_covered_tele):
        assert (
            entity_provides_covered_tele.far["52.204-26.c.1"]["text"]
            == "(1) The Offeror represents that it DOES provide covered "
            + "telecommunications equipment or services as a part of its offered "
            + "products or services to the Government in the performance of any "
            + "contract, subcontract, or other contractual instrument."
        )

    def test_far_text_c2(self, entity_provides_covered_tele):
        assert (
            entity_provides_covered_tele.far["52.204-26.c.2"]["text"]
            == "(2) After conducting a reasonable inquiry for purposes of this "
            + "representation, the offeror represents that it DOES NOT use covered "
            + "telecommunications equipment or services, or any equipment, system, "
            + "or service that uses covered telecommunications equipment or "
            + "services."
        )


class TestEightEightNineUses:
    def test_is_compliant(self, entity_uses_covered_tele):
        assert entity_uses_covered_tele.is_compliant is False

    def test_status_text(self, entity_uses_covered_tele):
        assert entity_uses_covered_tele.status_text == "USES COVERED TELECOMMUNICATIONS"

    def test_far_provision_date(self, entity_uses_covered_tele):
        assert entity_uses_covered_tele.far_provision_date == "OCT 2020"

    def test_far_text_c1(self, entity_uses_covered_tele):
        assert (
            entity_uses_covered_tele.far["52.204-26.c.1"]["text"]
            == "(1) The Offeror represents that it DOES NOT provide covered "
            + "telecommunications equipment or services as a part of its offered "
            + "products or services to the Government in the performance of any "
            + "contract, subcontract, or other contractual instrument."
        )

    def test_far_text_c2(self, entity_uses_covered_tele):
        assert (
            entity_uses_covered_tele.far["52.204-26.c.2"]["text"]
            == "(2) After conducting a reasonable inquiry for purposes of this "
            + "representation, the offeror represents that it DOES use covered "
            + "telecommunications equipment or services, or any equipment, system, "
            + "or service that uses covered telecommunications equipment or "
            + "services."
        )


class TestEightEightNineProvidesAndUses:
    def test_is_compliant(self, entity_provides_and_uses_covered_tele):
        assert entity_provides_and_uses_covered_tele.is_compliant is False

    def test_status_text(self, entity_provides_and_uses_covered_tele):
        assert (
            entity_provides_and_uses_covered_tele.status_text
            == "PROVIDES AND USES COVERED TELECOMMUNICATIONS"
        )

    def test_far_provision_date(self, entity_provides_and_uses_covered_tele):
        assert entity_provides_and_uses_covered_tele.far_provision_date == "OCT 2020"

    def test_far_text_c1(self, entity_provides_and_uses_covered_tele):
        assert (
            entity_provides_and_uses_covered_tele.far["52.204-26.c.1"]["text"]
            == "(1) The Offeror represents that it DOES provide covered "
            + "telecommunications equipment or services as a part of its offered "
            + "products or services to the Government in the performance of any "
            + "contract, subcontract, or other contractual instrument."
        )

    def test_far_text_c2(self, entity_provides_and_uses_covered_tele):
        assert (
            entity_provides_and_uses_covered_tele.far["52.204-26.c.2"]["text"]
            == "(2) After conducting a reasonable inquiry for purposes of this "
            + "representation, the offeror represents that it DOES use covered "
            + "telecommunications equipment or services, or any equipment, system, "
            + "or service that uses covered telecommunications equipment or "
            + "services."
        )


class TestEightEightNineProvidesAndNoC2:
    def test_is_compliant(self, entity_provides_and_no_c2):
        assert entity_provides_and_no_c2.is_compliant is False

    def test_status_text(self, entity_provides_and_no_c2):
        assert entity_provides_and_no_c2.status_text == "OUTDATED FAR (No part (C)(2))"

    def test_far_provision_date(self, entity_provides_and_no_c2):
        assert entity_provides_and_no_c2.far_provision_date == "DEC 2019"

    def test_far_text_c1(self, entity_provides_and_no_c2):
        assert (
            entity_provides_and_no_c2.far["52.204-26.c.1"]["text"]
            == "(1) The Offeror represents that it DOES provide covered "
            + "telecommunications equipment or services as a part of its offered "
            + "products or services to the Government in the performance of any "
            + "contract, subcontract, or other contractual instrument."
        )

    def test_far_text_c2(self, entity_provides_and_no_c2):
        assert entity_provides_and_no_c2.far["52.204-26.c.2"]["text"] is None


class TestEightEightNineDoesNotProvideAndNoC2:
    def test_is_compliant(self, entity_does_not_provide_and_no_c2):
        assert entity_does_not_provide_and_no_c2.is_compliant is False

    def test_status_text(self, entity_does_not_provide_and_no_c2):
        assert (
            entity_does_not_provide_and_no_c2.status_text
            == "OUTDATED FAR (No part (C)(2))"
        )

    def test_far_provision_date(self, entity_does_not_provide_and_no_c2):
        assert entity_does_not_provide_and_no_c2.far_provision_date == "DEC 2019"

    def test_far_text_c1(self, entity_does_not_provide_and_no_c2):
        assert (
            entity_does_not_provide_and_no_c2.far["52.204-26.c.1"]["text"]
            == "(1) The Offeror represents that it DOES NOT provide covered "
            + "telecommunications equipment or services as a part of its offered "
            + "products or services to the Government in the performance of any "
            + "contract, subcontract, or other contractual instrument."
        )

    def test_far_text_c2(self, entity_does_not_provide_and_no_c2):
        assert entity_does_not_provide_and_no_c2.far["52.204-26.c.2"]["text"] is None
