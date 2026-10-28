---
layout: post
title:  "„We have contact!“"
date:   2026-10-21 11:32:00 +0200
categories: blog
---

openESHER in it's core is a chat system. It is all about getting in contact with a large language model. 
It's about sending prompt messages, and getting back the responses. 
Not more, but also not less. With Python and the Ollama API, getting started was surprisingly simple. 

The first iteration is a classical "Hello world!". After the necessary [preparations]({% link preparations.md %}), it is just a few lines of code:

```python
import ollama

response = ollama.chat(
    model="mistral:latest",
    messages=[{"role": "user", "content": "Say hello"}],
)
print(response.message.content)
```

Before you can run this snippet, you need to install the `ollama` library into your Python environment. 
(How to get started with the Python environment and Ollama will be added soon!)
That is the only dependency, so far. You can install the library with: 

```bash
python3 -m pip install -U ollama
```

Maybe you need to install the library not globally, but into a [virtual environment](https://docs.python.org/3/library/venv.html). 

After that, you are ready to paste the code above into a file, e.g., named `my_chat.py`, and to start your conversation with Ollama: 

```bash
python3 my_chat.py
```

You will see: The model will answer! 

Now, change the example above to some real question, and run it again, e.g.: 

```python
import ollama

response = ollama.chat(
    model="mistral:latest",
    messages=[{"role": "user", "content": "How can I create an AI agent with Python and Ollama?"}],
)
print(response.message.content)
```

Of course this is a little bit short for a real communication. The next step will be to stay in touch with the model, i.e., 
to stay in a *loop* where you can exchange a series of messages and responses with the model – a real conversation!