# Troubleshooting Guide

## Overview

This guide covers common issues, error scenarios, and troubleshooting steps for the Data Framework. It's organized by component and includes diagnostic commands, common error messages, and solutions.

## General Troubleshooting

### System Requirements Check

Before diving into specific issues, verify your system meets requirements:

```bash
# Check Python version
python3 --version
# Should be 3.8 or higher

# Check Ansible version
ansible --version
# Should be 2.4 or higher

# Check available disk space
df -h

# Check memory usage
free -h

# Check network connectivity
ping -c 3 google.com
```

### Log Locations

The framework generates logs in various locations:

```bash
# EventGen logs
/tmp/eventgen/logs/
/var/log/eventgen/

# Ansible logs
./ansible.log
~/.ansible/log/

# System logs
/var/log/syslog
/var/log/messages

# Script logs
/var/log/data_framework.log
```

### Enable Debug Mode

For detailed troubleshooting, enable debug logging:

```bash
# EventGen debug mode
cd ansible/configs/ev_core/splunk_eventgen
python3 __main__.py generate --verbosity 2 your_config.conf

# Ansible debug mode
ansible-playbook -i hosts playbook.yml -vvvv

# Script debug mode
export DEBUG=1
./script_name.sh --debug
```

## EventGen Issues

### Common Error Messages

#### 1. "Module not found" Errors

**Error**: `ModuleNotFoundError: No module named 'splunk_eventgen'`

**Causes**:
- Missing Python dependencies
- Incorrect Python path
- Virtual environment not activated

**Solutions**:
```bash
# Install dependencies
pip3 install -r ansible/configs/ev_core/splunk_eventgen/lib/requirements.txt

# Check Python path
python3 -c "import sys; print(sys.path)"

# Install specific missing modules
pip3 install jinja2 requests redis

# If using virtual environment
source /path/to/venv/bin/activate
pip install -r requirements.txt
```

#### 2. "Configuration file not found"

**Error**: `FileNotFoundError: [Errno 2] No such file or directory: 'config.conf'`

**Causes**:
- Incorrect file path
- Missing configuration file
- Permission issues

**Solutions**:
```bash
# Check file existence
ls -la your_config.conf

# Use absolute path
python3 __main__.py generate /full/path/to/config.conf

# Check permissions
chmod 644 your_config.conf

# Validate configuration syntax
python3 -c "
import configparser
config = configparser.ConfigParser()
config.read('your_config.conf')
print('Configuration is valid')
"
```

#### 3. "Sample file not found"

**Error**: `Sample file not found: sample.csv`

**Causes**:
- Sample file missing
- Incorrect path in configuration
- File permissions

**Solutions**:
```bash
# Check sample file
ls -la ansible/configs/ev_core/splunk_eventgen/samples/

# Copy sample file to correct location
cp your_sample.csv ansible/configs/ev_core/splunk_eventgen/samples/

# Update configuration with correct path
sample = /full/path/to/sample.csv
```

#### 4. "Connection refused" Errors

**Error**: `Connection refused: [Errno 111] Connection refused`

**Causes**:
- Splunk server not running
- Incorrect port configuration
- Firewall blocking connection

**Solutions**:
```bash
# Test Splunk connectivity
curl -k -u admin:changedme https://your-splunk-host:8089/services/auth/login

# Check Splunk service status
sudo systemctl status splunk

# Verify port is open
telnet your-splunk-host 8089

# Check firewall rules
sudo ufw status
sudo iptables -L
```

### Performance Issues

#### Slow Data Generation

**Symptoms**:
- Low event generation rate
- High CPU usage
- Memory leaks

**Diagnostics**:
```bash
# Monitor CPU usage
top -p $(pgrep -f eventgen)

# Monitor memory usage
ps aux | grep eventgen

# Check disk I/O
iotop -o

# Profile EventGen
python3 __main__.py generate --profiler your_config.conf
```

**Solutions**:
```bash
# Adjust worker counts
generatorWorkers = 4
outputWorkers = 2

# Use threading instead of multiprocessing
multithread = true

# Optimize queue sizes
generatorQueueSize = 1000

# Reduce complexity of tokens
# Simplify regular expressions
# Use file-based tokens instead of complex patterns
```

#### Memory Issues

**Symptoms**:
- Out of memory errors
- System swapping
- Process crashes

