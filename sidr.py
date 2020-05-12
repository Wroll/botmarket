from botshop.db.utils import *


class GeneratorTestData:

    @classmethod
    def generate(cls):
        for _ in range(2):
            GeneratorHandler.create_news()
        a = GeneratorHandler.create_category()
        for _ in range(2):
            GeneratorHandler.create_product(a)
        b = GeneratorHandler.create_category()
        for _ in range(2):
            c = GeneratorHandler.create_subcategory(b)
            for _ in range(2):
                GeneratorHandler.create_product(c)


if __name__ == '__main__':
    GeneratorTestData.generate()
