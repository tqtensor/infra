"""A Python Pulumi program"""

from resources.ec2.airbyte import create_airbyte_instance
from resources.ec2.nextcloud import create_nextcloud_instance
from resources.iam.nextcloud import create_nextcloud_user

create_airbyte_instance()
create_nextcloud_instance()
create_nextcloud_user()
