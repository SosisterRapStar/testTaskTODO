from dataclasses import dataclass


@dataclass
class UseCases:

    async def get_my_notes():
        pass

    async def add_tag():
        pass

    async def create_note():
        pass

    async def change_note():
        pass

    async def find_nodes_by_tags():
        pass

    async def enter_to_my_account():
        pass

    async def create_account():
        pass
