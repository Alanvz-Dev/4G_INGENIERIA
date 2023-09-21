//Define el id externo
odoo.define('production_time.my_custom_widget', function (require) {    
    'use strict';
    //El parametro require permite al módulo importar otros módulos
    // var AbstractAction = require('web.AbstractAction');
    var Widget = require('web.Widget');
    // var view_registry = require('web.view_registry');
    // Realizamos un seguimiento de todas las acciones del cliente en este registro. 
    //Aquí es donde el administrador de acciones busca cada vez 
    //que necesita crear una acción de cliente. 
    var core = require('web.core');
    /**
     * core.qweb
     * (el núcleo es el módulo web.core) 
     * Una instancia de QWeb2.Engine () 
     * con todos los archivos de plantilla definidos por el módulo cargados 
     * y referencias a objetos auxiliares estándar _ (subrayado), _t (función de traducción) 
     * y JSON.
     * core.qweb.render se puede utilizar para representar 
     * fácilmente plantillas de módulos básicos
     */
    var rpc = require('web.rpc');
    //Llamada a procedimiento remoto
    var QWeb = core.qweb;
    var CustomWidget = Widget.extend({
    template: 'TemplateWidgetName',
        events: {
        },
        init: function(parent, action) {
            this._super(parent, action);
        },
        //El método init () actúa como constructor. 
        //Esta clase se puede instanciar de esta manera:
        start: function() {
            var self = this;
            
            self.load_data();
        },
        /**
         * Cuando se agrega un widget de campo al DOM, 
         * se llama a su método de inicio y automáticamente llamará a render. 
         * La mayoría de los widgets no deberían anular esto.
         */
        load_data: function () {
            var self = this;
            alert("Hello")
            console.log(self)
                    var self = this;
                    self._rpc({
                        model: 'production_time.data',
                        method: 'get_data_custom_widget',
                        args: [],
                    }).then(function(datas) {
                        console.log(datas)
                    console.log("dataaaaaa", datas)
                        self.$('.table_view').html(QWeb.render('TemplateWidgetName', {
                            // report_lines es el alias con el que identificara la variable
                                   report_lines : datas,
                        }));
                    });
            },
        /**
         * Busca las diversas clases de FontAwesome en el elemento enlazado 
         * y establece los elementos de plantilla / formulario correspondientes 
         * en el estado correcto. Si varias clases de la misma categoría están presentes 
         * en un elemento (por ejemplo, fa-lg y fa-3x), se seleccionará la última que ocurra, 
         * que puede no coincidir con el aspecto visual del elemento.
         */
    });
    core.action_registry.add('my_custom_widget', CustomWidget);
    /**
     * Debemos hacer que el cliente web sea consciente del mapeo entre las acciones del cliente 
     * y la clase real
     */
    return CustomWidget;
 });