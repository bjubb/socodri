var layout = require('../../views/layouts/window.hbs')
var toolbarContext = require('../../views/partials/toolbar-context.hbs')
var request = require('superagent-bluebird-promise')
var moment = require("moment")
var Promise = require("bluebird")
var Handlebars = require('handlebars/runtime').default
Handlebars.registerPartial('window-card', require('../../views/partials/window-card.hbs'))


module.exports.path = '/(:mount/):initiative/window/:window/'
module.exports.run = function(params) {
    'use strict'
    var contentEl = document.querySelector('#content')

    var initiative
    var _window
    var categories

    request.get(reverse_url(params.mount, '/api/initiative/' + params.initiative + '/'))
        .then(function(response){
            initiative = response.body
            var context = document.querySelector('#context')
            context.innerHTML = toolbarContext(initiative)
            return Promise.all([
              request.get(reverse_url(params.mount, '/api/window/' + params.window + "/")),
              request.get(reverse_url(params.mount, '/api/window/' + params.window + "/insights/")),
              request.get(reverse_url(params.mount, '/api/label/categories/')).query({window: params.window})
            ])
          })
          .spread(function(window_response, insights_response, categories_response){
            _window = window_response.body
            _window.insights = insights_response.body.data
            _window.labels = []
            categories = categories_response.body.data

            contentEl.innerHTML = layout(_window)

            var i
            var promises = []
            for(i = 0; i < categories.length; i++){
              promises.push(request.get(reverse_url(params.mount, '/api/label/insights/')).query({window: _window.id, category: categories[i]}))
            }
            return Promise.all(promises)
          })
          .map(function(response){
              var label_insights = []
              for(var k in response.body.data){
                label_insights.push({
                  text: k,
                  insights: response.body.data[k]
                })
              }
              return label_insights.sort(function(x, y){
                  return (x.insights.spend/x.insights.conversions) <= (y.insights.spend/y.insights.conversions) ? -1 : 1
              })
          })
          .then(function(label_insights){
              var i = 0
              for(i; i < categories.length; i++){
                //contentEl.innerHTML += labelList({category: categories[i], labels: label_insights[i], funnel: funnel})
              }
          })
          .catch(function(err){
            console.log(err)
          })
}
