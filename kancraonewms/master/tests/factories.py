from factory import Faker
from factory import SubFactory
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyChoice
from factory.fuzzy import FuzzyDecimal

from kancraonewms.master.models import UOM
from kancraonewms.master.models import Item
from kancraonewms.master.models import ItemUOM
from kancraonewms.master.models import Rack
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
