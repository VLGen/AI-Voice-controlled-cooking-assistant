from uuid import uuid4

import gradio as gr


def new_thread_id() -> str:
    return str(uuid4())


def respond(
    message: str,
    history: list[dict[str, str]] | None,
    thread_id: str,
) -> tuple[str, list[dict[str, str]]]:
    message = message.strip()
    if not message:
        return "", history or []

    from src.agent.graph import app as agent

    result = agent.invoke(
        {
            "messages": [{"role": "user", "content": message}],
            "current_recipe_id": None,
            "current_step": None,
            "timer_end": None,
            "intent": "",
            "recipes": [],
        },
        config={"configurable": {"thread_id": thread_id}},
    )
    last_message = result["messages"][-1]
    if last_message.get("role") == "assistant":
        answer = last_message["content"]
    else:
        answer = (
            "Пока умею искать рецепты. Переформулируйте запрос, "
            "например: хочу приготовить борщ."
        )

    updated_history = list(history or [])
    updated_history.extend(
        [
            {"role": "user", "content": message},
            {"role": "assistant", "content": answer},
        ]
    )
    return "", updated_history


def clear_chat() -> tuple[str, list[dict[str, str]], str]:
    return "", [], new_thread_id()


def create_demo() -> gr.Blocks:
    with gr.Blocks(title="AI-повар") as demo:
        gr.Markdown("# AI-повар\nСпросите о рецепте или попросите помочь с приготовлением.")
        thread_id = gr.State(value=new_thread_id)
        chatbot = gr.Chatbot(
            label="История диалога",
            height=560,
            placeholder="Начните диалог с ассистентом",
        )
        with gr.Row():
            message = gr.Textbox(
                label="Сообщение",
                placeholder="Например: Хочу приготовить борщ",
                lines=2,
                scale=8,
            )
            send = gr.Button("Отправить", variant="primary", scale=1)
        clear = gr.Button("Очистить чат")

        inputs = [message, chatbot, thread_id]
        outputs = [message, chatbot]
        send.click(respond, inputs=inputs, outputs=outputs)
        message.submit(respond, inputs=inputs, outputs=outputs)
        clear.click(
            clear_chat,
            inputs=[],
            outputs=[message, chatbot, thread_id],
        )

    return demo


def main() -> None:
    create_demo().launch()


if __name__ == "__main__":
    main()
