import os
import ollama

MODEL_NAME = "gemma2"  # Локальная модель в Ollama

def read_markdown_prompt(file_path):
    """Считывает инструкции из md-файлов"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Файл промпта не найден: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def start_simulation():
    try:
        opponent_prompt = read_markdown_prompt("prompts/opponent_case_05.md")
        judge_prompt = read_markdown_prompt("prompts/judge_analyst.md")
    except FileNotFoundError as e:
        print(f"❌ Ошибка инициализации: {e}")
        return

    print("═══ СИМУЛЯТОР СТРАТАГЕМ: НАЧАЛО ПЕРЕГОВОРОВ ═══")
    print("Контекст: Вы продаете партию товара. Ваша компания в кризисе (кассовый разрыв, нужны деньги).")
    print("Перед вами директор по закупкам ритейлера. Ваша задача — подписать контракт.\n")
    
    # Инициализируем историю диалога с системным промптом
    dialogue_history = [{"role": "system", "content": opponent_prompt}]
    
    # Стартовый триггер диалога
    dialogue_history.append({"role": "user", "content": "Приветствую. Давайте обсудим контракт на поставку."})
    
    # Используем официальный метод ollama.chat
    response = ollama.chat(model=MODEL_NAME, messages=dialogue_history)
    first_icebreaker = response['message']['content']
    
    print(f"🤖 Оппонент: {first_icebreaker}\n")
    dialogue_history.append({"role": "assistant", "content": first_icebreaker})

    # 3 раунда переговоров
    for round_num in range(1, 4):
        user_input = input(f"👤 Вы (Раунд {round_num}/3): ")
        if user_input.lower() in ['exit', 'quit', 'выход']:
            break
            
        dialogue_history.append({"role": "user", "content": user_input})
        
        # Запрос к оппоненту через библиотеку ollama
        response = ollama.chat(model=MODEL_NAME, messages=dialogue_history)
        opponent_response = response['message']['content']
        
        print(f"\n🤖 Оппонент: {opponent_response}\n")
        dialogue_history.append({"role": "assistant", "content": opponent_response})

    print("═══ ПЕРЕГОВОРЫ ЗАВЕРШЕНЫ. АНАЛИЗ СУДЬИ ═══\n")
    print("Идет оценка ваших навыков взаимодействия...")
    
    # Формируем чистый лог для судьи (без системного промпта оппонента)
    clean_history = [m for m in dialogue_history if m["role"] != "system"]
    formatted_log = "\n".join([f"{'Игрок' if m['role']=='user' else 'Оппонент'}: {m['content']}" for m in clean_history])
    
    judge_messages = [
        {"role": "system", "content": judge_prompt},
        {"role": "user", "content": f"Вот лог переговоров:\n{formatted_log}"}
    ]
    
    # Запрос к судье через библиотеку ollama
    judge_response = ollama.chat(model=MODEL_NAME, messages=judge_messages)
    print(judge_response['message']['content'])

if __name__ == "__main__":
    os.makedirs("prompts", exist_ok=True)
    start_simulation()
