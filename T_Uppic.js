var PythonShell = require('python-shell');

var isError = 0;

PythonShell.run('newPic.py', function (err,results) 
{
  if (err)
  { 
    console.log(err);
  }
  console.log('results: %j', results);
});

