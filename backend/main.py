import ollama


def get_response(user_input):
    stream = ollama.chat(
        model='onecern',
        messages=[{'role': 'user', 'content': user_input}],
        stream=True,
    )
    for chunk in stream:
        yield chunk['message']['content']
