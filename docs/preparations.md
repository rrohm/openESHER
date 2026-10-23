---
layout: page
title: Preparations
permalink: /preparations/
---
# Preparations

openESHER is build with the goal to get started easily, and to minimize dependencies. You need: 

1. Ollama as a LMM runtime
2. A model 
3. A Python environment




## Installing Ollama

Installing Ollama normally is quite simple, following the instructions on the Ollama homepage 
(see. [https://ollama.com/download](https://ollama.com/download){:target="_blank"}, for Linux, macOs or Windows). 
Usually you will install from a terminal window. For macOS and MS Windows, there are installer packages, too.

After successful installation, you should be able to verify if Ollama is running in several ways: 

1. With you browser: Request the address `http://localhost:11434/`. If Ollama is running, it should answer accordingly: You should see `Ollama is running` in your browser. 
2. In your terminal: Enter 'ollama --version' and hit `RETURN`. Ollama should answer with a version number, e.g., like that: `ollama version is 0.40.2`.

If Ollama is not yet running, you can open a terminal and enter: 

```console
$ ollama serve
```

After that, repeating the first test described above should show Ollama running.