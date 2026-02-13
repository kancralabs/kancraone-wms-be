from factory import DjangoModelFactory, Faker

from kancraonewms.master.models import Item


class ItemFactory(DjangoModelFactory):
    code = Faker("lexify", text="ITEM-????")
    name = Faker("sentence", nb_words=3)
    description = Faker("paragraph")
    unit = Faker("random_element", elements=["pcs", "kg", "liter", "box", "carton"])
    is_active = True
    
    class Meta:
        model = Item