**Diagnostics**:
```bash
# Check memory usage
free -h
ps aux --sort=-%mem | head

# Monitor memory over time
watch -n 1 'free -h'

# Check for memory leaks
valgrind --tool=memcheck python3 __main__.py generate your_config.conf
```

**Solutions**:
```bash
# Reduce batch sizes
count = 1000  # Instead of unlimited

# Use file output instead of memory-intensive operations
outputMode = file

# Implement periodic cleanup
end = 100  # Process in smaller chunks
```

## Ansible Issues

### Common Error Messages

#### 1. SSH Connection Issues

**Error**: `SSH Error: Permission denied (publickey,password)`

**Causes**:
- SSH key authentication issues
- Incorrect user credentials
- SSH service not running

**Solutions**:
```bash
# Test SSH connectivity
ansible all -i hosts -m ping

# Check SSH configuration
ansible all -i hosts -m setup | grep ansible_ssh

# Setup SSH keys
ssh-keygen -t rsa -b 4096
ssh-copy-id user@hostname

# Test with specific user
ansible-playbook -i hosts playbook.yml -u username --ask-pass
```

#### 2. "Host not found" Errors

**Error**: `ERROR! Invalid data passed to 'host', required`

**Causes**:
- Host not in inventory
- Incorrect inventory file path
- DNS resolution issues

**Solutions**:
```bash
# Check inventory file
cat ansible/hosts

# Test host resolution
nslookup hostname
dig hostname

# Use IP address instead of hostname
# In hosts file:
# server1 ansible_host=192.168.1.100
```

#### 3. "Module not found" in Ansible

**Error**: `MODULE FAILURE`

**Causes**:
- Missing Ansible modules
- Python path issues on target
- Missing Python packages

**Solutions**:
```bash
# Check Python on target
ansible hosts -i hosts -m command -a "python3 --version"

# Install required packages
ansible hosts -i hosts -m pip -a "name=requests state=present"

# Check Ansible module path
ansible hosts -i hosts -m setup | grep ansible_python
```

### Playbook Issues

#### Task Failures

**Diagnostics**:
```bash
# Run with verbose output
ansible-playbook -i hosts playbook.yml -vvv

# Run in check mode
ansible-playbook -i hosts playbook.yml --check

# Run specific task
ansible-playbook -i hosts playbook.yml --start-at-task="task name"
```

**Common Solutions**:
```bash
# Ignore errors for non-critical tasks
- name: Optional task
  command: some_command
  ignore_errors: yes

# Use conditional execution
- name: Conditional task
  command: some_command
  when: condition_is_true

# Retry failed tasks
- name: Retry task
  command: unreliable_command
  retries: 3
  delay: 5
```

## Script Issues

### Shell Script Problems

#### Permission Denied

**Error**: `bash: ./script.sh: Permission denied`

**Solutions**:
```bash
# Make script executable
chmod +x script_name.sh

# Check script permissions
ls -la script_name.sh

# Run with bash explicitly
bash script_name.sh
```

#### Variable Issues

**Error**: Variable not found or incorrect values

**Diagnostics**:
```bash
# Debug variables
set -x  # Enable debug mode
echo "Variable value: $VAR_NAME"

# Check environment variables
env | grep VAR_NAME
```

**Solutions**:
```bash
# Set default values
VAR_NAME="${VAR_NAME:-default_value}"

# Validate variables
if [[ -z "$VAR_NAME" ]]; then
    echo "ERROR: VAR_NAME is not set"
    exit 1
fi

# Use absolute paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
```

### Python Script Issues

#### Import Errors

**Error**: `ImportError: No module named 'module_name'`

**Solutions**:
```bash
# Install missing modules
pip3 install module_name

# Check Python path
python3 -c "import sys; print(sys.path)"

# Use virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Runtime Errors

**Diagnostics**:
```bash
# Run with debug output
python3 -v script_name.py

# Use Python debugger
python3 -m pdb script_name.py

# Check syntax
python3 -m py_compile script_name.py
```

## Network Issues

### Connectivity Problems

#### DNS Resolution

**Diagnostics**:
```bash
# Test DNS resolution
nslookup hostname
dig hostname
host hostname

# Check /etc/resolv.conf
cat /etc/resolv.conf

# Test with different DNS servers
nslookup hostname 8.8.8.8
```

#### Port Connectivity

**Diagnostics**:
```bash
# Test port connectivity
telnet hostname port
nc -zv hostname port

