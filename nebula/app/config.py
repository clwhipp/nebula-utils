import click
import os
import yaml

def load_yaml_file(location):
        
    data = {}
    if not os.path.exists(location):
        print("%s not found" % (location))
        return data

    with open(location, 'rt') as f:
        data = yaml.safe_load(f)

    return data

def retrieve_hosts_in_group(device_profiles, group):
    hostnames = []
    for device_name in device_profiles:
        profile = device_profiles[device_name]
        if group in profile['acl_groups']:
            hostnames.append(device_name)

    return hostnames

@click.command(name='expand')
@click.option('--profiles', default='profiles.yml', help='Specifies location for the file that contains the profiles.')
@click.argument('source')
@click.argument('destination')
def expand(profiles, source, destination):
    """
    Allows for expanding an acl_group within nebula configuration

    This utility allows for creating an acl_group within a nebula configuration. The
    devices within the profiles.yml with access to this acl_group will be replaced
    with a device specific whitelist configuration.
    """
    print("Expanding %s" % (source))

    device_profiles = load_yaml_file(profiles)

    template = load_yaml_file(source)
    rules = template['firewall']['inbound']

    config = template
    config['firewall']['inbound'] = []

    for rule in rules:

        if 'acl_group' in rule:
            group_name = rule['acl_group']
            hosts = retrieve_hosts_in_group(device_profiles, group_name)
            for host in hosts:
                entry = {}
                entry['port'] = rule['port']
                entry['proto'] = rule['proto']
                entry['host'] = host
                config['firewall']['inbound'].append(entry)
        else:
            config['firewall']['inbound'].append(rule)

    # Write back to the YAML file
    with open(destination, 'w') as file:
        yaml.dump(config, file, default_flow_style=False)


@click.group()
def firewall():
    """
    Provides facilities for managing firewall section of nebula configuration

    The Nebula configuration includes a firewall section. This firewall section
    allows for defining ports that devices are allowed to access.
    """
    pass

firewall.add_command(expand)
