#!/usr/bin/python
import traceback
import pdb

from ansible.module_utils.basic import AnsibleModule

try:
    from viptela_python.viptela import Viptela
    HAS_LIB=True

except ImportError:
    HAS_LIB=False


ANSIBLE_METADATA = {
    'metadata_version': '0.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: viptela_command

short_description: This does various actions pertaining to Viptela's REST API

version_added: "0.0.2"

description:
    - "This module allows various commands to invoke commands in vManage, including staging software in vEdge, vManage as well as upgrading of routers"

options:
    version_name:
        description:
            - This is the Software version number to add.
        required: true
    URL:
        description:
            - URL of software upgrade, eg. software_install-e8dd4424-c618-4216-8741-9a850c6950e6
        required: true only for checking upgrade status
    user:
    	description:
    	    - Username of manamgement account, eg. admin
    	required: true
    user_pass:
    	description:
    	    - Password of management account, eg. pass
    	required: true
    filename:
    	description:
    	    - filename of firmware for upload
    	required: false
    vmanage_server:
    	description:
    	    - IP / FQDN of vManage server, eg. 10.1.1.41
    	required: true
    device_type:
        description:
            - device type for device query, eg. vedges
        required: false
    device_uuid:
        description:
            - UUID of device for upgrade
        required: true for upgrade, activate, get running config
    ip_address:
        description:
            - IP / FQDN of vEdge device to be upgraded
        required: false
    verify:
        description:
            - SSL Verify - False as default
        required: false
    text:
        description:
            - banner text for setting banner
        requied: false
    device_id:
        description:
            - IP of device to be upgraded 
            - IP of device to be queried
        required: true for actions i
            'upgrade, activate,
             get_arp_table, get_bgp_summary, get_bgp_routes, get_bgp_neighbours,
             get_ospf_routes, get_ospf_neighbours, get_ospf_database,
             get_transport_connection, get tunnel_statistics, get_omp_peers,
             get_cellular_network, get_cellular_profiles, get_cellular_radio,
             get_cellular_status, get_ipsec_inbound, get_ipsec_outbound,
             get_ipsec_localsa'

    template_id:
        description:
            - Template ID
        required: optional for action 'get_template_feature'

extends_documentation_fragment:
    - nil

author:
    - Eugene KY Wong (@eugenekywong)
'''

EXAMPLES = '''
  # Upload software to vManage
  - name: Test with a message
    viptela_command:
      name: Stage 18.2.0
      filename: "viptela-18.2.0-mips64.tar.gz"
      user: admin
      user_pass: pass
      vmanage_server: 10.1.1.41
    register: results

  # Upload software to vEdge
  - name: Upgrade_Software
    viptela_command:
      user: admin
      user_pass: pass
      vmanage_server: "{{ vmanage_server }}"
      version: "{{ version }}"
      URL: 'vmanage'
      #device_type: 'vedges'
      action: 'upgrade'
      ip_address: "{{ ip_address }}"
      device_uuid: "{{ device_uuid[0] }}"
    register: upgrade

  # Upgrade software in vEdge
  - name: Change_Partition
    viptela_command:
      user: admin
      user_pass: pass
      vmanage_server: "{{ vmanage_server }}"
      version: "{{ version }}"
      action: 'activate'
      ip_address: "{{ ip_address }}"
      device_uuid: "{{ device_uuid[0] }}"
    register: change_partition

  # Check Upgrade status
  - name: Check_Upgrade_Status
    viptela_command:
      user: admin
      user_pass: pass
      vmanage_server: "{{ vmanage_server }}"
      URL: "{{ change_partition.results }}"
      action: 'check_status'
    register: check_status
    retries: "{{ timeout * 6 }}"
    delay: 10
    until: ( check_status.results[0].statusId=="success" ) or
           ( check_status.results[0].statusId=="skipped" )
'''

RETURN = '''
original_message:
    description: The original name param that was passed in
    type: str
message:
    description: The output message that the sample module generates
'''

DEVICE_ID_MODULES = {
             'get_arp_table', 'get_bgp_summary', 'get_bgp_routes', 'get_bgp_neighbours',
             'get_ospf_routes', 'get_ospf_neighbours', 'get_ospf_database',
             'get_transport_connection', 'get tunnel_statistics', 'get_omp_peers',
             'get_cellular_network', 'get_cellular_profiles', 'get_cellular_radio',
             'get_cellular_status', 'get_ipsec_inbound', 'get_ipsec_outbound',
             'get_ipsec_localsa'
}

DEVICE_UUID_MODULES = {
             'get_running_config'
}

from ansible.module_utils.basic import AnsibleModule

def run_module():
    # define the available arguments/parameters that a user can pass to
    # the module
    module_args = dict(
        version=dict(type='str', required=False),
        URL=dict(type='str', required=False),
        user=dict(type='str', required=True),
        user_pass=dict(type='str', required=True, no_log=True),
        filename=dict(type='str', required=False),
        vmanage_server=dict(type='str', required=True),
        action=dict(type='str', required=True),
        device_type=dict(type='str', required=False),
        device_uuid=dict(type='str', required=False),
        ip_address=dict(type='str', required=False),
        verify=dict(type='bool', required=False, default=False)
    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # change is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
        #original_message='',
        #message=''
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    if not HAS_LIB:
        module.fail_json(msg="Viptela package is required for this module.")

    vManage_init_args = {'user': module.params['user'],
        'user_pass': module.params['user_pass'],
        'vmanage_server': module.params['vmanage_server'],
        'verify': module.params['verify'],
        'disable_warnings': 'True'}

    vManage_upgrade_args = {'ip_address': module.params['ip_address'],
        'version': module.params['version'],
        'device_uuid': module.params['device_uuid']}

    if module.params['action'] in DEVICE_ID_MODULES:
        vManage_args = {'device_id': module.params['ip_address']}
    elif module.params['action'] in DEVICE_UUID_MODULES:
        vManage_args = {'device_uuid': module.params['device_uuid']}
    else:
        vManage_args = {'device_type': module.params['device_type'],
            'device_uuid': module.params['device_uuid']}

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        return result

    # manipulate or modify the state as needed (this is going to be the
    # part where your module will do what it needs to do)
    #pdb.set_trace()

    method_name= module.params['action']
    method = None

    vsession = Viptela(**vManage_init_args)

    if (method_name == "upgrade" or method_name =="activate"):

        #result['changed']=True
        if (method_name == "upgrade"):
            response = vsession.upgrade(**vManage_upgrade_args)
        elif (method_name == "activate"):
            (response) = vsession.activate(**vManage_upgrade_args)
        result['status_code'] = response.status_code
        result['results'] = response.data

    elif (method_name == "check_status" or method_name == "set_banner"
        or method_name == "firmware_upload"):

        result['changed']=True
        if (method_name == "check_status"):
            response = vsession.check_status(module.params['URL'])
        elif (method_name == "set_banner"):
            response = vsession.set_banner(module.params['URL'])
        elif (method_name == "firmware_upload"):
            response = vsession.firmware_upload(module.params['filename'])
        result['status_code'] = response.status_code
        result['results'] = response.data

    elif (module.params['action'] in DEVICE_ID_MODULES or 
      module.params['action'] in DEVICE_UUID_MODULES):
        try:
            method = getattr(vsession, method_name)
        except AttributeError:
            raise NotImplementedError("Class `{}` does not implement `{}`"
                .format(vsession.__class__.__name__, method_name))

        response=method(**vManage_args)

        result['results'] = response.data
        result['status_code'] = response.status_code

    else:
        try:
            method = getattr(vsession, method_name)
        except AttributeError:
            raise NotImplementedError("Class `{}` does not implement `{}`"
                .format(vsession.__class__.__name__, method_name))
        method()

        result['status_code'] = method().status_code
        result['results'] = method().data

    # use whatever logic you need to determine whether or not this module
    # made any modifications to your target
    # if module.params['new']:
    #     result['changed'] = True

    # during the execution of the module, if there is an exception or a
    # conditional state that effectively causes a failure, run
    # AnsibleModule.fail_json() to pass in the message and the result
    if module.params['version'] == 'fail me':
        module.fail_json(msg='You requested this to fail', **result)

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()

