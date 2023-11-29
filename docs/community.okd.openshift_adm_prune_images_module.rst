.. _community.okd.openshift_adm_prune_images_module:


****************************************
community.okd.openshift_adm_prune_images
****************************************

**Remove unreferenced images**


Version added: 2.2.0

.. contents::
   :local:
   :depth: 1


Synopsis
--------
- This module allow administrators to remove references images.
- Note that if the ``namespace`` is specified, only references images on Image stream for the corresponding namespace will be candidate for prune if only they are not used or references in another Image stream from another namespace.
- Analogous to ``oc adm prune images``.



Requirements
------------
The below requirements are needed on the host that executes this module.

- python >= 3.6
- kubernetes >= 12.0.0
- docker-image-py


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
                    <b>all_images</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">boolean</span>
                    </div>
                </td>
                <td>
                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                    <li>no</li>
                                    <li><div style="color: blue"><b>yes</b>&nbsp;&larr;</div></li>
                        </ul>
                </td>
                <td>
                        <div>Include images that were imported from external registries as candidates for pruning.</div>
                        <div>If pruned, all the mirrored objects associated with them will also be removed from the integrated registry.</div>
                </td>
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
                    <b>ignore_invalid_refs</b>
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
                        <div>If set to <em>True</em>, the pruning process will ignore all errors while parsing image references.</div>
                        <div>This means that the pruning process will ignore the intended connection between the object and the referenced image.</div>
                        <div>As a result an image may be incorrectly deleted as unused.</div>
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
                    <b>keep_younger_than</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">integer</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Specify the minimum age (in minutes) of an image and its referrers for it to be considered a candidate for pruning.</div>
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
                        <div>Use to specify namespace for objects.</div>
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
                    <b>prune_over_size_limit</b>
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
                        <div>Specify if images which are exceeding LimitRanges specified in the same namespace, should be considered for pruning.</div>
                </td>
            </tr>
            <tr>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>prune_registry</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">boolean</span>
                    </div>
                </td>
                <td>
                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                    <li>no</li>
                                    <li><div style="color: blue"><b>yes</b>&nbsp;&larr;</div></li>
                        </ul>
                </td>
                <td>
                        <div>If set to <em>False</em>, the prune operation will clean up image API objects, but none of the associated content in the registry is removed.</div>
                </td>
            </tr>
            <tr>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>registry_ca_cert</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">path</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Path to a CA certificate used to contact registry. The full certificate chain must be provided to avoid certificate validation errors.</div>
                </td>
            </tr>
            <tr>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>registry_url</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>The address to use when contacting the registry, instead of using the default value.</div>
                        <div>This is useful if you can&#x27;t resolve or reach the default registry but you do have an alternative route that works.</div>
                        <div>Particular transport protocol can be enforced using &#x27;&lt;scheme&gt;://&#x27; prefix.</div>
                </td>
            </tr>
            <tr>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>registry_validate_certs</b>
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
    </table>
    <br/>


Notes
-----

.. note::
   - To avoid SSL certificate validation errors when ``validate_certs`` is *True*, the full certificate chain for the API server must be provided via ``ca_cert`` or in the kubeconfig file.



Examples
--------