# Check listening ports
netstat -tlnp
ss -tlnp

# Test with curl
curl -v http://hostname:port
```

### Firewall Issues

**Diagnostics**:
```bash
# Check firewall status
sudo ufw status
sudo iptables -L -n

# Check specific port
sudo ufw status numbered
sudo iptables -L -n | grep 8089
```

**Solutions**:
```bash
# Allow port in UFW
sudo ufw allow 8089/tcp

# Add iptables rule
sudo iptables -A INPUT -p tcp --dport 8089 -j ACCEPT

# Save iptables rules
sudo iptables-save > /etc/iptables/rules.v4
```

## Data Issues

### CSV Format Problems

#### Invalid CSV Format

**Error**: CSV parsing errors or missing headers

**Diagnostics**:
```bash
# Check CSV format
head -5 your_file.csv

# Validate headers
head -1 your_file.csv | grep -E "(index|_raw|sourcetype)"

# Check for special characters
cat your_file.csv | od -c
```

**Solutions**:
```bash
# Fix CSV format
# Ensure first row has headers: index,_raw,sourcetype,host

# Remove special characters
sed 's/[[:cntrl:]]//g' your_file.csv > cleaned_file.csv

# Validate with Python
python3 -c "
import csv
with open('your_file.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(row)
"
```

### Timestamp Issues

#### Invalid Timestamp Formats

**Diagnostics**:
```bash
# Check timestamp patterns
grep -E "\d{4}-\d{2}-\d{2}" your_file.csv

# Test timestamp parsing
python3 -c "
import datetime
dt = datetime.datetime.strptime('2023-01-01 10:00:00', '%Y-%m-%d %H:%M:%S')
print(dt)
"
```

**Solutions**:
```bash
# Update token configuration
token.0.token = \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}
token.0.replacement = %Y-%m-%d %H:%M:%S

# Test different formats
# %Y-%m-%d %H:%M:%S,%f for milliseconds
# %d/%b/%Y:%H:%M:%S for Apache logs
# %Y-%m-%dT%H:%M:%SZ for ISO format
```

## Performance Monitoring

### System Monitoring

```bash
# Monitor CPU usage
top -p $(pgrep -f eventgen)
htop

# Monitor memory usage
free -h
watch -n 1 'free -h'

# Monitor disk I/O
iotop -o
iostat -x 1

# Monitor network
iftop
nethogs
```

### Application Monitoring

```bash
# Monitor EventGen processes
ps aux | grep eventgen
watch -n 1 'ps aux | grep eventgen'

# Check log files in real-time
tail -f /tmp/eventgen/logs/eventgen.log

# Monitor output generation
watch -n 1 'wc -l /tmp/eventgen.test.log'
```

## Recovery Procedures

### Data Recovery

```bash
# Check for partial output files
ls -la /tmp/eventgen*.log

# Recover from backup
cp /backup/eventgen.test.log /tmp/eventgen.test.log

# Restart from last known good state
python3 __main__.py generate --backfill=-1h your_config.conf
```

### Service Recovery

```bash
# Restart EventGen
pkill -f eventgen
python3 __main__.py generate your_config.conf

# Restart Splunk (if needed)
sudo systemctl restart splunk

# Clear stuck processes
pkill -9 -f eventgen
```

## Getting Help

### Log Collection

When seeking help, collect relevant information:

```bash
# System information
uname -a
python3 --version
ansible --version

# Configuration files
cat your_config.conf
cat ansible/hosts

# Log files
tail -100 /tmp/eventgen/logs/eventgen.log
tail -100 ansible.log

# Error output
python3 __main__.py generate your_config.conf 2>&1 | tee error.log
```

### Debug Commands

```bash
# Full EventGen debug
python3 __main__.py generate --verbosity 2 --profiler your_config.conf

# Ansible debug with timing
ansible-playbook -i hosts playbook.yml -vvv --timing

# Network debug
tcpdump -i any port 8089 -w capture.pcap
```

### Support Channels

1. **Documentation**: Check relevant documentation sections
2. **Logs**: Review error logs for specific error messages
3. **Community**: Post questions with relevant logs and configuration
4. **Issues**: Create detailed bug reports with reproduction steps

This troubleshooting guide covers the most common issues. For specific problems not covered here, refer to the relevant component documentation or seek community support.
