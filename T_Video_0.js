var PythonShell = require('python-shell');

var isError = 0;


PythonShell.run('VDOS.py', function (err,results) 
{
  if (err)
  { 
    console.log(err);
  }
  console.log('results: %j', results);
});
