frappe.ui.form.on('Sales Invoice', {
	refresh(frm) {
		if (frm.selected_doc.docstatus == 1 && frm.selected_doc.ksa_qr == undefined) {
						cur_frm.add_custom_button(__("E-Invoice"), function () {
							frappe.call({
								method: "cleartax_ksa.cleartax_ksa.API.einv.generate_einv",
								args: {
									invoice: frm.selected_doc.name
								},
								callback: function (r) {
								//console.log(r.message)
									if (r.message.msg == 'success') {
										frappe.msgprint("IRN Created Successfully!")
										location.reload();
									}
									else {
										// frappe.msgprint(r.message.error)
										frappe.msgprint(r.message.error)
									}
								}
							});
						}, __('Create'));
						cur_frm.page.set_inner_btn_group_as_primary(__('Create'));
					}
                }
            });
					