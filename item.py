from abc import ABC, abstractmethod

from exeptions import ItemCreationError


class AbstractCategory(ABC):
    def __init__(self, title: str, data: dict = None):
        self.title = title
        self.data = data
        super().__init__()

    @abstractmethod
    def get_info(self):
        pass


class Category(AbstractCategory):
    def get_info(self):
        return self.title


class SubCategory(AbstractCategory):
    def __init__(self, category: Category, title: str, data: dict = None):
        self.category = category
        super().__init__(title=title, data=data)

    def get_info(self):
        return f"{self.category.get_info()}:{self.title}"


class Item(object):
    def __init__(self, title: str, category: Category = None, sub_category: SubCategory = None, data: dict = None):
        if not type(category) is Category or type(sub_category) is SubCategory:
            raise ItemCreationError
        self._sub_category = sub_category
        self._category = category
        self.title = title
        self.data = data

    @property
    def category(self):
        return self._category or self._sub_category.category

    @property
    def sub_category(self):
        return self._sub_category

    def get_info(self):
        return self.title
