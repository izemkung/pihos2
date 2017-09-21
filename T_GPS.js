var PythonShell = require('python-shell');

var isError = 0;

PythonShell.run('GPS.py', function (err) 
{
  if (err)
  { 
    console.log(err);
  }
  console.log('GPS connection ERROR > 20 time');
});

