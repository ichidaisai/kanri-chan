import dataset


DATABASE = "postgresql://postgres:pass2023@postgres:5432/postgres"
db = dataset.connect(DATABASE)

group_table = db["group_table"]


def is_group_exist(group_name, group_type):
    return group_table.find_one(name=group_name, type=group_type) is not None


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


class MissingRequiredArgument(Exception):
    pass

class GroupNotExist(Exception):
    pass
