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

(How to get started with the Python environment and Ollama will be added soon!)