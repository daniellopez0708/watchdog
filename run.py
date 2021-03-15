import base64
import json
import os
import shutil
import ssl
import tempfile
import time
import urllib
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from sys import path
from types import SimpleNamespace
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement

import requests

import util
from djxml import XmlDictConfig

bod_xmlns = '{http://infor.com/daf}'

server_url = 'https://dev.cloudintegration.eu/'

temp_download_dir = 'temp_downloads'




def process_xml_bods():
    read_dir = util.get_incoming_read()
    for file in Path(read_dir).iterdir():
        if file.suffix != '.xml':
            continue
        process_xml_bod_file(file)


def process_xml_bod_file(file):
    if not file.endswith('.xml'):
        return

    pid, url = get_document_info(file) # getting pid, and url from bod

    filename = pid + ".pdf"
    filename_xml = pid +".xml"

    filepath = download_pdf_from_idm(url,filename) # downloading pdf file
    print('filepath: ' + filepath)
    task_id = upload_file_to_ocr(filename, filepath) # uploading pdf to ocr server
    print('task id: ' + task_id)
    
    try:
        starttime = time.time()
        while True:
            status = get_task_status(task_id)
            print(status)
            if status == "completed":
                break
            time.sleep(10.0 - ((time.time() - starttime) % 10.0))
    except requests.ConnectionError:
        print("failed to connect")



    decoded_string = get_file_from_ocr(filename, task_id) # donloading ocr 
    print('file decoded')

    create_xml_bod(pid, filename, decoded_string, filename_xml)
    print('bod created')



def get_document_info(file):
    tree = ET.parse(str(file))
    root = tree.getroot()
    xmldict = XmlDictConfig(root)

    url = xmldict.get('DataArea').get('IDM_Doc').get(f'{bod_xmlns}item').get(f'{bod_xmlns}resrs').get(f'{bod_xmlns}res')[0].get(f'{bod_xmlns}url')
    pid = xmldict.get('DataArea').get('IDM_Doc').get(f'{bod_xmlns}item').get(f'{bod_xmlns}pid')

    return pid, url


def download_pdf_from_idm(url, filename):
    print('url')
    print(url)
    r = requests.get(url ,verify=False)    
    #tf = tempfile.NamedTemporaryFile(suffix='.pdf')
    
    destination = os.path.join(temp_download_dir , filename)

    ssl._create_default_https_context = ssl._create_unverified_context
    urllib.request.urlretrieve(url, destination )

    

    """
    with open(destination, mode='wb') as f:
        f.write(r.content)
        f.seek(0)
    """
    return destination


def upload_file_to_ocr(filename, filepath):
    payload={'Jpg_quality': '3',
            'optimize': '3',
            'pdfa': 'true',
            'OCR_Lang': 'deu',
            'deskew': 'true',
            'clean': 'true',
            'final': 'true',
            'background': 'true',
            'rotate': 'true',
            'force': 'true'
            }
    files=[
        ('file',(filename, open(filepath,'rb'),'application/pdf'))
    ]
    
    ocr_url, ocr_username, ocr_password = get_ocr_cred()
    cred_str = str.encode(f'{ocr_username}:{ocr_password}')
    userAndPass = base64.b64encode(cred_str).decode("ascii")
    headers = { 'Authorization' : 'Basic %s' %  userAndPass }

    if(not ocr_url[-1] == '/'):
        ocr_url= ocr_url + '/'

    r = requests.post(ocr_url+ 'api/ocrserver/uploads/', headers=headers, files=files, data=payload)

    data = json.loads(r.text)
    task_id = data['task_id']
    return task_id




def get_task_status(task_id):
    ocr_url, ocr_username, ocr_password = get_ocr_cred()
    cred_str = str.encode(f'{ocr_username}:{ocr_password}')
    userAndPass = base64.b64encode(cred_str).decode("ascii")
    headers = { 'Authorization' : 'Basic %s' %  userAndPass }

    r = requests.get(ocr_url+'api/ocrserver/status/'+task_id, headers=headers)

    status = json.loads(r.text)
    state_id = status['state']
    return state_id


def get_ocr_cred():
    ocr_cred = util.get_ocr_server_cred()
    ocr_url = ocr_cred['url']
    ocr_username = ocr_cred['username']
    ocr_password = ocr_cred['password']
    if(not ocr_url[-1] == '/'):
        ocr_url= ocr_url + '/'
    return ocr_url, ocr_username, ocr_password


def get_file_from_ocr(filename, task_id):
    #r = requests.get('https://dev.cloudintegration.eu/api/ocrserver/download/'+task_id)
    r = requests.get(server_url+'api/ocrserver/download/'+task_id)
    ocr_dir = util.get_ocr()
    with open(os.path.join(ocr_dir, filename), "wb") as f:
        f.write(r.content)
        #print("OCR was saved")

    file_path = os.path.join(ocr_dir, filename)

    with open(file_path, "rb") as pdf_file:
        encoded_string = base64.b64encode(pdf_file.read())
        #print(encoded_string)
        decoded_string = encoded_string.decode('UTF-8')
        #print(encoded_string)
    return decoded_string


def create_xml_bod(pid, filename, decoded_string, filename_xml):
    write_dir = util.get_outgoing_read()
    print(write_dir)

    top = Element('OCRProcessed_Doc')

    child = SubElement(top, 'pid')
    child.text = pid

    child_name = SubElement(top, 'filename')
    child_name.text = filename

    child_base = SubElement(top, 'base64')
    child_base.text = str(decoded_string)

    mydata = ET.tostring(top)

    with open(os.path.join(write_dir,filename_xml), "wb") as f:
        f.write(mydata)



if __name__ == '__main__':
    process_xml_bods()
