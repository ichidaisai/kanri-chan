import dataset


DATABASE = "postgresql://postgres:pass2023@postgres:5432/postgres"
db = dataset.connect(DATABASE)

group_table = db["group_table"]
item_table = db["item_table"]


def is_group_exist(group_name, group_type):
    return group_table.find_one(name=group_name, type=group_type) is not None


def is_item_exist(item_name):
    return item_table.find_one(name=item_name) is not None


def get_all_item():
    item_id_list = [data["id"] for data in item_table.all()]
    return [Item(id=item_id) for item_id in item_id_list]


def get_all_item_named(name):
    item_id_list = [data["id"] for data in item_table.all() if data["name"] == name]
    return [Item(id=item_id) for item_id in item_id_list]


class Group:
    def __init__(self, role_id=None, name=None, type=None):
        if role_id:
            data = group_table.find_one(role_id=role_id)
        elif name and type:
            data = group_table.find_one(name=name, type=type)
        else:
            raise MissingRequiredArgument()
        if data is None:
            raise GroupNotExist()
        self.role_id = data["role_id"]
        self.name = data["name"]
        self.type = data["type"]
        self.channel_id = data["channel_id"]

    def update(self):
        group_table.update(vars(self), ["role_id"])

    def delete(self):
        group_table.delete(role_id=self.role_id)


class Item:
    def __init__(self, name=None, id=None):
        if name:
            data = item_table.find_one(name=name)
        elif id:
            data = item_table.find_one(id=id)
        else:
            raise MissingRequiredArgument()
        if data is None:
            raise ItemNotExist()
        self.id = data["id"]
        self.name = data["name"]
        self.target_role_id = data["target_role_id"]
        self.limit = data["limit"]
        self.format = data["format"]
        self.handler = data["handler"]

    def delete(self):
        item_table.delete(id=self.id)


class MissingRequiredArgument(Exception):
    pass

class GroupNotExist(Exception):
    pass

class ItemNotExist(Exception):
    pass
