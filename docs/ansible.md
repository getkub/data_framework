# Ansible Automation Guide

## Overview

The Data Framework includes comprehensive Ansible automation capabilities for deployment, configuration management, and operations. This guide covers how to use Ansible playbooks and roles to manage your data generation infrastructure.

## Ansible Structure

```
ansible/
├── hosts                          # Inventory file
├── group_vars/                    # Group variables
│   ├── common.yml                 # Common variables
│   ├── df.yml                     # Data Framework variables
│   └── splunk.yml                 # Splunk-specific variables
├── main_playbooks/                # Main execution playbooks
│   └── replay.yml                 # Primary data generation playbook
├── roles/                         # Reusable roles
│   ├── common/                    # Common tasks
│   └── build_data/                # Data building roles
│       ├── build_logs/            # Log building tasks
│       └── clone_core/            # Core cloning tasks
└── configs/                      # Configuration templates
    └── df_configs/                # Data Framework configurations
```

## Inventory Configuration

### Hosts File

The `ansible/hosts` file defines your target hosts:

```ini
[dev]
localhost ansible_connection=local

[production]
server1.example.com
server2.example.com

[splunk_servers]
splunk1.example.com
splunk2.example.com

[data_generators]
gen1.example.com
gen2.example.com
```

### Group Variables

#### Common Variables (`group_vars/common.yml`)

```yaml
---
# Common variables for DEV
src_base: ".."
src_base_playbook: "{{ playbook_dir }}"
project: "df"
dest_base: "/tmp/{{ ansible_user_id }}/{{ project }}"
configs: "configs"
buildDir: "buildDir"

# Ansible Directories
ansible_dir: "{{ playbook_dir }}/../../ansible"
config_dir: "{{ playbook_dir }}/../../configs"
```

#### Data Framework Variables (`group_vars/df.yml`)

```yaml
---
## Default settings
## Default output settings
df_out_dir: "df_output"
df_out_file: "default.out"
```

#### Splunk Variables (`group_vars/splunk.yml`)

```yaml
---
## Common variables
mgmtPort: 8089
httpPort: 8000
kvstorePort: 8191
fwdPort: 9997
replicationPort: 8080

protocol: "http"

# Splunk app specific
splunkadminuser: "admin"
splunkadminpass: "changedme"
```

## Main Playbooks

### Replay Playbook (`main_playbooks/replay.yml`)

The primary playbook for data generation:

```yaml
---
- name: Playbook to send data, accepts parameters
  hosts: dev
  gather_facts: no
  vars_files:
    - "{{ playbook_dir }}/../group_vars/common.yml"
    - "{{ playbook_dir }}/../group_vars/df.yml"
  roles:
    - "{{ playbook_dir }}/../roles/common"
    - "{{ playbook_dir }}/../roles/build_data/clone_core"
    - "{{ playbook_dir }}/../roles/build_data/build_logs"
```

### Running the Replay Playbook

```bash
# Basic execution
ansible-playbook -i ansible/hosts ansible/main_playbooks/replay.yml

# With specific host
ansible-playbook -i ansible/hosts ansible/main_playbooks/replay.yml --limit server1.example.com

# With extra variables
ansible-playbook -i ansible/hosts ansible/main_playbooks/replay.yml -e "count=1000 interval=5"
```

## Roles

### Common Role

The common role handles basic setup and validation tasks.

#### Structure

```
roles/common/
└── tasks/
    ├── main.yml
    └── validate_host.yml
```

#### Main Tasks (`roles/common/tasks/main.yml`)

```yaml
---
- name: Include validation tasks
  include_tasks: validate_host.yml

- name: Create base directories
  file:
    path: "{{ dest_base }}"
    state: directory
    mode: '0755'

- name: Create build directory
  file:
    path: "{{ dest_base }}/{{ buildDir }}"
    state: directory
    mode: '0755'
```

#### Host Validation (`roles/common/tasks/validate_host.yml`)

```yaml
---
- name: Check Python availability
  command: python3 --version
  register: python_version
  failed_when: python_version.rc != 0

- name: Check required directories
  stat:
    path: "{{ item }}"
  register: dir_check
  loop:
    - "{{ src_base }}"
    - "{{ config_dir }}"
  failed_when: not dir_check.stat.exists

- name: Display host information
  debug:
    msg:
      - "Host: {{ inventory_hostname }}"
      - "User: {{ ansible_user_id }}"
      - "Python: {{ python_version.stdout }}"
      - "Destination: {{ dest_base }}"
```

