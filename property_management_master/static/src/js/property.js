/*$(document).ready(function(){
    $('.oe_product_image').imgLiquid();
})*/
odoo.define('property_management_master.property_search', function(require) {
    'use strict';


    var core = require('web.core');
    var config = require('web.config');
    var publicWidget = require('web.public.widget');
    const Utils = require('website.utils');

    publicWidget.registry.property_search = publicWidget.Widget.extend({
        selector: '.s_text_highlight',
        init: function() {
            this._super.apply(this, arguments);

        },
        start() {
            const def = this._super(...arguments);
            this._rpc({
            route: '/website/real_state_operations',
            params: {} 
            }).then((res) => {
                $.each(res, function(key, value) {
                    $('#snippet_real_state_op').append($('<option>', {
                        value: value[0],
                        text: value[1]
                    }));
                });


            });

            this._rpc({
                model: 'property.management.type',
                method: 'search_read',
                args: [
                    [],
                    ['name']
                ],
            }).then((res) => {
                $.each(res, function(key, value) {
                    $('#snippet_property_type_id').append($('<option>', {
                        value: value.id,
                        text: value.name
                    }));
                });



            });



            return def;
        },
    });
});