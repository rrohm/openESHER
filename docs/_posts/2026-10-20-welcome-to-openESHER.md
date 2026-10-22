---
layout: post
title:  "Welcome to openESHER!"
date:   2026-10-20 09:30:57 +0200
categories: jekyll update
---

Let's get started with the first iteration! 

openESHER in it's core is a chat system, not more. But also not less.
With Python and Ollama, this was surprisingly simple. Not more than the classical "Hello world!":

```python
import ollama

response = ollama.chat(
    model="llama3.1",
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

Of course this is a little bit short for a real communication. The next step will be to stay in touch with the model, i.e., 
to stay in a *loop* where you can exchange a series of messages and responses with the model – a real conversation!
