import ollama


def get_response(user_input):
    stream = ollama.chat(
        model='onecern',
        messages=[
            {'role': 'system', 'content': "You are the Singapore QP's Board of Architect expert, the person is sitting for the QP examination, please help with finding the references and stuff needed for the exam"},
            {'role': 'user', 'content': user_input}
        ],
        stream=True,
    )
    for chunk in stream:
        yield chunk['message']['content']