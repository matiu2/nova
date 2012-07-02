# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2011 OpenStack LLC.
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

from datetime import timedelta, datetime
from nova import test
from nova.tests.api.openstack import fakes
from nova.context import RequestContext
from nova.api.openstack.compute.contrib.instance_action_log import \
     InstanceActionLogController
from nova.db.api import instance_action_log_get_by_instance_uuid


class FakeResponse(object):
    """We need to make up a response so that the loggers can log things"""

    def __init__(self, code=200, obj=None):
        self.code = code
        self.obj = obj


class FakeContext(RequestContext):

    def __init__(self, user_name='fake_admin', project='fake_project'):
        super(FakeContext, self).__init__(user_name, project, is_admin=True)


class InstanceActionLogTest(test.TestCase):

    def setUp(self):
        super(InstanceActionLogTest, self).setUp()
        self.controller = InstanceActionLogController()

    def test_create(self):
        req = fakes.HTTPRequest.blank('/v2/fake/servers/create')
        req._headers = {
            'X-Auth-User': 'mister cool',
            'X-Auth-Project-Id': 'cool project'
        }
        req.environ['REMOTE_ADDR'] = '1.2.3.4'
        body = {'server':
                {'ip': '1.2.3.4',
                 'name': 'a server',
                 'info': 'this all gets logged',
                }}
        resp_obj = FakeResponse(200, {'server': {'id': '1234'}})
        self.controller.create(req, body, resp_obj)
        result = instance_action_log_get_by_instance_uuid(
            FakeContext(), '1234')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['extra'], \
            "{'info': 'this all gets logged', "
            "'ip': '1.2.3.4', 'name': 'a server'}"
        )
        self.assertEqual(result[0]['instance_uuid'], '1234')
        self.assertEqual(result[0]['user_id'], 'mister cool')
        self.assertEqual(result[0]['project_id'], 'cool project')
        self.assertEqual(result[0]['action_name'], 'create')
        # Must have been logged in last 60 seconds..
        self.assert_(datetime.now() - result[0]['created_at'] < timedelta(0,60))
        self.assertEqual(result[0]['response_code'], 200)
        self.assertEqual(result[0]['requesting_ip'], '1.2.3.4')
