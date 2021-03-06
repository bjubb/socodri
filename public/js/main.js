var ready = require('detect-dom-ready')
var Route = require('route-parser')
require('./handlebars-helpers')

var modules = [
    require('./views/window-detail'),
    require('./views/initiative-detail'),
    require('./views/initiative-list'),
]
var location = window.location.pathname

reverse_url = function(mount, url){
    return mount ? '/' + mount + url : url
}

function loadApp(){
    for (var i in modules) {
        var m = modules[i]
        var r = new Route(m.path)
        var params = r.match(location)
        if (params) m.run(params)
    }
}

ready(loadApp)
