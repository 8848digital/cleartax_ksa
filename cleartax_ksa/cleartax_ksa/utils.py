import frappe
import json
import io
import os
from base64 import b64encode
from pyqrcode import create as qr_create


def create_cl_qr(qr,inv):
    doc = frappe.get_doc('Sales Invoice',inv)
    base64_string = b64encode(bytes.fromhex(qr)).decode()
    qr_image = io.BytesIO()
    url = qr_create(base64_string, error="L")
    url.png(qr_image, scale=2, quiet_zone=1)
    name = frappe.generate_hash(doc.name, 5)
    # making file
    filename = f"QRCode-{name}.png".replace(os.path.sep, "__")
    _file = frappe.get_doc(
        {
            "doctype": "File",
            "file_name": filename,
            "is_private": 0,
            "content": qr_image.getvalue(),
            "attached_to_doctype": doc.get("doctype"),
            "attached_to_name": doc.get("name"),
            "attached_to_field": "cleartax_qr",
        }
    )
    _file.save()
    # assigning to document
    doc.db_set("cleartax_qr", _file.file_url)

def get_dict(type,doc):
    if frappe.db.exists(type,doc):
        return frappe.get_doc(type,doc).as_dict()
    return None

    
def success_response(data=None):
    response = {'msg': 'success'}
    if data: 
        response['data'] = data
    return response 

def error_response(err_msg):
    return {
        'msg': 'error',
        'error': err_msg
    }

def response_error_handling(response):
    error = ""
    errors = []
    if type(response) ==list:
        response = response[0]
    if type(response) == str:
        return error_response(response)
    if type(response) == None:
        return error_response("No response received!")
    if response.get('govt_response'):
        if response.get('govt_response').get('ErrorDetails'):
            errors = response.get('govt_response').get('ErrorDetails')
    elif response.get('ErrorDetails'):
        errors = response.get('ErrorDetails')
    elif response.get('errorDetails'):
        errors.append(response.get('errorDetails'))
    elif response.get('errors') and response.get('errors').get('errors'):
            errors = response.get('errors').get('errors') 
    else:
        errors.append({'error_message':json.dumps(response)})
    c=1
    for i in errors:
        error += str(c) + ". " + i.get("error_message") + "\r\n"
        c+=1 
    return error_response(error)



        
def response_logger(payload,response,api,doc_type,doc_name,status="Failed"):
    try:
        response = json.dumps(response, indent=4, sort_keys=False, default=str)
        if frappe.db.exists('Cleartax Api Log',{'document_name':doc_name,'api':api}):
            doc = frappe.get_doc('Cleartax Api Log',{'document_name':doc_name,'api':api})
            doc.request_data = payload
            doc.response = response
            doc.status = status
            doc.save(ignore_permissions=True)
        else:
            doc = frappe.new_doc('Cleartax Api Log')
            doc.document_type = doc_type
            doc.document_name = doc_name
            doc.api = api
            doc.request_data = payload
            doc.response = response
            doc.status = status
            doc.insert(ignore_permissions=True)
        frappe.db.commit()
    except Exception as e:
        frappe.logger('response').exception(e)