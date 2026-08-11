from transformers import AutoTokenizer, AutoModelForCausalLM

model_name = "Vikhrmodels/Vikhr-Qwen-2.5-0.5b-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# Используем официальный шаблон чата
messages = [
    {"role": "user", "content": "Напиши одно короткое воодушевляющее предложение повару для приготовления пасты карбонара."}
]
text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
inputs = tokenizer(text, return_tensors="pt")

outputs = model.generate(
    **inputs,
    max_new_tokens=30,
    do_sample=True,
    temperature=0.4,
    top_p=0.9,
)

response = tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
print(f"Ответ: {response}")