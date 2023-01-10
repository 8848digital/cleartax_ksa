import frappe
import cleartax_ksa.utils as utils


@frappe.whitelist()
def generate_einv():
    try:
        pass
    except Exception as e:
        frappe.logger('cleartax').exception(e)

