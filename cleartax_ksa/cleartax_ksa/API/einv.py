import frappe
import cleartax_ksa.utils as utils
import json
import requests 

@frappe.whitelist()
def generate_einv(**kwargs):
    try:
        invoice = frappe.get_doc('Sales Invoice',kwargs.get('invoice'))
        data = {
            'invoice': invoice.as_dict(),
            'customer': utils.get_dict('Customer',invoice.customer),
            'company': utils.get_dict('Company', invoice.company),
            'company_address': utils.get_dict('Address',invoice.company_address),
            'customer_address': utils.get_dict('Address',invoice.customer_address),
            'item_list': [utils.get_dict('Item', row.item_code) for row in invoice.items],
            'vat_settings': utils.get_dict('KSA VAT Settings',{'company':invoice.company})
        }
        return einv_request(data,invoice.name)
    except Exception as e:
        frappe.logger('cleartax').exception(e)



def einv_request(data,inv):
    try:
        settings = frappe.get_doc('Cleartax Settings')
        url = settings.host_url + "/api/method/cleartax.cleartax.API.irn.generate_irn"
        headers = {
            'sandbox': str(settings.sandbox),
            'Content-Type': 'application/json',
            'token': settings.get_password('sandbox_auth_token') if settings.sandbox else settings.get_password('production_auth_token'),
        }
        payload = json.dumps(data, indent=4, sort_keys=False, default=str)

        with requests.Session() as session:
            response = session.post(url, headers=headers, data=payload)
            response = response.json()['message']
            if response.get('error'):
                return utils.error_response(response.get('error'))

            utils.response_logger(response['request'], response['response'], "GENERATE IRN", "Sales Invoice", inv, response['msg'])

            if response['msg'] == 'Success':
                store_irn_details(inv,response['response'][0])
                return utils.success_response()

            return utils.response_error_handling(json.loads(json.dumps(response['response'][0])))


    except Exception as e:
        frappe.logger('cleartax').exception(e)


@frappe.whitelist()
def store_irn_details(inv,response):
    try:
        values = {
                    'ksa_einv_qr': response.get('QRCode'),
                    'generated_date': response.get('GeneratedDate'),
                    'generated_time': response.get('GeneratedTime')
                }
        frappe.db.set_value("Sales Invoice", inv, values)
        frappe.db.commit()
    except Exception as e:
        frappe.logger('cleartax').exception(e)
        return utils.error_response(e)