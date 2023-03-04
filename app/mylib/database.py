import dataset
from .errors import *


DATABASE = "postgresql://postgres:pass2023@postgres:5432/postgres"
db = dataset.connect(DATABASE)

union_table = db["union_table"]
dest_table = db["dest_table"]
document_table = db["document_table"]


def is_union_exist(union_name, union_type):
    return union_table.find_one(name=union_name, type=union_type) is not None


class Union:
    def __init__(self, id=None, role_id=None, name=None, type=None):
        if id:
            data = union_table.find_one(id=id)
        elif role_id:
            data = union_table.find_one(role_id=role_id)
        elif name and type:
            data = union_table.find_one(name=name, type=type)
        else:
            raise MissingRequiredArgument()
        if data is None:
            raise UnionNotExist()
        self.id = data["id"]
        self.role_id = data["role_id"]
        self.name = data["name"]
        self.type = data["type"]
        self.channel_id = data["channel_id"]

    def update(self):
        union_table.update(vars(self), ["id"])

    def delete(self):
        union_table.delete(id=self.id)


def is_dest_exist(dest_id):
    return dest_table.find_one(id=dest_id) is not None


def get_all_dest():
    dest_id_list = [data["id"] for data in dest_table.all()]
    return [Dest(id=dest_id) for dest_id in dest_id_list]


def get_dests(role_id=None):
    dest_id_list = [
        data["id"] for data in dest_table.all() if data["role_id"] == role_id
    ]
    return [Dest(id=dest_id) for dest_id in dest_id_list]


class Dest:
    def __init__(self, id=None, name=None):
        if name:
            data = dest_table.find_one(name=name)
        elif id:
            data = dest_table.find_one(id=id)
        else:
            raise MissingRequiredArgument()
        if data is None:
            raise DestNotExist()
        self.id = data["id"]
        self.name = data["name"]
        self.role_id = data["role_id"]
        self.limit = data["limit"]
        self.format = data["format"]
        self.handler_id = data["handler_id"]

    def delete(self):
        dest_table.delete(id=self.id)


def is_document_exist(dest_id, union_id):
    return document_table.find_one(dest_id=dest_id, union_id=union_id) is not None


def get_documents(union_id):
    document_id_list = [
        data["id"] for data in document_table.all() if data["union_id"] == union_id
    ]
    return [Document(id=document_id) for document_id in document_id_list]


class Document:
    def __init__(self, id=None, dest_id=None, union_id=None):
        if id:
            data = document_table.find_one(id=id)
        elif dest_id and union_id:
            data = document_table.find_one(dest_id=dest_id, union_id=union_id)
        else:
            raise MissingRequiredArgument()
        if data is None:
            raise DestNotExist()
        self.id = data["id"]
        self.dest_id = data["dest_id"]
        self.union_id = data["union_id"]
        self.msg_url = data["msg_url"]

    def update(self):
        document_table.update(vars(self), ["id"])
