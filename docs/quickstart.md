# Quick Start Guide

## Getting Started Quickly

This guide will help you get the Data Framework up and running in minutes. Follow these steps to generate your first synthetic data.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8+** - Core runtime requirement
- **Ansible 2.4+** - For automation (optional but recommended)
- **Git** - For cloning the repository

## Step 1: Clone the Repository

```bash
git clone https://github.com/getkub/data_framework.git
cd data_framework
```

## Step 2: Basic Setup

### Option A: Quick Setup (Recommended)

```bash
# Install Python dependencies
pip3 install -r ansible/configs/ev_core/splunk_eventgen/lib/requirements.txt

# Set up basic configuration
cp ansible/configs/df_configs/df_default_configs.txt my_config.conf
```

### Option B: Ansible Setup

```bash
# Run the setup playbook
ansible-playbook -i ansible/hosts ansible/main_playbooks/replay.yml
```

## Step 3: Generate Your First Data

### Using the Command Line

```bash
# Navigate to the EventGen directory
cd ansible/configs/ev_core/splunk_eventgen

# Generate data using default configuration
python3 __main__.py generate ../df_configs/df_default_configs.txt
```

### Using the Replay Script

```bash
# Create a sample CSV file (if you don't have one)
cat > sample_data.csv << EOF
index,_raw,sourcetype,host
main,"2023-01-01 10:00:00,000 INFO Application started",application,server1
main,"2023-01-01 10:00:01,000 DEBUG Processing request",application,server1
main,"2023-01-01 10:00:02,000 INFO Request completed",application,server1
EOF

# Run the replay script
cd ../../../../scripts
./replayData.sh sample_data.csv sample
```

## Step 4: Verify Output

### Check Generated Data

```bash
# If using file output
ls -la /tmp/eventgen.test.log
cat /tmp/eventgen.test.log

# If using Splunk output, check your Splunk instance
# Navigate to your Splunk instance and search for the data
```

## Step 5: Customize Configuration

### Edit Configuration

Edit your configuration file (`my_config.conf`):

```ini
# Basic configuration
[sample_data]
mode = sample
sampletype = csv
backfill = -15m
interval = 60
earliest = -5m
latest = now
end = 10

# Output configuration
outputMode = file
fileName = /tmp/my_generated_data.log

# Token configuration for timestamp replacement
token.0.token = \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}
token.0.replacementType = timestamp
token.0.replacement = %Y-%m-%d %H:%M:%S,%f
```

### Run with Custom Configuration

```bash
cd ansible/configs/ev_core/splunk_eventgen
python3 __main__.py generate my_config.conf
```

## Common Use Cases

### 1. Generate Web Server Logs

```bash
# Use built-in web log sample
cd ansible/configs/ev_core/splunk_eventgen
python3 __main__.py generate -s sample.weblog
```

### 2. Replay Existing Data

```bash
# With your sanitized CSV file
./scripts/replayData.sh your_data.csv replay
```

### 3. Generate High-Volume Data

```bash
# Generate 1000 events quickly
python3 __main__.py generate -c 1000 -i 1 your_config.conf
```

## Configuration Templates

### Basic File Output

```ini
[your_sample]
mode = sample
sampletype = csv
outputMode = file
fileName = /tmp/your_output.log
interval = 60
end = 100
```

### Splunk Output

```ini
[your_sample]
mode = sample
sampletype = csv
outputMode = splunkstream
splunkHost = your-splunk-host
splunkPort = 8089
splunkUser = admin
splunkPass = your-password
interval = 60
end = 100
```

### HTTP Output

```ini
[your_sample]
mode = sample
sampletype = csv
outputMode = httpevent
http_url = http://your-endpoint.com/events
http_method = POST
interval = 60
end = 100
```

## Troubleshooting Common Issues

### Issue: "Module not found" errors

**Solution:**
```bash
# Install missing dependencies
pip3 install -r ansible/configs/ev_core/splunk_eventgen/lib/requirements.txt

# Or install specific packages
pip3 install jinja2 requests redis
```

### Issue: Permission denied

**Solution:**
```bash
# Check file permissions
ls -la your_config.conf
chmod 644 your_config.conf

# Check output directory permissions
ls -la /tmp/
chmod 755 /tmp/
```

### Issue: No data generated

**Solution:**
```bash
# Check configuration syntax
python3 __main__.py generate --verbosity 2 your_config.conf

# Verify sample file exists
ls -la your_sample_file.csv
```

### Issue: Splunk connection failed

**Solution:**
```bash
# Test Splunk connectivity
curl -k -u admin:changedme https://your-splunk-host:8089/services/auth/login

# Check Splunk configuration
# Verify HEC is enabled and credentials are correct
```

## Next Steps

Once you have the basic setup working:

1. **Explore Templates**: Look at the sample data in `ansible/configs/ev_core/splunk_eventgen/samples/`
2. **Customize Tokens**: Modify timestamp patterns in `df_time_tokens.txt`
3. **Try Different Outputs**: Experiment with various output plugins
4. **Scale Up**: Use Ansible playbooks for larger deployments
5. **Monitor**: Set up monitoring and alerting

## Getting Help

- **Documentation**: Check the full documentation in the `docs/` directory
- **Configuration Reference**: See `config-reference.md` for all options
- **Troubleshooting**: Refer to `troubleshooting.md` for detailed help
- **Examples**: Look at the `README/` directory for example configurations

## Quick Reference

### Essential Commands

```bash
# Generate data
python3 __main__.py generate config_file.conf

# Generate with specific count
python3 __main__.py generate -c 100 config_file.conf

# Generate with verbosity
python3 __main__.py generate -v config_file.conf

# Run replay script
./scripts/replayData.sh data.csv format

# Run Ansible playbook
ansible-playbook -i hosts playbook.yml
```

### Key Files

- `ansible/configs/df_configs/df_default_configs.txt` - Default configuration
- `ansible/configs/df_configs/df_time_tokens.txt` - Timestamp patterns
- `scripts/replayData.sh` - Data replay script
- `ansible/main_playbooks/replay.yml` - Main Ansible playbook

### Common Directories

- `ansible/configs/ev_core/splunk_eventgen/samples/` - Sample data files
- `ansible/configs/df_configs/` - Configuration templates
- `scripts/` - Utility scripts
- `docs/` - Documentation

You're now ready to use the Data Framework! For more advanced usage, refer to the detailed documentation.
