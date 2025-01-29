# How to Use TaskChainSample.py

## Overview

`TaskChainSample.py` demonstrates how to create and manage task chains using the DeadCalm framework. This sample script shows how to define and structure tasks, configure dependencies, and submit jobs using the GUI or command line.

## Prerequisites

- Ensure you have set up the environment as described in the `README.md`.
- Install required dependencies using:
  ```bash
  pip install -r requirements.txt
  ```
- Ensure `config.json` is correctly configured.

## Running the Sample

You can run `TaskChainSample.py` in two modes:

### GUI Mode

This will launch the GUI for job submission.

```bash
python samples/TaskChainSample.py
```

### CLI Mode

To submit a job directly via command line, modify the script as follows:

1. Uncomment `run_cli()` and comment out `run_gui()`.
2. Run:
   ```bash
   python samples/TaskChainSample.py
   ```

## Task Structure

### Creating a Job

The script initializes a `JobBase` instance as the root job:

```python
job = JobBase()
job.title = 'test job'
job.priority = 55
job.projects = ["test_project"]
```

### Adding Tasks

The script defines three types of tasks:

1. **Maya Task** (`TaskMaya`)
   ```python
   taskMaya = TaskMaya()
   taskMaya.title = 'maya task test'
   taskMaya.projectFolder = 'projects/test'
   taskMaya.fileName = 'foo.mb'
   taskMaya.start = 1
   taskMaya.end = 20
   ```
2. **Nuke Task** (`TaskNuke`)
   ```python
   taskNuke = TaskNuke()
   taskNuke.title = 'nuke test'
   taskNuke.fileName = 'aaa.nk'
   ```
3. **Custom Task** (`TaskCustom`)
   ```python
   taskCustom = TaskCustom()
   taskCustom.title = 'my custom task'
   taskCustom.executable = taskCustom.appendD('mayabatch')
   taskCustom.envkey = ['maya2018']
   taskCustom.option = ['-proj','aaaaaa','aaa.mb']
   ```

### Nested Task Chains

The script also demonstrates nested task chains:

```python
# Root task
taskRoot = TaskBase()
taskRoot.title = 'root'

# Parent task
taskParent = TaskBase()
taskParent.title = 'parent'

# Child tasks
taskChild1 = TaskCustom()
taskChild1.executable = 'cmd.exe'
taskChild1.title = "child1"

taskChild2 = TaskCustom()
taskChild2.title = "child2"
taskChild2.executable = 'cmd.exe'

# Structuring the hierarchy
taskParent.addChild(taskChild1)
taskParent.addChild(taskChild2)
taskRoot.addChild(taskParent)

# Defining execution order
taskRoot.serialSubTasks = True  # True = Sequential execution
```

### Submitting the Job

After setting up tasks, they are added to the job and submitted:

```python
job.addChild(taskMaya)
job.addChild(taskNuke)
job.addChild(taskCustom)
job.addChild(taskRoot)
```

In CLI mode, the job is submitted using:

```python
job.submit()
```
