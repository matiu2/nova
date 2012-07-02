# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2011 OpenStack LLC.
# Copyright 2012 Michael Still and Canonical Inc
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from migrate import ForeignKeyConstraint
from sqlalchemy import MetaData, String, Table, DateTime, Text, Boolean
from sqlalchemy import select, Column, ForeignKey, Integer
from nova.openstack.common import timeutils

from nova import log as logging


LOG = logging.getLogger(__name__)


def upgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine
    instances = Table('instances', meta, autoload=True)
    instance_action_log = Table('instance_action_log', meta,
        Column('id', Integer, primary_key=True, nullable=False),
        Column('instance_uuid', String(36), ForeignKey('instances.uuid'), nullable=False),
        Column('action_name', String(255)),
        Column('created_at', DateTime),
        Column('updated_at', DateTime),
        Column('deleted_at', DateTime),
        Column('deleted', Boolean),
        Column('requesting_ip', String(255), nullable=False),
        Column('response_code', Integer, nullable=False),
        Column('project_id', Text, nullable=False),
        Column('user_id', Text, nullable=False),
        Column('extra', Text),
        mysql_engine='InnoDB',
        mysql_charset='utf8'
    )
    instance_action_log.create()


def downgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine
    instance_action_log = Table('instance_action_log', meta, autoload=True)
    instance_action_log.drop()
