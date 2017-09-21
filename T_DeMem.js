var PythonShell = require('python-shell');

PythonShell.run('DeleteFile.py', function (err,results) {
  if (err) console.log(err);
  console.log('results: %j', results);
});