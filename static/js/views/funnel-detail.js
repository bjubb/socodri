var toolbar = require('../../templates/toolbar.hbs')
var modelView = require('../../templates/model-view.hbs')
var funnelSummary = require('../../templates/funnel-summary.hbs')
var stageList = require('../../templates/stage-list.hbs')
var topLabel = require('../../templates/label-top.hbs')
var request = require('superagent-bluebird-promise')
var Promise = require("bluebird");

module.exports.path = '/:funnel/'
module.exports.run = function(params) {
    'use strict'
    var toolbarEl = document.querySelector('#header-toolbar')
    toolbarEl.innerHTML = toolbar({viewName: 'funnel'})

    var contentEl = document.querySelector('#content')
    contentEl.innerHTML = modelView()

    var cardsEl = document.querySelector('#card-list')

    var funnel
    var stages
    var categories

    request.get('/api/funnel/' + params.funnel + '/')
        .then(function(response){
            funnel = response.body
            toolbarEl.innerHTML = toolbar({viewName: 'funnel', funnel: funnel})
            return Promise.all([
              request.get('/api/stage/').query({funnel: funnel.id}),
              request.get('/api/funnel/' + funnel.id + "/insights/"),
              request.get('/api/stage/insights/').query({funnel: funnel.id}),
              request.get('/api/label/categories/').query({funnel: funnel.id})
            ])
          })
          .spread(function(stage_response, insights_response, stage_insights_response, categories_response){
            stages = stage_response.body.objects
            funnel.insights = insights_response.body.data
            var stage_insights = stage_insights_response.body.data
            categories = categories_response.body.data

            var summaryEl = document.querySelector('#funnel-summary')
            summaryEl.innerHTML = funnelSummary({funnel: funnel})

            var i
            for(i = 0; i < stages.length; i++){
              stages[i].insights = stage_insights[stages[i].number]
            }
            cardsEl.innerHTML += stageList({funnel: funnel, stages: stages})

            var promises = []
            for(i = 0; i < categories.length; i++){
              promises.push(request.get('/api/label/insights/').query({funnel: funnel.id, category: categories[i]}))
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
                  return x.insights.conversions > y.insights.conversions ? -1 : 1
              })
          })
          .then(function(label_insights){
              var i = 0
              for(i; i < categories.length; i++){
                cardsEl.innerHTML += topLabel({category: categories[i], count: label_insights[i].length, label: label_insights[i][0], funnel: funnel})
              }

          })
          .catch(function(err){
            console.log(err)
          })
}
