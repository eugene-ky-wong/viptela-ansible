Role Name
=========

A brief description of the role goes here.

Ansible role to DevOps-ify Cisco Viptela's enrivonrment, using Cisco Viptela's software-defined networking capablities and vManage's remote management capabilities.

Requirements
------------

All modules of this role require ``python2.7`` environment::

    sudo pip install viptela-python --upgrade
    sudo pip install ansible

Installation
------------
The Ansible role can be installed directly from Ansible Galaxy by running::

     ansible-galaxy install eugene_ky_wong.viptela_ansible --force 

If the ``ansible-galaxy`` command-line tool is not available (usually shipped with Ansible), or you prefer to download the role package directly,
navigate to the Ansible Galaxy `role page <https://galaxy.ansible.com/eugene_ky_wong/viptela_ansible>`_ and hit "Download".

Alternately, you can directly navigate to our `GitHub repository <https://galaxy.ansible.com/eugene_ky_wong/viptela_ansible>`_.


Role Variables
--------------

A description of the settable variables for this role should go here, including any variables that are in defaults/main.yml, vars/main.yml, and any variables that can/should be set via parameters to the role. Any variables that are read from other roles and/or the global scope (ie. hostvars, group vars, etc.) should be mentioned here as well.

Dependencies
------------

A list of other roles hosted on Galaxy should go here, plus any details in regards to parameters that may need to be set for other roles, or variables that are used from other roles.

Example Playbook
----------------

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


License
-------

BSD

Author Information
------------------

morphyme@gmail.com
https://github.com/eugene-ky-wong/viptela-ansible


