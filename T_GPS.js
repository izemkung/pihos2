var PythonShell = require('python-shell');

var isError = 0;

PythonShell.run('GPS.py', function (err,results) 
{
  if (err)
  { 
    console.log(err);
  }
  console.log(results);
});

