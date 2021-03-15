import os
import yaml

default_file = 'configuration.yaml'
def get_dirs(file):
    #file = "configuration.yaml"
    if(file is None):
        file = default_file
    if not os.path.isfile(file):
        print("Configuration file is missing")
        return

    with open(file, "r") as yamlfile:
        cfg = yaml.safe_load(yamlfile)
        return cfg

def get_incoming_read(file=None):
    cfg = get_dirs(file)
    if cfg:
        return cfg['incoming_bods_dir']['read']
    else:
        return None


def get_incoming_processed(file=None):
    cfg = get_dirs(file)
    if cfg:
        return cfg['incoming_bods_dir']['processed']
    else:
        return None

def get_incoming_error(file=None):
    cfg = get_dirs(file)
    if cfg:
        return cfg['incoming_bods_dir']['error']
    else:
        return None

def get_outgoing_read(file=None):
    cfg = get_dirs(file)
    if cfg:
        return cfg['outgoing_bods_dir']['write']
    else:
        return None


def get_ocr(file=None):
    cfg = get_dirs(file)
    if cfg:
        return cfg['ocr_dir']['ocr']
    return None


def get_infor_processed_field_name(file=None):
    cfg = get_dirs(file)
    if cfg and cfg['infor_ocr_processed_field']:
        return cfg['infor_ocr_processed_field']
    return 'OCRProcessed'


def get_ocr_server_cred(file=None):
    cfg = get_dirs(file)
    if cfg and cfg['ocr_server_cred']:
        return cfg['ocr_server_cred']