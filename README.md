Hawat
===

- Conversational agent with long and short-term memory, run only on personal infrastructure, to provide effective advice and assistance to the user.
- A conversation partner that remembers previous conversations.

Plan Outline
---
- Python CLI FE (initial)
    - Or Golang for fun?
    - Would need to replace with gui at some point
- Python BE Controller
    - gRPC
        - Receive messages from FE
        - Pass responses back to FE
    - Store conversations
    - Process Messages
        - Summarize conversations
        - Summarize statements
        - Develop important facts
        - Named-Entity and Keyword recognition
        - Conversation and statement times
        - Recognize Conversation changes
    - Manage multiple resolutions of memory within and between conversations
    - Use convos and metadata to explore connections between concepts
    - "Reflection" between convos to do the summarizations and connections
    - Trigger new conversations at relevant points
- Interchangeable, self-hosted LLM service via OpenAI API
    - Grab something 'abliterated' from Hugging Face
    - Probably run it with LM Studio
- Self-hosted embeddings model
    - Need to pick one and stick with it
    - Design DB to support migrating embedding generator
- Interchangeable, self-hosted vector DB
    - Honestly? Just Postgres
- Extensions
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
