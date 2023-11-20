.. _community.okd.openshift_adm_migrate_template_instances_module:


******************************************************
community.okd.openshift_adm_migrate_template_instances
******************************************************

**Update TemplateInstances to point to the latest group-version-kinds**


Version added: 2.2.0

.. contents::
   :local:
   :depth: 1


Synopsis
--------
- Update TemplateInstances to point to the latest group-version-kinds.
- Analogous to ``oc adm migrate template-instances``.



Requirements
------------
The below requirements are needed on the host that executes this module.

- python >= 3.6
- kubernetes >= 12.0.0


Parameters
----------

.. raw:: html

    <table  border=0 cellpadding=0 class="documentation-table">
        <tr>
            <th colspan="2">Parameter</th>
            <th>Choices/<font color="blue">Defaults</font></th>
            <th width="100%">Comments</th>
        </tr>
            <tr>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>api_key</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Token used to authenticate with the API. Can also be specified via K8S_AUTH_API_KEY environment variable.</div>
                </td>
            </tr>
            <tr>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>ca_cert</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">path</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Path to a CA certificate used to authenticate with the API. The full certificate chain must be provided to avoid certificate validation errors. Can also be specified via K8S_AUTH_SSL_CA_CERT environment variable.</div>
                        <div style="font-size: small; color: darkgreen"><br/>aliases: ssl_ca_cert</div>
                </td>
            </tr>
            <tr>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>client_cert</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">path</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Path to a certificate used to authenticate with the API. Can also be specified via K8S_AUTH_CERT_FILE environment variable.</div>
                        <div style="font-size: small; color: darkgreen"><br/>aliases: cert_file</div>
                </td>
            </tr>
            <tr>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>client_key</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">path</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Path to a key file used to authenticate with the API. Can also be specified via K8S_AUTH_KEY_FILE environment variable.</div>
                        <div style="font-size: small; color: darkgreen"><br/>aliases: key_file</div>
                </td>
            </tr>
            <tr>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>context</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>The name of a context found in the config file. Can also be specified via K8S_AUTH_CONTEXT environment variable.</div>
                </td>
            </tr>
            <tr>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>host</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Provide a URL for accessing the API. Can also be specified via K8S_AUTH_HOST environment variable.</div>
                </td>
            </tr>
            <tr>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>impersonate_groups</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">list</span>
                         / <span style="color: purple">elements=string</span>
                    </div>
                    <div style="font-style: italic; font-size: small; color: darkgreen">added in 2.3.0</div>
                </td>
                <td>
                </td>
                <td>
                        <div>Group(s) to impersonate for the operation.</div>
                        <div>Can also be specified via K8S_AUTH_IMPERSONATE_GROUPS environment. Example: Group1,Group2</div>
                </td>
            </tr>
            <tr>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>impersonate_user</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                    <div style="font-style: italic; font-size: small; color: darkgreen">added in 2.3.0</div>
                </td>
                <td>
                </td>
                <td>
                        <div>Username to impersonate for the operation.</div>
                        <div>Can also be specified via K8S_AUTH_IMPERSONATE_USER environment.</div>
                </td>
            </tr>
            <tr>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>kubeconfig</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">raw</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Path to an existing Kubernetes config file. If not provided, and no other connection options are provided, the Kubernetes client will attempt to load the default configuration file from <em>~/.kube/config</em>. Can also be specified via K8S_AUTH_KUBECONFIG environment variable.</div>
                        <div>Multiple Kubernetes config file can be provided using separator &#x27;;&#x27; for Windows platform or &#x27;:&#x27; for others platforms.</div>
                        <div>The kubernetes configuration can be provided as dictionary. This feature requires a python kubernetes client version &gt;= 17.17.0. Added in version 2.2.0.</div>
                </td>
            </tr>
            <tr>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>namespace</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>The namespace that the template can be found in.</div>
                        <div>If no namespace if specified, migrate objects in all namespaces.</div>
                </td>
            </tr>
            <tr>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>no_proxy</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                    <div style="font-style: italic; font-size: small; color: darkgreen">added in 2.3.0</div>
                </td>
                <td>
                </td>
                <td>
                        <div>The comma separated list of hosts/domains/IP/CIDR that shouldn&#x27;t go through proxy. Can also be specified via K8S_AUTH_NO_PROXY environment variable.</div>
                        <div>Please note that this module does not pick up typical proxy settings from the environment (e.g. NO_PROXY).</div>
                        <div>This feature requires kubernetes&gt;=19.15.0. When kubernetes library is less than 19.15.0, it fails even no_proxy set in correct.</div>
                        <div>example value is &quot;localhost,.local,.example.com,127.0.0.1,127.0.0.0/8,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16&quot;</div>
                </td>
            </tr>
            <tr>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>password</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Provide a password for authenticating with the API. Can also be specified via K8S_AUTH_PASSWORD environment variable.</div>
                        <div>Please read the description of the <code>username</code> option for a discussion of when this option is applicable.</div>
                </td>
            </tr>
            <tr>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>persist_config</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">boolean</span>
                    </div>
                </td>
                <td>
                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                    <li>no</li>
                                    <li>yes</li>
                        </ul>
                </td>
                <td>
                        <div>Whether or not to save the kube config refresh tokens. Can also be specified via K8S_AUTH_PERSIST_CONFIG environment variable.</div>
                        <div>When the k8s context is using a user credentials with refresh tokens (like oidc or gke/gcloud auth), the token is refreshed by the k8s python client library but not saved by default. So the old refresh token can expire and the next auth might fail. Setting this flag to true will tell the k8s python client to save the new refresh token to the kube config file.</div>
                        <div>Default to false.</div>
                        <div>Please note that the current version of the k8s python client library does not support setting this flag to True yet.</div>
                        <div>The fix for this k8s python library is here: https://github.com/kubernetes-client/python-base/pull/169</div>
                </td>
            </tr>
            <tr>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>proxy</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>The URL of an HTTP proxy to use for the connection. Can also be specified via K8S_AUTH_PROXY environment variable.</div>
                        <div>Please note that this module does not pick up typical proxy settings from the environment (e.g. HTTP_PROXY).</div>
                </td>
            </tr>
            <tr>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>proxy_headers</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">dictionary</span>
                    </div>
                    <div style="font-style: italic; font-size: small; color: darkgreen">added in 2.0.0</div>
                </td>
                <td>
                </td>
                <td>
                        <div>The Header used for the HTTP proxy.</div>
                        <div>Documentation can be found here <a href='https://urllib3.readthedocs.io/en/latest/reference/urllib3.util.html?highlight=proxy_headers#urllib3.util.make_headers'>https://urllib3.readthedocs.io/en/latest/reference/urllib3.util.html?highlight=proxy_headers#urllib3.util.make_headers</a>.</div>
                </td>
            </tr>
                                <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>basic_auth</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Colon-separated username:password for basic authentication header.</div>
                        <div>Can also be specified via K8S_AUTH_PROXY_HEADERS_BASIC_AUTH environment.</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>proxy_basic_auth</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Colon-separated username:password for proxy basic authentication header.</div>
                        <div>Can also be specified via K8S_AUTH_PROXY_HEADERS_PROXY_BASIC_AUTH environment.</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>user_agent</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>String representing the user-agent you want, such as foo/1.0.</div>
                        <div>Can also be specified via K8S_AUTH_PROXY_HEADERS_USER_AGENT environment.</div>
                </td>
            </tr>

            <tr>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>username</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Provide a username for authenticating with the API. Can also be specified via K8S_AUTH_USERNAME environment variable.</div>
                        <div>Please note that this only works with clusters configured to use HTTP Basic Auth. If your cluster has a different form of authentication (e.g. OAuth2 in OpenShift), this option will not work as expected and you should look into the <span class='module'>community.okd.k8s_auth</span> module, as that might do what you need.</div>
                </td>
            </tr>
            <tr>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>validate_certs</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">boolean</span>
                    </div>
                </td>
                <td>
                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                    <li>no</li>
                                    <li>yes</li>
                        </ul>
                </td>
                <td>
                        <div>Whether or not to verify the API server&#x27;s SSL certificates. Can also be specified via K8S_AUTH_VERIFY_SSL environment variable.</div>
                        <div style="font-size: small; color: darkgreen"><br/>aliases: verify_ssl</div>
                </td>
            </tr>
            <tr>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>wait</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">boolean</span>
                    </div>
                </td>
                <td>
                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                    <li><div style="color: blue"><b>no</b>&nbsp;&larr;</div></li>
                                    <li>yes</li>
                        </ul>
                </td>
                <td>
                        <div>Whether to wait for certain resource kinds to end up in the desired state.</div>
                        <div>By default the module exits once Kubernetes has received the request.</div>
                        <div>Implemented for <code>state=present</code> for <code>Deployment</code>, <code>DaemonSet</code> and <code>Pod</code>, and for <code>state=absent</code> for all resource kinds.</div>
                        <div>For resource kinds without an implementation, <code>wait</code> returns immediately unless <code>wait_condition</code> is set.</div>
                </td>
            </tr>
            <tr>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>wait_condition</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">dictionary</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Specifies a custom condition on the status to wait for.</div>
                        <div>Ignored if <code>wait</code> is not set or is set to False.</div>
                </td>
            </tr>
                                <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>reason</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>The value of the reason field in your desired condition</div>
                        <div>For example, if a <code>Deployment</code> is paused, The <code>Progressing</code> <code>type</code> will have the <code>DeploymentPaused</code> reason.</div>
                        <div>The possible reasons in a condition are specific to each resource type in Kubernetes.</div>
                        <div>See the API documentation of the status field for a given resource to see possible choices.</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>status</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                    <li><div style="color: blue"><b>True</b>&nbsp;&larr;</div></li>
                                    <li>False</li>
                                    <li>Unknown</li>
                        </ul>
                </td>
                <td>
                        <div>The value of the status field in your desired condition.</div>
                        <div>For example, if a <code>Deployment</code> is paused, the <code>Progressing</code> <code>type</code> will have the <code>Unknown</code> status.</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>type</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>The type of condition to wait for.</div>
                        <div>For example, the <code>Pod</code> resource will set the <code>Ready</code> condition (among others).</div>
                        <div>Required if you are specifying a <code>wait_condition</code>.</div>
                        <div>If left empty, the <code>wait_condition</code> field will be ignored.</div>
                        <div>The possible types for a condition are specific to each resource type in Kubernetes.</div>
                        <div>See the API documentation of the status field for a given resource to see possible choices.</div>
                </td>
            </tr>

            <tr>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>wait_sleep</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">integer</span>
                    </div>
                </td>
                <td>
                        <b>Default:</b><br/><div style="color: blue">5</div>
                </td>
                <td>
                        <div>Number of seconds to sleep between checks.</div>
                </td>
            </tr>
            <tr>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>wait_timeout</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">integer</span>
                    </div>
                </td>
                <td>
                        <b>Default:</b><br/><div style="color: blue">120</div>
                </td>
                <td>
                        <div>How long in seconds to wait for the resource to end up in the desired state.</div>
                        <div>Ignored if <code>wait</code> is not set.</div>
                </td>
            </tr>
    </table>
    <br/>


