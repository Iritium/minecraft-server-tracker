"""
    The models are divided into 2 main categories:
    - Normal models
    - Record models

    **Normal** models hold data that is constant and never changes, such as server address or player username.
    Although you can change this data, from the perspective of this scrapper, it is permanent since I'm not going to build some advanced systems
    for username histories (because there are tools like [NameMC](https://namemc.com/) for that purpose already) or server IP address history
    (because there is no way for the scrapper to know past IPs).

    **Record** models hold data that can change over time, such as server version (server can update to a new version), server MOTD/description
    (can be changed in server properties), player count, etc.
"""

import typing as t

from mst.settings import DATABASE_PATH, DATABASE_DATETIME_FILE_FORMAT

from pathlib import Path
from datetime import datetime

from peewee import *

__all__ = ['Server', 'ServerRecord', 'Player', 'ALL_MODELS', 'initialize_database']



class Server(Model):
    """
        - `hostname` - Server hostname/IP address
        - `port` - Server port
        - `source` - From what server list page was the server scrapped

        ### Backrefs:
        - `records` - All record for this server
    """

    hostname = CharField()
    port = IntegerField(default=25565)
    source = CharField(null=True, choices=())
    records: t.Iterable['ServerRecord']


    class Meta:
        db_table = 'servers'



class Record(Model):
    """
        - `timestamp` - The timestamp of the record
    """

    timestamp = DateTimeField(default=datetime.now)



class ServerRecord(Record):
    """
        - `latency` - Server latency (in ms)
        - `version` - Server version
        - `is_modded` - Is the server modded?
        - `description` - Server MOTD/description
        - `max_players` - Max players online
        - `online_players_number` - Players online (number)
        - `server` - Server that this record belongs to

        ### Backrefs:
        - `online_players` - Players online (list)
    """

    latency = FloatField(null=True)
    version = CharField(null=True)
    is_modded = BooleanField(default=False)
    description = TextField(null=True)
    max_players = IntegerField()
    online_players_number = IntegerField(default=0)
    server = ForeignKeyField(Server, backref='records', null=True)
    rs_players: t.Iterable['PlayerRecordsRelationship']


    class Meta:
        db_table = 'server_records'



class Player(Model):
    """
        - `uuid` - UUID
        - `username` - Username
        - `server_record` - `ServerRecord` where this player was last seen at
    """

    uuid = CharField(max_length=36)
    username = CharField(max_length=16)
    rs_server_records: t.Iterable['PlayerRecordsRelationship']


    class Meta:
        db_table = 'players'



class PlayerRecordsRelationship(Model):
    player = ForeignKeyField(Player, backref='rs_server_records')
    record = ForeignKeyField(ServerRecord, backref='rs_players')

    
    class Meta:
        db_table = 'rs_player_server_records'




ALL_MODELS: t.List[t.Type[Model]] = [Server, ServerRecord, Player, PlayerRecordsRelationship]


def initialize_database(database_name: Path=Path(f"{datetime.now().strftime(DATABASE_DATETIME_FILE_FORMAT)}.db"), directory_path: Path=DATABASE_PATH, *args, **kwargs) -> SqliteDatabase:
    database = SqliteDatabase(Path(directory_path, database_name), *args, **kwargs)
    database.bind(ALL_MODELS)
    database.create_tables(ALL_MODELS)

    return database



if __name__ == "__main__":
    initialize_database()