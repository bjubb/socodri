var layout = require('../../views/layouts/list.hbs')
var toolbarContext = require('../../views/partials/toolbar-context.hbs')
var request = require('superagent-bluebird-promise')
var Handlebars = require('handlebars/runtime').default
Handlebars.registerPartial('initiative-card', require('../../views/partials/initiative-card.hbs'))

module.exports.path = '/:mount/'
module.exports.run = function(params) {
    'use strict'

    var contentEl = document.querySelector('#content')

    request.get(reverse_url(params.mount, '/api/initiative/'))
        .then(function(response){
            var context = document.querySelector('#context')
            context.innerHTML = toolbarContext({brand_name: 'SocialCode', name: 'Initiatives'})
            contentEl.innerHTML = layout({initiatives: response.body.objects})
          })
        .catch(function(err){
            console.log(err)
        })
}
