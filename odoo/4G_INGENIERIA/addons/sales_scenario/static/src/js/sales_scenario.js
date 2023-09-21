odoo.define('sales_scenario.sale_scenario', function (require) {

var core = require('web.core');
var data = require('web.data');
var ActionManager = require('web.ActionManager');
var form_common = require('web.form_common');
var time = require('web.time');
var _t = core._t;
var QWeb = core.qweb;

var ScenarioSummary = form_common.FormWidget.extend(form_common.ReinitializeWidgetMixin, {
        display_name: _t('Form'),
        view_type: "form",
        init: function() {
            this._super.apply(this, arguments);
            if(this.field_manager.model == "sale.scenario")
            {
                $(".oe_view_manager_buttons").hide();
                $(".oe_view_manager_header").hide();
            }
           this.set({
               summary: false,
               summary_header: false,
               summary_total: false,
           });
           this.summary = [];
           this.summary_header = [];
           this.summary_total = [];
           this.field_manager.on("field_changed:summary", this, function() {
                this.set({"summary":this.field_manager.get_field_value("summary")});
            });
            this.field_manager.on("field_changed:summary_header", this, function() {
                 this.set({"summary_header":this.field_manager.get_field_value("summary_header")});
             });
             this.field_manager.on("field_changed:summary_total", this, function() {
                  this.set({"summary_total":this.field_manager.get_field_value("summary_total")});
              });
       },
       initialize_field: function() {
            form_common.ReinitializeWidgetMixin.initialize_field.call(this);
            var self = this;
            self.initialize_content;
        },
        initialize_content: function() {
           var self = this;
           if (self.setting)
               return;

           this.destroy_content();

           if (this.get("summary")) {
            this.summary = py.eval(this.get("summary"));
           }
           if (this.get("summary_header")) {
            this.summary_header = py.eval(this.get("summary_header"));
           }
           if (this.get("summary_total")) {
            this.summary_total = py.eval(this.get("summary_total"));
           }

           this.renderElement();
           this.view_loading();
        },
        view_loading: function(r) {
            return this.load_form(r);
        },
        load_form: function(data) {
            self.action_manager = new ActionManager(self);
        },
        renderElement: function() {
             this.destroy_content();
             this.$el.html(QWeb.render("scenarioTemplate", {widget: this}));
        }
    });


var ScenarioSummaryOrder = form_common.FormWidget.extend(form_common.ReinitializeWidgetMixin, {
            display_name: _t('Form'),
            view_type: "form",
            init: function() {
                this._super.apply(this, arguments);
                if(this.field_manager.model == "sale.scenario.order")
                {
                    $(".oe_view_manager_buttons").hide();
                    $(".oe_view_manager_header").hide();
                }
               this.set({
                   summary: false,
                   summary_header: false,
                   summary_total: false,
               });
               this.summary = [];
               this.summary_header = [];
               this.summary_total = [];
               this.field_manager.on("field_changed:summary", this, function() {
                    this.set({"summary":this.field_manager.get_field_value("summary")});
                });
                this.field_manager.on("field_changed:summary_header", this, function() {
                     this.set({"summary_header":this.field_manager.get_field_value("summary_header")});
                 });
                 this.field_manager.on("field_changed:summary_total", this, function() {
                      this.set({"summary_total":this.field_manager.get_field_value("summary_total")});
                  });
           },
           initialize_field: function() {
                form_common.ReinitializeWidgetMixin.initialize_field.call(this);
                var self = this;
                self.initialize_content;
            },
            initialize_content: function() {
               var self = this;
               if (self.setting)
                   return;

               this.destroy_content();

               if (this.get("summary")) {
                this.summary = py.eval(this.get("summary"));
               }
               if (this.get("summary_header")) {
                this.summary_header = py.eval(this.get("summary_header"));
               }
               if (this.get("summary_total")) {
                this.summary_total = py.eval(this.get("summary_total"));
               }

               this.renderElement();
               this.view_loading();
            },
            view_loading: function(r) {
                return this.load_form(r);
            },
            load_form: function(data) {
                self.action_manager = new ActionManager(self);
            },
            renderElement: function() {
                 this.destroy_content();
                 this.$el.html(QWeb.render("scenarioTemplate", {widget: this}));
            }
        });

var ScenarioSummaryTotal = form_common.FormWidget.extend(form_common.ReinitializeWidgetMixin, {
                    display_name: _t('Form'),
                    view_type: "form",
                    init: function() {
                        this._super.apply(this, arguments);
                        if(this.field_manager.model == "sale.scenario.total")
                        {
                            $(".oe_view_manager_buttons").hide();
                            $(".oe_view_manager_header").hide();
                        }
                       this.set({
                           summary: false,
                           summary_header: false,
                           summary_total: false,
                       });
                       this.summary = [];
                       this.summary_header = [];
                       this.summary_total = [];
                       this.field_manager.on("field_changed:summary", this, function() {
                            this.set({"summary":this.field_manager.get_field_value("summary")});
                        });
                        this.field_manager.on("field_changed:summary_header", this, function() {
                             this.set({"summary_header":this.field_manager.get_field_value("summary_header")});
                         });
                         this.field_manager.on("field_changed:summary_total", this, function() {
                              this.set({"summary_total":this.field_manager.get_field_value("summary_total")});
                          });
                   },
                   initialize_field: function() {
                        form_common.ReinitializeWidgetMixin.initialize_field.call(this);
                        var self = this;
                        self.initialize_content;
                    },
                    initialize_content: function() {
                       var self = this;
                       if (self.setting)
                           return;

                       this.destroy_content();

                       if (this.get("summary")) {
                        this.summary = py.eval(this.get("summary"));
                       }
                       if (this.get("summary_header")) {
                        this.summary_header = py.eval(this.get("summary_header"));
                       }
                       if (this.get("summary_total")) {
                        this.summary_total = py.eval(this.get("summary_total"));
                       }

                       this.renderElement();
                       this.view_loading();
                    },
                    view_loading: function(r) {
                        return this.load_form(r);
                    },
                    load_form: function(data) {
                        self.action_manager = new ActionManager(self);
                    },
                    renderElement: function() {
                         this.destroy_content();
                         this.$el.html(QWeb.render("scenarioTemplateTot", {widget: this}));
                    }
                });



core.form_custom_registry.add('Scenario_Summary', ScenarioSummary);
core.form_custom_registry.add('Scenario_Summary_Order', ScenarioSummaryOrder);
core.form_custom_registry.add('Scenario_Summary_Total', ScenarioSummaryTotal);
});
