from factory import DjangoModelFactory, Faker
from factory.fuzzy import FuzzyChoice

from kancraonewms.master.models import Item, UOM


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
