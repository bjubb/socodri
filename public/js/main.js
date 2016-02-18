var ready = require('detect-dom-ready')
var Route = require('route-parser')
require('./handlebars-helpers')

var modules = [
    require('./views/window-detail'),
    require('./views/initiative-detail'),
]
var location = window.location.pathname

function loadApp(){
    for (var i in modules) {
        var m = modules[i]
        var r = new Route(m.path)
        var params = r.match(location)
        if (params) m.run(params)
    }
}

ready(loadApp)
