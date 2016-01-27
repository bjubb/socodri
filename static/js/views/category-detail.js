var toolbar = require('../../templates/toolbar.hbs')
var modelView = require('../../templates/model-view.hbs')
var funnelSummary = require('../../templates/funnel-summary.hbs')
var labelList = require('../../templates/label-list.hbs')
var request = require('superagent-bluebird-promise')
var Promise = require("bluebird");

module.exports.path = '/:funnel/category/:category/'
module.exports.run = function(params) {
    'use strict'
    var toolbarEl = document.querySelector('#header-toolbar')
    toolbarEl.innerHTML = toolbar({viewName: 'funnel'})

    var contentEl = document.querySelector('#content')
    contentEl.innerHTML = modelView()

    var category = params.category
    var funnel

    request.get('/api/funnel/' + params.funnel + '/')
        .then(function(response){
            funnel = response.body
            toolbarEl.innerHTML = toolbar({viewName: 'funnel', funnel: funnel, context: category})
            return Promise.all([
              request.get('/api/funnel/' + funnel.id + "/insights/"),
              request.get('/api/label/insights/').query({funnel: funnel.id, category: category})
            ])
          })
          .spread(function(fi_response, ci_response){
            funnel.insights = fi_response.body.data

            var summaryEl = document.querySelector('#funnel-summary')
            summaryEl.innerHTML = funnelSummary({funnel: funnel})

            var label_insights = []
            for(var k in ci_response.body.data){
                label_insights.push({
                  text: k,
                  insights: ci_response.body.data[k]
              })
            }

            label_insights.sort(function(x, y){
                return x.insights.conversions > y.insights.conversions ? -1 : 1
            })

            var cardsEl = document.querySelector('#card-list')
            cardsEl.innerHTML += labelList({category: category, labels: label_insights, funnel: funnel})
          })
          .catch(function(err){
            console.log(err)
          })
}
