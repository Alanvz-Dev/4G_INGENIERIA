odoo.define('flujo_efectivo.action_button', function (require) {
	"use strict";
	var core = require('web.core');
	var PivotController = require('web.PivotController');
	var rpc = require('web.rpc');
	var session = require('web.session');
	var _t = core._t;
	PivotController.include({
		renderButtons: function ($node) {
			this._super($node)
			if ($node && this.modelName === 'flujo_efectivo.flujo_efectivo') {
				var context = this.model.get(this.handle, { raw: true }).context				
				// if (context.show_xml_button !== undefined && context.show_xml_button == true) {
					if (this.$buttons.find(".o_pivot_download").length) {
						var $export_xml_button = $("<button type='button' class='btn btn-default o_pivot_download_xml'>Agregar Monto</button>");
						this.$buttons.find(".o_pivot_download").after($export_xml_button);
					}
				//}
			}
		},
		_onButtonClick: function (event) {
			var $target = $(event.target);
			if ($target.hasClass('o_pivot_download_xml')) {
				this._AgregarMonto();
			}
			else {
				this._super(event);
			}
		},
		_AgregarMonto: function () {
			var table = this.model.exportData();
			return this.do_action({
				name: "Agregar Monto Flujo de Efectivo",
				type: 'ir.actions.act_window',
				view_mode: 'form',
				views: [[false, 'form']],
				target: 'new',
				res_model: 'flujo_efectivo.agregar_monto',
				context: { data: JSON.stringify(table) }
			});


			/*table.title = this.title;
			session.get_file({
				url: '/web/pivot/export_xml',
				data: {data: JSON.stringify(table)},
				complete: framework.unblockUI,
				error: crash_manager.rpc_error.bind(crash_manager)
			});*/
		},
	})
});