### Build Data Role

The build data role handles data generation and processing.

#### Clone Core Role

```
roles/build_data/clone_core/
└── tasks/
    ├── main.yml
    └── clone_rsync.yml
```

**Main Tasks (`roles/build_data/clone_core/tasks/main.yml`):**
```yaml
---
- name: Include rsync tasks
  include_tasks: clone_rsync.yml

- name: Verify core components
  stat:
    path: "{{ dest_base }}/eventgen"
  register: core_check
  failed_when: not core_check.stat.exists
```

**RSync Tasks (`roles/build_data/clone_core/tasks/clone_rsync.yml`):**
```yaml
---
- name: Clone EventGen core using rsync
  synchronize:
    src: "{{ src_base }}/eventgen"
    dest: "{{ dest_base }}/"
    recursive: yes
    delete: no
    archive: yes
  delegate_to: "{{ inventory_hostname }}"
```

#### Build Logs Role

```
roles/build_data/build_logs/
└── tasks/
    ├── main.yml
    └── build_logs_from_template.yml
```

**Main Tasks (`roles/build_data/build_logs/tasks/main.yml`):**
```yaml
---
- name: Include log building tasks
  include_tasks: build_logs_from_template.yml

- name: Start EventGen processes
  command: >
    {{ dest_base }}/eventgen/bin/eventgen.py
    {{ dest_base }}/local/{{ config_file }}
  async: 300
  poll: 0
  when: start_eventgen | default(true)
```

**Template Building (`roles/build_data/build_logs/tasks/build_logs_from_template.yml`):**
```yaml
---
- name: Create configuration from templates
  template:
    src: "{{ config_dir }}/{{ item.src }}"
    dest: "{{ dest_base }}/local/{{ item.dest }}"
    mode: '0644'
  loop:
    - { src: 'df_configs/df_default_configs.txt', dest: 'default.conf' }
    - { src: 'df_configs/df_default_outputs.txt', dest: 'outputs.conf' }
    - { src: 'df_configs/df_time_tokens.txt', dest: 'tokens.conf' }

- name: Generate combined configuration
  assemble:
    src: "{{ dest_base }}/local/"
    dest: "{{ dest_base }}/local/combined.conf"
    regexp: '.*\.conf$'
```

## Configuration Management

### Template Variables

Use Jinja2 templates in your configuration files:

```ini
# df_default_configs.txt.j2
mode = {{ df_mode | default('sample') }}
sampletype = {{ df_sampletype | default('csv') }}
backfill = {{ df_backfill | default('-15m') }}
interval = {{ df_interval | default('60') }}
earliest = {{ df_earliest | default('-60m') }}
latest = {{ df_latest | default('now') }}
end = {{ df_end | default('1') }}
```

### Environment-Specific Configurations

Create different variable files for environments:

```yaml
# group_vars/dev.yml
df_mode: sample
df_interval: 30
df_output_mode: file
df_output_file: /tmp/dev_output.log

# group_vars/prod.yml
df_mode: sample
df_interval: 5
df_output_mode: splunkstream
df_splunk_host: splunk.prod.example.com
```

## Advanced Usage

### Dynamic Inventory

Use dynamic inventory for cloud environments:

```python
#!/usr/bin/env python3
# inventory.py
import json
import boto3

def get_ec2_instances():
    ec2 = boto3.client('ec2')
    response = ec2.describe_instances(Filters=[
        {'Name': 'tag:Environment', 'Values': ['production']},
        {'Name': 'tag:Role', 'Values': ['data-generator']}
    ])
    
    inventory = {
        '_meta': {
            'hostvars': {}
        },
        'data_generators': []
    }
    
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            if instance['State']['Name'] == 'running':
                host = instance['PublicIpAddress']
                inventory['data_generators'].append(host)
                inventory['_meta']['hostvars'][host] = {
                    'ansible_user': 'ec2-user',
                    'ansible_ssh_private_key_file': '~/.ssh/aws_key.pem'
                }
    
    return inventory

if __name__ == '__main__':
    print(json.dumps(get_ec2_instances(), indent=2))
```

### Conditional Execution

Use conditions to control playbook execution:

```yaml
---
- name: Conditional data generation
  hosts: data_generators
  vars:
    generate_data: "{{ ansible_date_time.hour >= 9 and ansible_date_time.hour <= 17 }}"
  tasks:
    - name: Generate business hours data
      include_role:
        name: build_data
      when: generate_data

    - name: Generate off-hours data
      include_role:
        name: build_data
      vars:
        df_interval: 300  # Slower rate off-hours
      when: not generate_data
```

