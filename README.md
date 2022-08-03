# Quick Roster

## Front End Codebase
This codebase contains everything needed to launch the front end. The front end can be installed with and launched with:
```
npm install
npm run serve
```

To reconfigure the service for use with a different identity pool and S3 bucket edit the 
bucketName, bucketRegion, IdentidyPoolId variables in the /src/app/upload.js and /.env files.


## Fargate Setup
This directory contains the code required to setup a solver as a Fargate task. This code
is adapted from this excellent blog: https://www.serverless.com/blog/serverless-application-for-long-running-process-fargate-lambda. I recommend reading the blog before trying to adapt the code.


## NSP Codebase
This codebase contains a nurse scheduling problem solver, tools to parse benchmark instances, tools to generate
sample data, machine learning notebook for optimizing the solver, and a machine learning pipeline.

### Required Python Packages
 - Python v3.8
 - gurobipy
 - pandas 
 - imblearn 
 - joblib 
 - numpy 
 - sklearn
 - from mlxtend
 - matplotlib
 - seaborn

### DataPipeline  
Experiments can be performed using this pipeline. The pipeline is controlled by the aptly named 'run_pipeline' script. To reconfigure the default directories, edit the 'pipeline_constants' file. The pipeline is bootstrapped by a series of helper scripts. Each script simply calls objects from the other directories of this project.

### NspDataProducers  
This directory contains the objects require to parse SchedulingBenchmark.org multi-activity problems and modify them, and a range of encoding and decoding objects for reading schedule JSONs

### NspMl  
This directory contains a series of enumerated notebooks for training models to solve the NSP.

### NspObjects 
The directory contains all the primitive NSP objects like rosters, schedules, shiftData, etc.

### NspSolver  
This contains the Gurobi implementation of the NSP algorithm described in my final year report.

### NspUtils
This contains a misc range of helper scripts as well as the notebooks used to decide distribution parameters are contained here.

