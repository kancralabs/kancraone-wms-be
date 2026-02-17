from factory import Faker
from factory import SubFactory
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyChoice
from factory.fuzzy import FuzzyDecimal

from kancraonewms.master.models import UOM
from kancraonewms.master.models import Accessibility
from kancraonewms.master.models import Item
from kancraonewms.master.models import ItemUOM
from kancraonewms.master.models import Menu
from kancraonewms.master.models import Rack
from kancraonewms.master.models import Role
from kancraonewms.master.models import RoleMenuAccess
from kancraonewms.organizations.tests.factories import WarehouseFactory


class ItemFactory(DjangoModelFactory):
    code = Faker("lexify", text="ITEM-????")
    name = Faker("sentence", nb_words=3)
    description = Faker("paragraph")
    unit = Faker("random_element", elements=["pcs", "kg", "liter", "box", "carton"])
    is_active = True

    class Meta:
        model = Item


class UOMFactory(DjangoModelFactory):
    code = Faker("lexify", text="UOM-???")
    name = Faker("word")
    description = Faker("sentence")
    uom_type = FuzzyChoice(["weight", "length", "volume", "quantity", "time", "other"])
    conversion_factor = Faker("pydecimal", left_digits=3, right_digits=4, positive=True)
    is_active = True

    class Meta:
        model = UOM


class ItemUOMFactory(DjangoModelFactory):
    item = SubFactory(ItemFactory)
    uom = SubFactory(UOMFactory)
    conversion_factor = FuzzyDecimal(0.01, 1000.0, precision=4)
    is_base_uom = False
    is_purchase_uom = True
    is_sales_uom = True
    is_stock_uom = True
    barcode = Faker("ean13")
    is_active = True

    class Meta:
        model = ItemUOM


class RackFactory(DjangoModelFactory):
    warehouse = SubFactory(WarehouseFactory)
    code = Faker("lexify", text="RACK-????")
    name = Faker("bs")
    description = Faker("paragraph")
    zone = Faker("random_element", elements=["A", "B", "C", "D"])
    aisle = Faker("numerify", text="A##")
    bay = Faker("numerify", text="B##")
    level = Faker("random_int", min=1, max=5)
    capacity = FuzzyDecimal(0.0, 1000.0, precision=2)
    max_weight = FuzzyDecimal(0.0, 5000.0, precision=2)
    is_active = True
    notes = Faker("sentence")

    class Meta:
        model = Rack


class RoleFactory(DjangoModelFactory):
    code = Faker("lexify", text="ROLE-???")
    name = Faker("job")
    description = Faker("sentence")
    is_active = True

    class Meta:
        model = Role


class AccessibilityFactory(DjangoModelFactory):
    role = SubFactory(RoleFactory)
    module = Faker(
        "random_element",
        elements=["master", "inventory", "transaction", "report"],
    )
    feature = Faker("random_element", elements=["item", "uom", "rack", "warehouse"])
    permission = FuzzyChoice(["create", "read", "update", "delete", "export", "import"])
    is_granted = True

    class Meta:
        model = Accessibility


class MenuFactory(DjangoModelFactory):
    code = Faker("lexify", text="MENU-???")
    name = Faker("bs")
    icon = Faker("word")
    url = Faker("uri_path")
    order = Faker("random_int", min=1, max=100)
    is_active = True
    module = Faker(
        "random_element",
        elements=["master", "inventory", "transaction", "report"],
    )

    class Meta:
        model = Menu


class RoleMenuAccessFactory(DjangoModelFactory):
    role = SubFactory(RoleFactory)
    menu = SubFactory(MenuFactory)
    can_access = True

    class Meta:
        model = RoleMenuAccess
