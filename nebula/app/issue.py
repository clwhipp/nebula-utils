import click
import os
import subprocess
from ruamel.yaml import YAML

class NebulaCertificateIssuer(object):

    def __init__(self, ca_key, ca_certificate, profile_location = 'profiles.yml'):
        self._key = ca_key
        self._cert = ca_certificate
        self._password_required = False
        self._prof_location = profile_location

        self.__load_profiles()

    def __load_profiles(self):
        self._profiles = {}
        with open(self._prof_location, 'rt') as f:
            yaml = YAML()
            self._profiles = yaml.load(f)

    def issue(self, device_name, private_key_location, cert_location, qrcode_location):

        if device_name not in self._profiles:
            return False, "Failed to find profile for " + device_name
        
        device_profile = self._profiles[device_name]
        device_attributes = ','.join(device_profile['attributes'])
        device_cidr = device_profile['ip']
        device_duration = device_profile['validity'] * 8760

        # Step 1 - Need to generate key pair for the device
        temp_public_location = 'device-temp.pub'
        cmd = ['nebula-cert', 'keygen', '--out-key', private_key_location, '--out-pub', temp_public_location]
        try:
            subprocess.run(cmd, check=True)

        except subprocess.CalledProcessError as e:
            return False, str(e)

        # Step 2 - Issue Certificate for the device
        cmd = ['nebula-cert', 'sign', '-ca-crt', self._cert, '-ca-key', self._key, '-duration', str(device_duration) + 'h', '-groups', device_attributes, '-in-pub', temp_public_location, '-ip', device_cidr, '-name', device_name, '-out-crt', cert_location, '-out-qr', qrcode_location]
        try:
            subprocess.run(cmd, check=True)

        except subprocess.CalledProcessError as e:
            return False, str(e)
        
        os.remove(temp_public_location)

        return True, ""

@click.command(name='device')
@click.argument('device_name')
@click.option('--private', default=None, help='Specify location for the generated private key to be stored.')
@click.option('--cert', default=None, help='Specify location for the generated certificate for the device.')
@click.option('--qrcode', default=None, help='Specify location for storing the qrcode for the certificate.')
@click.option('--ca-key', default='ca.key', help='Location of the ca private key for handling issuance.')
@click.option('--ca-crt', default='ca.crt', help='Location of the ca certificate for handling issuance.')
@click.option('--profiles', default='profiles.yml', help='Allows for changing default location for device profiles.')
def device(device_name, private, cert, qrcode, ca_key, ca_crt, profiles):
    """
    Issue a Nebula certificate for a specific device

    Handles the process of generating a key pair and associated certificate
    for the specified device. The private key, certificate, and QR Code
    will be generated at the default location unless specified otherwise.

    @param device_name Name of the device from issuance-profiles.
    """
    print("Issuing certificate for %s" % (device_name))

    private_location = "%s.key" % (device_name)
    if private != None:
        private_location = private

    cert_location = "%s.crt" % (device_name)
    if cert != None:
        cert_location = cert

    qrc_location = "%s.png" % (device_name)
    if qrcode != None:
        qrc_location = qrcode

    issuer = NebulaCertificateIssuer(ca_key, ca_crt, profiles)
    status, msg = issuer.issue(device_name, private_location, cert_location, qrc_location)
    if status == False:
        print(msg)
        exit(1)

@click.command(name='all')
@click.option('--cert_dir', default='generated-certs', help='Specify location where the generates keys and certificates should be stored.')
@click.option('--ca-key', default='ca.key', help='Location of the ca private key for handling issuance.')
@click.option('--ca-crt', default='ca.crt', help='Location of the ca certificate for handling issuance.')
@click.option('--profiles', default='profiles.yml', help='Allows for changing default location for device profiles.')
def all(cert_dir, ca_key, ca_crt, profiles):
    """
    Issues new keys and certificates for all devices

    Handles the process of generating a key pair and associated certificate
    for all devices. The private key, certificate, and QR Code
    will be generated within the cert_dir and named based on device name.
    """

    if not os.path.exists(cert_dir):
        os.makedirs(cert_dir)

    with open('profiles.yml', 'rt') as f:
        yaml = YAML()
        profile_data = yaml.load(f)

    issuer = NebulaCertificateIssuer(ca_key, ca_crt, profiles)
    for prf in profile_data:

        print("Issuing Certificate for %s" % (prf))

        device_name = prf
        private_location = os.path.join(cert_dir, "%s.key" % (device_name))
        cert_location = os.path.join(cert_dir, "%s.crt" % (device_name))
        qrc_location = os.path.join(cert_dir, "%s.png" % (device_name))

        status, msg = issuer.issue(device_name, private_location, cert_location, qrc_location)
        if status == False:
            print('ERROR: ' + prf + " - " + msg)
            exit(1)


@click.group()
def issue():
    """
    Provides facilities for issuing Nebula VPN certificates

    The Nebula VPN utilizes certificates to enable devices to mutually
    authenticate others in the environment. The commands in this group
    enable the issuance of certificates to support establishment of
    a Nebula VPN network.
    """
    pass

issue.add_command(device)
issue.add_command(all)
