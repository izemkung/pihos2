var PythonShell = require('python-shell');

PythonShell.run('GPIO.py', function (err,results) {
  if (err)  console.log(err);
  console.log('results: %j', results);
});