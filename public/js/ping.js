var request = require('superagent')

request
  .get('/ping')
  .end(function(err, response) {
    if (err) {
      console.error(`error contacting server: ${err.message}`)
    } else {
      console.log(`pinged server, response: ${response.text}`)
    }
  })
