from factory import Faker
from factory import SubFactory
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyChoice

from kancraonewms.organizations.models import Company
from kancraonewms.organizations.models import Warehouse


class CompanyFactory(DjangoModelFactory):
    code = Faker("lexify", text="COMP-????")
    name = Faker("company")
    legal_name = Faker("company")
    company_type = FuzzyChoice(["own", "customer", "vendor", "both"])
    tax_id = Faker("numerify", text="##.###.###.#-###.###")
    phone = Faker("phone_number")
    email = Faker("company_email")
    website = Faker("url")
    address = Faker("street_address")
    city = Faker("city")
    state = Faker("state")
    postal_code = Faker("postcode")
    country = "Indonesia"
    currency = "IDR"
    payment_terms = Faker("random_int", min=0, max=90)
    credit_limit = Faker("pydecimal", left_digits=8, right_digits=2, positive=True)
    is_active = True
    notes = Faker("paragraph")

    class Meta:
        model = Company


class WarehouseFactory(DjangoModelFactory):
    company = SubFactory(CompanyFactory)
    code = Faker("lexify", text="WH-????")
    name = Faker("bs")
    description = Faker("paragraph")
    address_line1 = Faker("street_address")
    address_line2 = Faker("secondary_address")
    city = Faker("city")
    state = Faker("state")
    postal_code = Faker("postcode")
    country = "Indonesia"
    phone = Faker("phone_number")
    email = Faker("company_email")
    is_active = True
    is_default = False

    class Meta:
        model = Warehouse
