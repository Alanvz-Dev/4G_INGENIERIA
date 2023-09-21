from odoo import models, fields, api
from odoo.exceptions import UserError


class AsistenteMaterialRequiredInternal(models.TransientModel):
    _name = "asistente.material.required.internal"
    _description = "Asistente para Requerir Materiales"
    @api.model
    def default_get(self, fields):
        res = super(
            AsistenteMaterialRequiredInternal, self.with_context(no_onchange=True)
        ).default_get(fields)
        # print("""Obtener campos""")
        record_ids = self._context.get("active_ids", [])
        # print("""Ids Activos""")
        picking_type = self.env["stock.picking.type"]

        type_ids = picking_type.search([("route_for_mrp", "=", True)])
        # print("""Filtra los registros donde route_for_mrp sea verdadero""")
        # Si es falso quiere decir que no hay operacion definida
        if not type_ids:
            raise UserError(
                (
                    "Error !\nNo existe una Operacion definida para Abastecimientos Internos de Produccion."
                )
            )

        mrp_obj = self.env["mrp.production"]

        if not record_ids:
            return {}
        location_id = False
        location_dest_id = 7
        location_id = type_ids[0].default_location_src_id.id
        production_qty = 0.0
        operation_id = type_ids[0].id
        # print("""Filtra por ID""")
        for mrp in mrp_obj.browse(record_ids):
            # print(record_ids)
            location_dest_id = mrp.location_src_id.id
            production_qty = mrp.product_qty
        res.update(
            location_id=location_id,
            location_dest_id=location_dest_id,
            production_qty=production_qty,
            operation_id=operation_id,
        )
        return res

    material_id_fk = fields.One2many(
        "asistente.material.required.internal.line", "wizard_id", "Detalle Materiales"
    )
    date_purchase = fields.Datetime("Fecha Planificada", default=fields.Datetime.now)
    quotation_exception_supplier = fields.Boolean("Crear Presupuesto para Excepciones")

    #### Partimos de las Ubicaciones #######
    location_dest_id = fields.Many2one("stock.location", "Ubicacion Destino")
    production_qty = fields.Float("Cantida a Producir", digits=(14, 2), readonly=True)
    operation_id = fields.Many2one("stock.picking.type", "Tipo de Operacion")
    location_id = fields.Many2one("stock.location", "Ubicacion Origen")    
    confirm_transfer = fields.Boolean(
        "Validar Transferencia",
        help="Valida la transferencia de forma automatica",
        default=False,
    )

    @api.onchange("location_id")
    def onchange_location_id(self):
        material_list = []
        if not self.location_id:
            return {}        
        record_ids = self._context.get("active_ids", [])
        picking_type = self.env["stock.picking.type"]
        mrp_obj = self.env["mrp.production"]    
        location_id = False
        location_dest_id = False
        location_id = self.location_id.id
        # print("Location id : ")
        # print(location_id)
        for mrp in mrp_obj.browse(record_ids):
            #print(record_ids)
            location_dest_id = mrp.location_src_id.id
            # print(location_dest_id)
            # print(mrp)
            # print("""############################""")
            # Cambio move_lines por  move_raw_ids
            valor = 0
            for product in mrp.move_raw_ids:
                valor = valor + 1
                #print(str(valor))
                qty_need = product.product_uom_qty
                # qty_reservated_in_dest = product.product_id.qty_available_not_res
                qty_reservated_in_dest = 0.0
                qty_reservated = 0.0

                self.env.cr.execute(
                    """
                    select sum(quantity) from stock_quant 
                        where location_id=%s and 
                        product_id=%s;

                    """,
                    (location_id, product.product_id.id,),
                )
                res_qty = self.env.cr.fetchall()
                if res_qty:
                    qty_reservated = res_qty[0][0] if res_qty[0][0] else 0.0

                self.env.cr.execute(
                    """
                    select sum(quantity) from stock_quant 
                        where location_id=%s and 
                        product_id=%s;

                    """,
                    (location_dest_id, product.product_id.id,),
                )
                res_qty_02 = self.env.cr.fetchall()
                if res_qty_02:
                    qty_reservated_in_dest = (
                        res_qty_02[0][0] if res_qty_02[0][0] else 0.0
                    )

                mrp_uom = product.product_uom
                product_uom = product.product_id.uom_id
                if mrp_uom != product_uom:
                    uom = product_uom
                    qty_reservated = uom._compute_quantity(qty_reservated, mrp_uom)

                qty_to_transfer = 0.0
                if qty_reservated_in_dest <= 0.0:
                    if qty_reservated > qty_need:
                        if qty_reservated_in_dest < 0.0:
                            qty_to_transfer = abs(qty_reservated_in_dest) + qty_need
                        else:
                            qty_to_transfer = qty_need
                    else:
                        qty_to_transfer = qty_reservated

                material_list.append(
                    (
                        0,
                        0,
                        {
                            "product_id": product.product_id.id,
                            "uom_id": product.product_uom.id,
                            "qty_need": qty_need,
                            "qty_reservated": qty_reservated,
                            "qty_to_transfer": qty_to_transfer,
                            "product_id_name": product.product_id.name_get()[0][1],
                            "uom_id_name": product.product_uom.name_get()[0][1],
                            "qty_reservated_in_dest": qty_reservated_in_dest,
                        },
                    )
                )
        self.update({"material_id_fk": material_list})

        #print((material_list))

    @api.multi
    def make_transfer(self):
        active_ids = self._context["active_ids"]
        picking_obj = self.env["stock.picking"]
        move_obj = self.env["stock.move"]
        mrp_obj = self.env["mrp.production"]
        vals = {}        
        picking_list = []
        # Por cada registro de esta clase
        for record in self:
            if record.location_id == record.location_dest_id:
                raise UserError(
                    "Error !\nLa Ubicacion Origen y Destino no puede ser la misma."
                )
            mrp_browse = mrp_obj.browse(active_ids)            
            move_line_ids = []            
            for material in record.material_id_fk:
                #print(material)
                if material.qty_to_transfer > 0.0:
                    xline = (
                        0,
                        0,
                        {
                            "location_id'": 12,
                            "location_dest_id": 7,
                            "qty_done": material.qty_to_transfer,
                            "product_id": material.product_id,
                            "move_id'": False,
                            "product_uom_id": material.uom_id,
                            "result_package_id": False,
                            "owner_id": False,
                            "lot_id":False,
                            "lot_name":False,
                        },
                    )
                    #print(xline)
                    move_line_ids.append(xline)

            if not move_line_ids:
                raise UserError(
                    "Error !\nNo requires Cantidades Adicionales de Material para la Produccion."
                )
            vals = {
                "is_locked": True,
                "location_id": 12,
                "location_dest_id": record.location_dest_id.id,
                "move_type": "direct",
                "company_id": 1,
                "partner_id": False,
                "origin":False,                
                "owner_id": False,                
                "move_line_ids": move_line_ids,

                "picking_type_id": 5,
                # "priority": 1,
                "ev1": False,
                "ev2": False,
                "ev3": False,
                "ev4": False,
                "note": False,
            }

            print(vals)
            # Stock Picking
            picking_id = picking_obj.create(vals)
            mrp_browse.write({"last_picking_id": picking_id.id})
            picking_id.action_confirm()
            picking_id.force_assign()
            picking_obj.button_validate()
#             if record.confirm_transfer:
#                 ## confirmando el Albaran
#                 picking_id.action_confirm()
#                 picking_id.force_assign()
#                 for mvline in picking_id.move_line_ids:
#                     mvline._action_done()
#                     #print(picking_id)
#                 picking_id.do_transfer()
#             picking_list.append(picking_id.id)
#             # print("""&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&""")
#             # print(type(picking_list))
#             for pick_id in picking_id:
#                 sql =("""select id,product_id,product_uom,product_qty,product_uom_qty, ordered_qty,date,location_id,location_dest_id, reference,create_uid,create_date,write_uid,write_date from stock_move where picking_id="""+ str(pick_id.id)+";")
#                 #print(sql)


#                 self.env.cr.execute(
#  sql
#                 )
#                 material = self.env.cr.fetchall()
#                 for res_move in material:                                                        
#                     tbl_stock_picking = self.env["stock.picking"].browse(picking_id.id)
#                     tbl_stock_picking.button_validate()
                



