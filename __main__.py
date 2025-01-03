"""A Python Pulumi program"""

from resources.airbyte import create_airbyte
from resources.nextcloud import create_nextcloud


create_airbyte()
create_nextcloud()
