var accounting = require('accounting');
var moment = require('moment');
var Handlebars = require('handlebars/runtime').default;

Handlebars.registerHelper('percentOf', function(value, outOf, precision) {
    return accounting.formatNumber([value / outOf] * 100, precision);
})

Handlebars.registerHelper('costPer', function(values, spend) {
    return accounting.formatMoney([spend / values], '$', 2);
})

Handlebars.registerHelper('roas', function(spend, revenue) {
    return accounting.formatNumber([revenue / spend], 2);
})

Handlebars.registerHelper('formatNumber', function(val) {
    return accounting.formatNumber(val);
})

Handlebars.registerHelper('formatMoney', function(val) {
    var opts = {
        symbol: '$',
        precision: 0
    }
    return accounting.formatMoney(val, opts.symbol, opts.precision);
})

Handlebars.registerHelper('formatDate', function(val) {
    var d = moment(val)
    return d.format("M/D/YY")
})