Notes
-----

.. note::
   - To avoid SSL certificate validation errors when ``validate_certs`` is *True*, the full certificate chain for the API server must be provided via ``ca_cert`` or in the kubeconfig file.



Examples
--------

.. code-block:: yaml

    - name: Migrate TemplateInstances in namespace=test
      community.okd.openshift_adm_migrate_template_instances:
        namespace: test
      register: _result

    - name: Migrate TemplateInstances in all namespaces
      community.okd.openshift_adm_migrate_template_instances:
      register: _result



Return Values
-------------
Common return values are documented `here <https://docs.ansible.com/ansible/latest/reference_appendices/common_return_values.html#common-return-values>`_, the following are the fields unique to this module:

.. raw:: html

    <table border=0 cellpadding=0 class="documentation-table">
        <tr>
            <th colspan="1">Key</th>
            <th>Returned</th>
            <th width="100%">Description</th>
        </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="return-"></div>
                    <b>result</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">list</span>
                       / <span style="color: purple">elements=dictionary</span>
                    </div>
                </td>
                <td>success</td>
                <td>
                            <div>List with all TemplateInstances that have been migrated.</div>
                    <br/>
                        <div style="font-size: smaller"><b>Sample:</b></div>
                        <div style="font-size: smaller; color: blue; word-wrap: break-word; word-break: break-all;">[{&#x27;apiVersion&#x27;: &#x27;template.openshift.io/v1&#x27;, &#x27;kind&#x27;: &#x27;TemplateInstance&#x27;, &#x27;metadata&#x27;: {&#x27;creationTimestamp&#x27;: &#x27;2021-11-10T11:12:09Z&#x27;, &#x27;finalizers&#x27;: [&#x27;template.openshift.io/finalizer&#x27;], &#x27;managedFields&#x27;: [{&#x27;apiVersion&#x27;: &#x27;template.openshift.io/v1&#x27;, &#x27;fieldsType&#x27;: &#x27;FieldsV1&#x27;, &#x27;fieldsV1&#x27;: {&#x27;f:spec&#x27;: {&#x27;f:template&#x27;: {&#x27;f:metadata&#x27;: {&#x27;f:name&#x27;: {}}, &#x27;f:objects&#x27;: {}, &#x27;f:parameters&#x27;: {}}}}, &#x27;manager&#x27;: &#x27;kubectl-create&#x27;, &#x27;operation&#x27;: &#x27;Update&#x27;, &#x27;time&#x27;: &#x27;2021-11-10T11:12:09Z&#x27;}, {&#x27;apiVersion&#x27;: &#x27;template.openshift.io/v1&#x27;, &#x27;fieldsType&#x27;: &#x27;FieldsV1&#x27;, &#x27;fieldsV1&#x27;: {&#x27;f:metadata&#x27;: {&#x27;f:finalizers&#x27;: {&#x27;.&#x27;: {}, &#x27;v:&quot;template.openshift.io/finalizer&quot;&#x27;: {}}}, &#x27;f:status&#x27;: {&#x27;f:conditions&#x27;: {}}}, &#x27;manager&#x27;: &#x27;openshift-controller-manager&#x27;, &#x27;operation&#x27;: &#x27;Update&#x27;, &#x27;time&#x27;: &#x27;2021-11-10T11:12:09Z&#x27;}, {&#x27;apiVersion&#x27;: &#x27;template.openshift.io/v1&#x27;, &#x27;fieldsType&#x27;: &#x27;FieldsV1&#x27;, &#x27;fieldsV1&#x27;: {&#x27;f:status&#x27;: {&#x27;f:objects&#x27;: {}}}, &#x27;manager&#x27;: &#x27;OpenAPI-Generator&#x27;, &#x27;operation&#x27;: &#x27;Update&#x27;, &#x27;time&#x27;: &#x27;2021-11-10T11:12:33Z&#x27;}], &#x27;name&#x27;: &#x27;demo&#x27;, &#x27;namespace&#x27;: &#x27;test&#x27;, &#x27;resourceVersion&#x27;: &#x27;545370&#x27;, &#x27;uid&#x27;: &#x27;09b795d7-7f07-4d94-bf0f-2150ee66f88d&#x27;}, &#x27;spec&#x27;: {&#x27;requester&#x27;: {&#x27;groups&#x27;: [&#x27;system:masters&#x27;, &#x27;system:authenticated&#x27;], &#x27;username&#x27;: &#x27;system:admin&#x27;}, &#x27;template&#x27;: {&#x27;metadata&#x27;: {&#x27;creationTimestamp&#x27;: None, &#x27;name&#x27;: &#x27;template&#x27;}, &#x27;objects&#x27;: [{&#x27;apiVersion&#x27;: &#x27;v1&#x27;, &#x27;kind&#x27;: &#x27;Secret&#x27;, &#x27;metadata&#x27;: {&#x27;labels&#x27;: {&#x27;foo&#x27;: &#x27;bar&#x27;}, &#x27;name&#x27;: &#x27;secret&#x27;}}, {&#x27;apiVersion&#x27;: &#x27;apps/v1&#x27;, &#x27;kind&#x27;: &#x27;Deployment&#x27;, &#x27;metadata&#x27;: {&#x27;name&#x27;: &#x27;deployment&#x27;}, &#x27;spec&#x27;: {&#x27;replicas&#x27;: 0, &#x27;selector&#x27;: {&#x27;matchLabels&#x27;: {&#x27;key&#x27;: &#x27;value&#x27;}}, &#x27;template&#x27;: {&#x27;metadata&#x27;: {&#x27;labels&#x27;: {&#x27;key&#x27;: &#x27;value&#x27;}}, &#x27;spec&#x27;: {&#x27;containers&#x27;: [{&#x27;image&#x27;: &#x27;k8s.gcr.io/e2e-test-images/agnhost:2.32&#x27;, &#x27;name&#x27;: &#x27;hello-openshift&#x27;}]}}}}, {&#x27;apiVersion&#x27;: &#x27;v1&#x27;, &#x27;kind&#x27;: &#x27;Route&#x27;, &#x27;metadata&#x27;: {&#x27;name&#x27;: &#x27;route&#x27;}, &#x27;spec&#x27;: {&#x27;to&#x27;: {&#x27;name&#x27;: &#x27;foo&#x27;}}}], &#x27;parameters&#x27;: [{&#x27;name&#x27;: &#x27;NAME&#x27;, &#x27;value&#x27;: &#x27;${NAME}&#x27;}]}}, &#x27;status&#x27;: {&#x27;conditions&#x27;: [{&#x27;lastTransitionTime&#x27;: &#x27;2021-11-10T11:12:09Z&#x27;, &#x27;message&#x27;: &#x27;&#x27;, &#x27;reason&#x27;: &#x27;Created&#x27;, &#x27;status&#x27;: &#x27;True&#x27;, &#x27;type&#x27;: &#x27;Ready&#x27;}], &#x27;objects&#x27;: [{&#x27;ref&#x27;: {&#x27;apiVersion&#x27;: &#x27;v1&#x27;, &#x27;kind&#x27;: &#x27;Secret&#x27;, &#x27;name&#x27;: &#x27;secret&#x27;, &#x27;namespace&#x27;: &#x27;test&#x27;, &#x27;uid&#x27;: &#x27;33fad364-6d47-4f9c-9e51-92cba5602a57&#x27;}}, {&#x27;ref&#x27;: {&#x27;apiVersion&#x27;: &#x27;apps/v1&#x27;, &#x27;kind&#x27;: &#x27;Deployment&#x27;, &#x27;name&#x27;: &#x27;deployment&#x27;, &#x27;namespace&#x27;: &#x27;test&#x27;, &#x27;uid&#x27;: &#x27;3b527f88-42a1-4811-9e2f-baad4e4d8807&#x27;}}, {&#x27;ref&#x27;: {&#x27;apiVersion&#x27;: &#x27;route.openshift.io/v1.Route&#x27;, &#x27;kind&#x27;: &#x27;Route&#x27;, &#x27;name&#x27;: &#x27;route&#x27;, &#x27;namespace&#x27;: &#x27;test&#x27;, &#x27;uid&#x27;: &#x27;5b5411de-8769-4e27-ba52-6781630e4008&#x27;}}]}}, &#x27;...&#x27;]</div>
                </td>
            </tr>
    </table>
    <br/><br/>


Status
------


Authors
~~~~~~~

- Alina Buzachis (@alinabuzachis)