### Rolling Updates

Implement rolling updates for zero-downtime deployments:

```yaml
---
- name: Rolling update of data generators
  hosts: data_generators
  serial: 1  # Update one host at a time
  tasks:
    - name: Stop EventGen on current host
      command: pkill -f eventgen
      ignore_errors: yes

    - name: Update EventGen
      synchronize:
        src: "{{ src_base }}/eventgen"
        dest: "{{ dest_base }}/"
        delete: yes

    - name: Start EventGen
      command: >
        {{ dest_base }}/eventgen/bin/eventgen.py
        {{ dest_base }}/local/combined.conf

    - name: Wait for EventGen to be healthy
      wait_for:
        port: 9997
        delay: 10
        timeout: 60
```

## Monitoring and Logging

### Ansible Logging

Configure detailed logging:

```bash
# Set ANSIBLE_CONFIG environment variable
export ANSIBLE_CONFIG=ansible.cfg

# ansible.cfg
[defaults]
log_path = ./ansible.log
retry_files_enabled = False
host_key_checking = False
```

### Custom Callbacks

Create custom callbacks for better visibility:

```python
# callback_plugins/detailed_logging.py
from ansible.plugins.callback import CallbackBase

class CallbackModule(CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'aggregate'
    CALLBACK_NAME = 'detailed_logging'
    CALLBACK_NEEDS_WHITELIST = False

    def v2_playbook_on_stats(self, stats):
        hosts = sorted(stats.processed.keys())
        for h in hosts:
            s = stats.summarize(h)
            self._display.display(f"Host: {h}")
            self._display.display(f"  Ok: {s['ok']}")
            self._display.display(f"  Changed: {s['changed']}")
            self._display.display(f"  Unreachable: {s['unreachable']}")
            self._display.display(f"  Failed: {s['failures']}")
```

## Best Practices

### 1. Security

- Use Ansible Vault for sensitive data:
```bash
# Encrypt variables file
ansible-vault encrypt group_vars/secrets.yml

# Edit encrypted file
ansible-vault edit group_vars/secrets.yml

# Run playbook with vault password
ansible-playbook --ask-vault-pass playbook.yml
```

### 2. Idempotency

Ensure tasks are idempotent:
```yaml
- name: Ensure EventGen is running
  service:
    name: eventgen
    state: started
    enabled: yes
```

### 3. Error Handling

Implement proper error handling:
```yaml
- name: Validate configuration
  command: python3 -c "import configparser; c=configparser.ConfigParser(); c.read('{{ config_file }}')"
  register: config_validation
  failed_when: config_validation.rc != 0

- name: Display validation error
  debug:
    msg: "Configuration validation failed"
  when: config_validation.rc != 0

- name: Stop on validation failure
  fail:
    msg: "Invalid configuration file"
  when: config_validation.rc != 0
```

### 4. Performance

Optimize playbook performance:
```yaml
- name: Use pipelining
  hosts: all
  strategy: free
  vars:
    ansible_ssh_pipelining: true
```

## Troubleshooting

### Common Issues

1. **SSH Connection Issues**
```bash
# Test SSH connectivity
ansible all -i hosts -m ping

# Check SSH configuration
ansible all -i hosts -m setup | grep ansible_ssh
```

2. **Permission Issues**
```bash
# Check file permissions
ansible hosts -i hosts -m file -a "path=/tmp/eventgen mode=0755"

# Fix permissions
ansible hosts -i hosts -m file -a "path=/tmp/eventgen recurse=yes mode=0755"
```

3. **Variable Issues**
```bash
# Debug variables
ansible hosts -i hosts -m debug -a "var=hostvars[inventory_hostname]"
```

### Debug Mode

Run playbooks with increased verbosity:

```bash
# Basic debug
ansible-playbook -i hosts playbook.yml -v

# Verbose debug
ansible-playbook -i hosts playbook.yml -vvv

# Maximum verbosity
ansible-playbook -i hosts playbook.yml -vvvv
```

### Dry Run

Test playbooks without making changes:

```bash
ansible-playbook -i hosts playbook.yml --check
```

This Ansible automation guide provides comprehensive coverage of using Ansible with the Data Framework. For specific playbook examples, refer to the playbooks in the `ansible/` directory.
