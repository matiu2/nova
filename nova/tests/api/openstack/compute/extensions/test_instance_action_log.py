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
        self.user = 'mister cool'
        self.project = 'cool project'
        self.remoteIP = '1.2.3.4'
        self.uuid = 'abcdefg'

    def _makeReq(self):
        req = fakes.HTTPRequest.blank('/v2/fake/servers/create')
        req._headers = {
            'X-Auth-User': self.user,
            'X-Auth-Project-Id': self.project,
        }
        req.environ['REMOTE_ADDR'] = self.remoteIP
        return req

    def _checkResult(self, action_name, expected_response_code=200):
        result = instance_action_log_get_by_instance_uuid(
            FakeContext(), self.uuid)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['instance_uuid'], self.uuid)
        self.assertEqual(result[0]['user_id'], self.user)
        self.assertEqual(result[0]['project_id'], self.project)
        self.assertEqual(result[0]['action_name'], action_name)
        # Must have been logged in last 60 seconds..
        self.assert_(datetime.now() - result[0]['created_at'] < timedelta(0,60))
        self.assertEqual(result[0]['response_code'], expected_response_code)
        self.assertEqual(result[0]['requesting_ip'], self.remoteIP)
        return result

    def test_create(self):
        req = self._makeReq()
        body = {'server':
                {'ip': '1.2.3.4',
                 'name': 'a server',
                 'info': 'this all gets logged',
                }}
        resp_obj = FakeResponse(200, {'server': {'id': self.uuid}})
        self.controller.create(req, body, resp_obj)
        result = self._checkResult('create')
        self.assertEqual(result[0]['extra'], \
            "{'info': 'this all gets logged', "
            "'ip': '1.2.3.4', 'name': 'a server'}"
        )

    def test_delete(self):
        pass

    def test_password(self):
        pass

    def test_resize(self):
        pass

    def test_rebuild(self):
        pass

    def test_create_image(self):
        pass

    def test_reboot(self):
        pass

    def test_resize(self):
        pass

    def test_revert_resize(self):
        pass

    def test_confirm_resize(self):
        pass

    def test_rescue(self):
        pass

    def test_unrescue(self):
        pass

    def test_clearState(self):
        pass

    def test_addIP(self):
        pass

    def test_removeIP(self):
        pass
