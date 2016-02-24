var layout = require('../../views/layouts/initiative.hbs')
var toolbarContext = require('../../views/partials/toolbar-context.hbs')
var request = require('superagent-bluebird-promise')
var moment = require("moment")
var numeral = require("numeral")
var Chart = require('chart.js')
var Promise = require("bluebird")
var Handlebars = require('handlebars/runtime').default
Handlebars.registerPartial('window-card', require('../../views/partials/window-card.hbs'))
var initiative

module.exports.path = '/:mount/:initiative/'
module.exports.run = function(params) {
    'use strict'

    Chart.defaults.global.responsive = true
    Chart.defaults.global.showTooltips = false
    Chart.defaults.global.scaleLabel = function (valuePayload) {
      return '$' + Number(valuePayload.value).toFixed(0)
    }

    request.get(reverse_url(params.mount, '/api/initiative/' + params.initiative + '/'))
        .then(function(response){
            initiative = response.body
            initiative.windows = []

            var context = document.querySelector('#context')
            context.innerHTML = toolbarContext(initiative)

            draw(initiative)

            return Promise.all([
              request.get(reverse_url(params.mount, '/api/initiative/' + initiative.id + "/insights/")),
              request.get(reverse_url(params.mount, '/api/window/')).query({initiative: initiative.id}),
            ])
          })
          .spread(function(insights_response, window_response){
              initiative.insights = insights_response.body.data
              initiative.total_insights = {
                  spend: 0,
                  conversions: 0,
                  impressions: 0,
                  since: initiative.insights[0].date_start,
                  until: initiative.insights[initiative.insights.length-1].date_stop
              }

              var i
              for(i=0; i < initiative.insights.length; i++){
                initiative.total_insights.impressions += Number(initiative.insights[i].impressions)
                initiative.total_insights.conversions += initiative.insights[i].conversions
                initiative.total_insights.spend += initiative.insights[i].spend
              }
              initiative.windows = window_response.body.objects
              draw(initiative)

              for(i = 0; i < initiative.windows.length; i++){
                loadWindow(initiative.windows[i])
              }
        })
        .catch(function(err){
            console.log(err)
        })

function loadWindow(_window){
    request.get(reverse_url(params.mount, '/api/window/' + _window.id + '/insights/'))
      .then(function(response){
          _window.insights = response.body.data
          draw(initiative)
      })
}

function draw(initiative){
    initiative.windows.sort(function(x, y){
      var diff = 0
      if(x.insights && y.insights){
        var stop = moment(x.insights.date_stop)
        diff = stop.diff(y.insights.date_stop)
        if(diff == 0){
          var start = moment(x.insights.date_start)
          diff = start.diff(y.insights.date_start)
        }
        return diff
      }
    })
    var contentEl = document.querySelector('#content')
    contentEl.innerHTML = layout(initiative)
    if(initiative.insights){
        var chartData = {
          labels: [],
          datasets: [{
            label: "Cost",
            type:'line',
            data: [],
            fill: false,
            backgroundColor: '#f5872e',
            borderColor: '#f5872e',
            pointBackgroundColor: '#f5872e',
            yAxisID: 'y-axis-2'
          },
          {
            type: 'bar',
            label: "Spend",
            data: [],
            fill: false,
            backgroundColor: '#1a707f',
            borderColor: '#1a707f',
            yAxisID: 'y-axis-1'
          }]
        }

      var i
      for(i=0; i < initiative.insights.length; i++){
        var label = moment(initiative.insights[i].date_stop).format("MMM 'YY")
        chartData.labels.push(i % 2 ? '' : label)

        chartData.datasets[1].data.push(Number(initiative.insights[i].spend).toFixed(0))
        var costPer = initiative.insights[i].conversions == 0 ? 0 : initiative.insights[i].spend / initiative.insights[i].conversions
        chartData.datasets[0].data.push(Number(costPer).toFixed(0))
      }

      var ctx = document.getElementById(initiative.slug+'-chart').getContext('2d');

      new Chart(ctx, {
          type: 'bar',
          data: chartData,
          options: {
            responsive: true,
            scales: {
              xAxes: [{
                display: true,
                barPercentage: 1.0,
                categoryPercentage: 1.0,
                gridLines: {
                    display: false
                },
                labels: {
                    show: true,
                }
              }],
              yAxes: [{
                type: "linear",
                display: true,
                position: "left",
                id: "y-axis-1",
                gridLines:{
                    display: false
                },
                ticks:{
                  callback: function(tickValue, index, ticks){
                    return numeral(tickValue).format('($0a)')
                  }
                },
                labels: {
                    show:true,
                }
              },{
                type: "linear",
                display: true,
                position: "right",
                id: "y-axis-2",
                gridLines:{
                    display: false
                },
                ticks:{
                  callback: function(tickValue, index, ticks){
                    return numeral(tickValue).format('($0a)')
                  }
                },
                labels: {
                    show:false,
                }
              }]
            }
          }
        })
      }
  }
}
