# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2011 OpenStack LLC.
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
#    under the License

"""Logs actions performed on instances"""

from nova.api.openstack import extensions
from nova.api.openstack import wsgi
from nova.db.api import instance_action_log_create
import pprint

ALIAS = 'OS-IAL' # Instance Action Log
XMLNS_DCF = "http://docs.openstack.org/compute/ext/instance_action_log/api/v2.0"
authorize = extensions.soft_extension_authorizer('compute', 'action_instance_log')


class InstanceActionLogController(wsgi.Controller):

    def _do_log(self, req, resp_obj, action_name, id, extra=''):
        context = req.environ['nova.context']
        user_name = req._headers.get('X-Auth-User')
        if user_name is None:
            # If this system is using noauth, the user name will actually be
            # in the auth-token, in the format: username:password
            token = req._headers.get('X-Auth-Token')
            if token is not None:
                user_name = token.split(':', 1)[0] # Don't want the password
            if not user_name:
                user_name = 'NOT-FOUND'

        instance_action_log = {
            'instance_uuid': id,
            'action_name': action_name,
            'requesting_ip': req.environ.get('REMOTE_ADDR', 'NOT-FOUND'),
            'response_code': resp_obj.code,
            'project_id': req._headers.get('X-Auth-Project-Id', 'NOT-FOUND'),
            'user_id': user_name,
            'extra': extra,
        }
        context = req.environ['nova.context']
        instance_action_log_create(context, instance_action_log)

    @wsgi.extends(wants_errors=True)
    def create(self, req, body, resp_obj):
        extra = pprint.pformat(body['server'])
        self._do_log(req, resp_obj, 'create', resp_obj.obj['server']['id'], extra)

    @wsgi.extends(wants_errors=True)
    def delete(self, req, id, resp_obj):
        self._do_log(req, resp_obj, 'delete', id)

    @wsgi.extends(action='changePassword', wants_errors=True)
    def _action_change_password(self, req, id, body, resp_obj):
        self._do_log(req, resp_obj, 'root-password', id)

    @wsgi.extends(action='resize', wants_errors=True)
    def _action_resize(self, req, id, body, resp_obj):
        extra = u'New Flavor: %s' % body['resize']['flavorRef']
        self._do_log(req, resp_obj, 'resize', id, extra)

    @wsgi.extends(wants_errors=True)
    def delete(self, req, resp_obj, id):
        self._do_log(req, resp_obj, 'delete', id)

    @wsgi.extends(action='rebuild', wants_errors=True)
    def _action_rebuild(self, req, id, body, resp_obj):
        extra = 'New Image: %s' % body['rebuild']['imageRef']
        self._do_log(req, resp_obj, 'rebuild', id, extra)

    @wsgi.extends(action='createImage', wants_errors=True)
    def _action_create_image(self, req, id, body, resp_obj):
        extra = u'name: %s\n' % body['createImage']['name']
        extra += u'metadata: %s' % pformat(body['createImage']['metadata'])
        self._do_log(req, resp_obj, 'volume-snapshot-create', id, extra)

    @wsgi.extends(action='reboot', wants_errors=True)
    def _action_reboot(self, req, id, body, resp_obj):
        extra = u'type: %s' % body['reboot']['type']
        self._do_log(req, resp_obj, 'reboot', id, extra)

    @wsgi.extends(action='confirmResize', wants_errors=True)
    def _action_confirm_resize(self, req, id, body, resp_obj):
        self._do_log(req, resp_obj, 'confirm-resize', id)

    @wsgi.extends(action='revertResize', wants_errors=True)
    def _action_revert_resize(self, req, id, body, resp_obj):
        self._do_log(req, resp_obj, 'revert-resize', id)


class Instance_action_log(extensions.ExtensionDescriptor):
    """Instance Action Log Extension"""

    name = "InstanceActionLog"
    alias = ALIAS
    namespace = XMLNS_DCF
    updated = "2012-06-23T00:00:00+00:00"

    def get_controller_extensions(self):
        servers_extension = extensions.ControllerExtension(
                self, 'servers', InstanceActionLogController())

        return [servers_extension]