.. code-block:: yaml

    # Prune if only images and their referrers were more than an hour old
    - name: Prune image with referrer been more than an hour old
      community.okd.openshift_adm_prune_images:
        keep_younger_than: 60

    # Remove images exceeding currently set limit ranges
    - name: Remove images exceeding currently set limit ranges
      community.okd.openshift_adm_prune_images:
        prune_over_size_limit: true

    # Force the insecure http protocol with the particular registry host name
    - name: Prune images using custom registry
      community.okd.openshift_adm_prune_images:
        registry_url: http://registry.example.org
        registry_validate_certs: false



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
                    <b>deleted_images</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">list</span>
                       / <span style="color: purple">elements=dictionary</span>
                    </div>
                </td>
                <td>success</td>
                <td>
                            <div>The images deleted.</div>
                    <br/>
                        <div style="font-size: smaller"><b>Sample:</b></div>
                        <div style="font-size: smaller; color: blue; word-wrap: break-word; word-break: break-all;">[{&#x27;apiVersion&#x27;: &#x27;image.openshift.io/v1&#x27;, &#x27;dockerImageLayers&#x27;: [{&#x27;mediaType&#x27;: &#x27;application/vnd.docker.image.rootfs.diff.tar.gzip&#x27;, &#x27;name&#x27;: &#x27;sha256:5e0b432e8ba9d9029a000e627840b98ffc1ed0c5172075b7d3e869be0df0fe9b&#x27;, &#x27;size&#x27;: 54932878}, {&#x27;mediaType&#x27;: &#x27;application/vnd.docker.image.rootfs.diff.tar.gzip&#x27;, &#x27;name&#x27;: &#x27;sha256:a84cfd68b5cea612a8343c346bfa5bd6c486769010d12f7ec86b23c74887feb2&#x27;, &#x27;size&#x27;: 5153424}, {&#x27;mediaType&#x27;: &#x27;application/vnd.docker.image.rootfs.diff.tar.gzip&#x27;, &#x27;name&#x27;: &#x27;sha256:e8b8f2315954535f1e27cd13d777e73da4a787b0aebf4241d225beff3c91cbb1&#x27;, &#x27;size&#x27;: 10871995}, {&#x27;mediaType&#x27;: &#x27;application/vnd.docker.image.rootfs.diff.tar.gzip&#x27;, &#x27;name&#x27;: &#x27;sha256:0598fa43a7e793a76c198e8d45d8810394e1cfc943b2673d7fcf5a6fdc4f45b3&#x27;, &#x27;size&#x27;: 54567844}, {&#x27;mediaType&#x27;: &#x27;application/vnd.docker.image.rootfs.diff.tar.gzip&#x27;, &#x27;name&#x27;: &#x27;sha256:83098237b6d3febc7584c1f16076a32ac01def85b0d220ab46b6ebb2d6e7d4d4&#x27;, &#x27;size&#x27;: 196499409}, {&#x27;mediaType&#x27;: &#x27;application/vnd.docker.image.rootfs.diff.tar.gzip&#x27;, &#x27;name&#x27;: &#x27;sha256:b92c73d4de9a6a8f6b96806a04857ab33cf6674f6411138603471d744f44ef55&#x27;, &#x27;size&#x27;: 6290769}, {&#x27;mediaType&#x27;: &#x27;application/vnd.docker.image.rootfs.diff.tar.gzip&#x27;, &#x27;name&#x27;: &#x27;sha256:ef9b6ee59783b84a6ec0c8b109c409411ab7c88fa8c53fb3760b5fde4eb0aa07&#x27;, &#x27;size&#x27;: 16812698}, {&#x27;mediaType&#x27;: &#x27;application/vnd.docker.image.rootfs.diff.tar.gzip&#x27;, &#x27;name&#x27;: &#x27;sha256:c1f6285e64066d36477a81a48d3c4f1dc3c03dddec9e72d97da13ba51bca0d68&#x27;, &#x27;size&#x27;: 234}, {&#x27;mediaType&#x27;: &#x27;application/vnd.docker.image.rootfs.diff.tar.gzip&#x27;, &#x27;name&#x27;: &#x27;sha256:a0ee7333301245b50eb700f96d9e13220cdc31871ec9d8e7f0ff7f03a17c6fb3&#x27;, &#x27;size&#x27;: 2349241}], &#x27;dockerImageManifestMediaType&#x27;: &#x27;application/vnd.docker.distribution.manifest.v2+json&#x27;, &#x27;dockerImageMetadata&#x27;: {&#x27;Architecture&#x27;: &#x27;amd64&#x27;, &#x27;Config&#x27;: {&#x27;Cmd&#x27;: [&#x27;python3&#x27;], &#x27;Env&#x27;: [&#x27;PATH=/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin&#x27;, &#x27;LANG=C.UTF-8&#x27;, &#x27;GPG_KEY=E3FF2839C048B25C084DEBE9B26995E310250568&#x27;, &#x27;PYTHON_VERSION=3.8.12&#x27;, &#x27;PYTHON_PIP_VERSION=21.2.4&#x27;, &#x27;PYTHON_SETUPTOOLS_VERSION=57.5.0&#x27;, &#x27;PYTHON_GET_PIP_URL=https://github.com/pypa/get-pip/raw/3cb8888cc2869620f57d5d2da64da38f516078c7/public/get-pip.py&#x27;, &#x27;PYTHON_GET_PIP_SHA256=c518250e91a70d7b20cceb15272209a4ded2a0c263ae5776f129e0d9b5674309&#x27;], &#x27;Image&#x27;: &#x27;sha256:cc3a2931749afa7dede97e32edbbe3e627b275c07bf600ac05bc0dc22ef203de&#x27;}, &#x27;Container&#x27;: &#x27;b43fcf5052feb037f6d204247d51ac8581d45e50f41c6be2410d94b5c3a3453d&#x27;, &#x27;ContainerConfig&#x27;: {&#x27;Cmd&#x27;: [&#x27;/bin/sh&#x27;, &#x27;-c&#x27;, &#x27;#(nop) &#x27;, &#x27;CMD [&quot;python3&quot;]&#x27;], &#x27;Env&#x27;: [&#x27;PATH=/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin&#x27;, &#x27;LANG=C.UTF-8&#x27;, &#x27;GPG_KEY=E3FF2839C048B25C084DEBE9B26995E310250568&#x27;, &#x27;PYTHON_VERSION=3.8.12&#x27;, &#x27;PYTHON_PIP_VERSION=21.2.4&#x27;, &#x27;PYTHON_SETUPTOOLS_VERSION=57.5.0&#x27;, &#x27;PYTHON_GET_PIP_URL=https://github.com/pypa/get-pip/raw/3cb8888cc2869620f57d5d2da64da38f516078c7/public/get-pip.py&#x27;, &#x27;PYTHON_GET_PIP_SHA256=c518250e91a70d7b20cceb15272209a4ded2a0c263ae5776f129e0d9b5674309&#x27;], &#x27;Hostname&#x27;: &#x27;b43fcf5052fe&#x27;, &#x27;Image&#x27;: &#x27;sha256:cc3a2931749afa7dede97e32edbbe3e627b275c07bf600ac05bc0dc22ef203de&#x27;}, &#x27;Created&#x27;: &#x27;2021-12-03T01:53:41Z&#x27;, &#x27;DockerVersion&#x27;: &#x27;20.10.7&#x27;, &#x27;Id&#x27;: &#x27;sha256:f746089c9d02d7126bbe829f788e093853a11a7f0421049267a650d52bbcac37&#x27;, &#x27;Size&#x27;: 347487141, &#x27;apiVersion&#x27;: &#x27;image.openshift.io/1.0&#x27;, &#x27;kind&#x27;: &#x27;DockerImage&#x27;}, &#x27;dockerImageMetadataVersion&#x27;: &#x27;1.0&#x27;, &#x27;dockerImageReference&#x27;: &#x27;python@sha256:a874dcabc74ca202b92b826521ff79dede61caca00ceab0b65024e895baceb58&#x27;, &#x27;kind&#x27;: &#x27;Image&#x27;, &#x27;metadata&#x27;: {&#x27;annotations&#x27;: {&#x27;image.openshift.io/dockerLayersOrder&#x27;: &#x27;ascending&#x27;}, &#x27;creationTimestamp&#x27;: &#x27;2021-12-07T07:55:30Z&#x27;, &#x27;name&#x27;: &#x27;sha256:a874dcabc74ca202b92b826521ff79dede61caca00ceab0b65024e895baceb58&#x27;, &#x27;resourceVersion&#x27;: &#x27;1139214&#x27;, &#x27;uid&#x27;: &#x27;33be6ab4-af79-4f44-a0fd-4925bd473c1f&#x27;}}, &#x27;...&#x27;]</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="return-"></div>
                    <b>updated_image_streams</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">list</span>
                       / <span style="color: purple">elements=dictionary</span>
                    </div>
                </td>
                <td>success</td>
                <td>
                            <div>The images streams updated.</div>
                    <br/>
                        <div style="font-size: smaller"><b>Sample:</b></div>
                        <div style="font-size: smaller; color: blue; word-wrap: break-word; word-break: break-all;">[{&#x27;apiVersion&#x27;: &#x27;image.openshift.io/v1&#x27;, &#x27;kind&#x27;: &#x27;ImageStream&#x27;, &#x27;metadata&#x27;: {&#x27;annotations&#x27;: {&#x27;openshift.io/image.dockerRepositoryCheck&#x27;: &#x27;2021-12-07T07:55:30Z&#x27;}, &#x27;creationTimestamp&#x27;: &#x27;2021-12-07T07:55:30Z&#x27;, &#x27;generation&#x27;: 1, &#x27;name&#x27;: &#x27;python&#x27;, &#x27;namespace&#x27;: &#x27;images&#x27;, &#x27;resourceVersion&#x27;: &#x27;1139215&#x27;, &#x27;uid&#x27;: &#x27;443bad2c-9fd4-4c8f-8a24-3eca4426b07f&#x27;}, &#x27;spec&#x27;: {&#x27;lookupPolicy&#x27;: {&#x27;local&#x27;: False}, &#x27;tags&#x27;: [{&#x27;annotations&#x27;: None, &#x27;from&#x27;: {&#x27;kind&#x27;: &#x27;DockerImage&#x27;, &#x27;name&#x27;: &#x27;python:3.8.12&#x27;}, &#x27;generation&#x27;: 1, &#x27;importPolicy&#x27;: {&#x27;insecure&#x27;: True}, &#x27;name&#x27;: &#x27;3.8.12&#x27;, &#x27;referencePolicy&#x27;: {&#x27;type&#x27;: &#x27;Source&#x27;}}]}, &#x27;status&#x27;: {&#x27;dockerImageRepository&#x27;: &#x27;image-registry.openshift-image-registry.svc:5000/images/python&#x27;, &#x27;publicDockerImageRepository&#x27;: &#x27;default-route-openshift-image-registry.apps-crc.testing/images/python&#x27;, &#x27;tags&#x27;: []}}, &#x27;...&#x27;]</div>
                </td>
            </tr>
    </table>
    <br/><br/>


Status
------


Authors
~~~~~~~

- Aubin Bikouo (@abikouo)
