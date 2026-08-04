from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from unittest.mock import MagicMock, patch, PropertyMock
from ansible_collections.community.okd.plugins.module_utils.openshift_adm_prune_auth import OpenShiftAdmPruneAuth

COMMON = 'ansible_collections.community.okd.plugins.module_utils.openshift_common.AnsibleOpenshiftModule'


class TestOpenShiftAdmPruneAuth:

    @patch(f'{COMMON}.kubernetes_facts', create=True)
    @patch(f'{COMMON}.find_resource', create=True)
    @patch(f'{COMMON}.__init__', return_value=None)
    @patch(f'{COMMON}.params', new_callable=PropertyMock)
    @patch(f'{COMMON}.check_mode', new_callable=PropertyMock)
    def test_update_security_context_success(self, mock_check, mock_params, mock_init, mock_find, mock_facts):
        mock_params.return_value = {'resource': 'users'}
        mock_check.return_value = False
        module = OpenShiftAdmPruneAuth()

        mock_facts.return_value = {
            "api_found": True,
            "resources": [
                {
                    "metadata": {"name": "restricted"},
                    "users": ["alice", "bob"]
                }
            ]
        }

        mock_res = MagicMock()
        mock_find.return_value = mock_res

        candidates, changed = module.update_security_context(ref_names=["alice"], key="users")

        assert changed is True
        assert "restricted" in candidates

        sent_data = mock_res.apply.call_args[0][0]
        assert "alice" not in sent_data["users"]
        assert "bob" in sent_data["users"]

    @patch(f'{COMMON}.kubernetes_facts', create=True)
    @patch(f'{COMMON}.find_resource', create=True)
    @patch(f'{COMMON}.__init__', return_value=None)
    @patch(f'{COMMON}.params', new_callable=PropertyMock)
    def test_update_security_context_no_change(self, mock_params, mock_init, mock_find, mock_facts):
        mock_params.return_value = {'resource': 'users'}
        module = OpenShiftAdmPruneAuth()

        mock_facts.return_value = {
            "api_found": True,
            "resources": [{"metadata": {"name": "any"}, "users": ["bob"]}]
        }

        candidates, changed = module.update_security_context(ref_names=["alice"], key="users")

        assert changed is False
        assert len(candidates) == 0
        assert mock_find.return_value.apply.called is False

    @patch(f'{COMMON}.kubernetes_facts', create=True)
    @patch(f'{COMMON}.find_resource', create=True)
    @patch(f'{COMMON}.__init__', return_value=None)
    @patch(f'{COMMON}.params', new_callable=PropertyMock)
    @patch(f'{COMMON}.fail_json')
    def test_update_security_context_not_found(self, mock_fail, mock_params, mock_init, mock_find, mock_facts):
        mock_params.return_value = {'resource': 'users'}
        module = OpenShiftAdmPruneAuth()

        mock_facts.return_value = {
            "api_found": False,
            "resources": [],
            "msg": "API not found"
        }

        module.update_security_context(ref_names=["alice"], key="users")

        assert mock_fail.called
        assert mock_fail.call_args[1]['msg'] == "API not found"
