Hawat
===

- Conversational agent with long and short-term memory, run only on personal infrastructure, to provide effective advice and assistance to the user.
- A conversation partner that remembers previous conversations.

How to run
---
Coming eventually

Plan Outline
---
- Python CLI FE (initial)
    - ~~Or Golang for fun?~~
    - Would need to replace with gui at some point
- Python BE Controller
    - [x] gRPC
        - [x] Receive messages from FE
        - [x] Pass responses back to FE
        - [ ] Make it async
        - [ ] Use a stream?
    - [x] Store conversations
        - [x] Store outgoing messages
        - [x] Store incoming messages
    - Process Messages
        - [x] Summarize conversations
        - [ ] Summarize statements
        - [ ] Develop important facts
        - [ ] Named-Entity and Keyword recognition
        - [x] Conversation and statement times
        - [ ] Recognize Conversation changes
    - Manage multiple resolutions of memory within and between conversations
    - Use convos and metadata to explore connections between concepts
    - [ ] "Reflection" between convos to do the summarizations and connections
    - Trigger new conversations at relevant points
- [ ] Interchangeable, self-hosted LLM service via OpenAI API
    - [ ] Interchangeable LLM service via OpenAI API
    - Grab something 'abliterated' from Hugging Face
    - Probably run it with LM Studio
- [x] Self-hosted embeddings model
    - ~~Need to pick one and stick with it~~
    - [ ] Design DB to support migrating embedding generator
        - Nothing to this one with just need a script to recalculate all vector embeddings
- ~~Interchangeable, self-hosted vector DB~~
    - [x] Honestly? Just Postgres
- Extensions (some day)
    - TTS
    - STT
    - Tools
        - Image Recog
        - OCR
        - Image Gen
        - Calendaring
        - Write and execute code for technical answers
        - Weather
        - Web search

FYI
---
To regenerate the `.py` files in `hawat.proto`, go to the repo root and execute:
```
poetry run python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. hawat/proto/chat.proto
```
