import os
from ConfigParser import SafeConfigParser
from cStringIO import StringIO


INSECURE = bool(os.environ.get('INSECURE', False))
if INSECURE:
    import warnings
    warnings.warn("**INSECURE ENVIRONMENT**")
    
INVENTORY = 'inventory'
ANSIBLE_CONFIG_FILE = "ansible.cfg"
DEMOSTHENES_CONFIG = '.demosthenes.cfg'
MAIN_SITE_PLAYBOOK = os.path.join('playbooks', 'site.yml')

ANSIBLE_INVENTORY_PATHS = [
    os.path.join('ansible', INVENTORY),
    INVENTORY,
]


CONFIG_DEFAULTS = """\
[paths]
data-home: $XDG_DATA_HOME/demosthenes

# Default installation directory
install-path: %(data-home)s/debops-playbooks

# Locations where Demosthenes playbooks may be found
playbooks-paths: %(install-path)s/playbooks

[ansible defaults]
ansible_managed = This file managed by ansible.  Do no edit!
"""

def set_xdg_defaults():
    for name, path in [
        ('XDG_CONFIG_HOME', '~/.config'),
        ('XDG_CONFIG_DIRS', '/etc/xdg'),
            ('XDG_DATA_HOME', '~/.local/share'),
    ]:
        if name not in os.environ:
            os.environ[name] = path

def find_in_parent(path, name):
    abspath = os.path.abspath(path)
    last = None
    while abspath != last:
        last = abspath
        abspath = os.path.join(abspath, name)
        if os.path.exists(abspath):
            return abspath
        abspath = os.path.dirname(last)
    return None

def find_demosthenes_project(path=None, required=None):
    if path is None:
        path = os.getcwd()
    demos_config = find_in_parent(path, DEMOSTHENES_CONFIG)
    proot = os.path.dirname(demos_config) if demos_config else None
    if required is None:
        return proot
    if required and not proot:
        raise RuntimeError, "unable to find project directory"
    return proot

def find_playbook_path(config, project_root, required=None):
    places = list()
    pb_dirname = config.get('repos', {}).get('playbooks_dirname',
                                             'debops-playbooks')
    if project_root:
        places = [os.path.join(project_root, pb_dirname, 'playbooks')]
    places.extend(config['paths']['playbooks-paths'])
    found_path = None
    for playbook_path in places:
        if os.path.isfile(os.path.join(playbook_path, 'site.yml')):
            found_path = playbook_path
            break
    if required is None:
        return found_path
    if required and found_path is None:
        raise RuntimeError, "unable to find playbook path"
    return found_path

def find_inventory_path(project_root, required=None):
    found_path = None
    for inventory_path in ANSIBLE_INVENTORY_PATHS:
        adirectory = os.path.join(project_root, inventory_path)
        if os.path.isdir(adirectory):
            found_path = adirectory
            break
    if required is None:
        return found_path
    if required and found_path is None:
        raise RuntimeError, "unable to find inventory for ansible"
    return found_path


def get_config_filenames():
    set_xdg_defaults()
    config_paths = [os.environ['XDG_CONFIG_HOME']]
    config_paths += os.environ['XDG_CONFIG_DIRS'].split(':')
    config_paths += ['/etc']
    config_paths = [os.path.expanduser(p) for p in config_paths]
    # FIXME should XDG_CONFIG_DIRS be reversed?
    # or should we start with /etc and end with XDG_CONFIG_HOME?
    config_paths.reverse()
    return [os.path.join(p, 'demosthenes.cfg') for p in config_paths]

def expand_user_and_vars(path):
    return os.path.expanduser(os.path.expandvars(path.strip()))

def read_config(project_root):
    configfiles = get_config_filenames()
    if project_root is not None:
        configfiles += [os.path.join(project_root, DEMOSTHENES_CONFIG)]
    cfgparser = SafeConfigParser()
    cfgparser.readfp(StringIO(CONFIG_DEFAULTS))
    cfgparser.read(configfiles)
    cfg = dict((section, dict(cfgparser.items(section)))
                for section in cfgparser.sections())
    for option in ['data-home', 'install-path']:
        cfg['paths'][option] = expand_user_and_vars(cfg['paths'][option])
    cfg['paths']['playbooks-paths'] = [
        expand_user_and_vars(p)
        for p in cfg['paths']['playbooks-paths'].splitlines()
        if p.strip()]
    return cfg

                                        
        
    
