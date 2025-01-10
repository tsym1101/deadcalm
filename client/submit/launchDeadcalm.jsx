projectName = app.project.file.name;
projectName = projectName.toString();

projectPath = app.project.file.fsName; 
projectPath = projectPath.toString();

var version = app.version.substring( 0, app.version.indexOf( 'x' ) );

var cmd = "python.exe client/submit/submit_ae.py";
cmdAddArg = cmd + " -flag " + "0" + " -name " + projectName + " -path " + projectPath + " -ver " + version ;
system.callSystem(cmdAddArg);
