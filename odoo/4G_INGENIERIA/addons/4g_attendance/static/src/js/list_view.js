odoo.define('4g_attendance.ListController', function (require) {
"use strict";

var ListController = require('web.ListController');

ListController.include({
	renderButtons: function ($node) {
		this._super($node)
		debugger;
		if (this.modelName==='hr.attendance' && !this.noLeaf){
			var context = this.model.get(this.handle, {raw: true}).getContext();
			/*if (context.is_fiel_attachment!==undefined && context.is_fiel_attachment==true){*/
				if (this.$buttons.find(".o_list_button_discard").length){
					var $import_button = $("<button type='button' class='btn btn-default btn-sm o_list_button_import_asistencia' accesskey='if'>importar asistencia</button>");
					this.$buttons.find(".o_list_button_discard").after($import_button);
					this.$buttons.on('click', '.o_list_button_import_asistencia', this._onImportAttendance.bind(this));
				}
			/*}	*/
		}
	},
    _onImportAttendance: function (event) {
        event.stopPropagation();
        return this.do_action({
            name: "importar asistencia",
            type: 'ir.actions.act_window',
            view_mode: 'form',
            views: [[false, 'form']],
            target: 'new',
            res_model: 'import.attendance'
        });
    },
});
});