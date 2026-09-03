import os
import ollama

MODEL_NAME = "gemma4:e4b-it-q4_K_M"  # или ваша модель

def read_markdown_prompt(file_path):
    """Считывает содержимое .md файла"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Файл не найден: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def load_all_stratagems(stratagems_dir="prompts/stratagems"):
    """Загружает все файлы стратагем из папки и возвращает их объединённое описание"""
    if not os.path.exists(stratagems_dir):
        return ""  # если папки нет, просто игнорируем
    descriptions = []
    for filename in sorted(os.listdir(stratagems_dir)):
        if filename.endswith(".md"):
            path = os.path.join(stratagems_dir, filename)
            try:
                content = read_markdown_prompt(path)
                descriptions.append(content.strip())
            except Exception as e:
                print(f"⚠️ Не удалось загрузить {filename}: {e}")
    return "\n\n".join(descriptions)

def start_simulation():
    # Загружаем кейс и стратагемы
    try:
        case_prompt = read_markdown_prompt("prompts/cases/case_01.md")
        stratagems_text = load_all_stratagems()
        judge_prompt = read_markdown_prompt("prompts/judge_analyst.md")
    except FileNotFoundError as e:
        print(f"❌ Ошибка инициализации: {e}")
        return

    # Формируем системный промпт для оппонента
    opponent_system = case_prompt
    if stratagems_text:
        opponent_system += "\n\n## Доступные стратагемы (ты можешь применять их по ситуации, но не называй их игроку)\n"
        opponent_system += stratagems_text
        opponent_system += "\n\nТы должен анализировать ход переговоров и в любой момент переключаться между стратагемами, выбирая наиболее эффективную для достижения своей цели."

    print("═══ СИМУЛЯТОР СТРАТАГЕМ: НАЧАЛО ПЕРЕГОВОРОВ ═══")
    print("Контекст: Вы – поставщик, ведёте переговоры с крупным ритейлером.")
    print("Ваша задача – заключить контракт на выгодных условиях.\n")

    dialogue_history = [{"role": "system", "content": opponent_system}]

    # Стартовая реплика
    dialogue_history.append({"role": "user", "content": "Приветствую. Давайте обсудим условия поставки."})
    response = ollama.chat(model=MODEL_NAME, messages=dialogue_history)
    first_response = response['message']['content']
    print(f"🤖 Оппонент: {first_response}\n")
    dialogue_history.append({"role": "assistant", "content": first_response})

    # Основной цикл (4 раунда)
    for round_num in range(1, 5):
        user_input = input(f"👤 Вы (Раунд {round_num}/4): ")
        if user_input.lower() in ['exit', 'quit', 'выход']:
            break

        # Обработка команды /guess
        if user_input.lower().startswith("/guess"):
            parts = user_input.split()
            if len(parts) > 1:
                guessed_num = parts[1]
                # Отправляем судье запрос на проверку догадки (можно реализовать отдельно)
                print("🔍 Вы попытались угадать стратагему. Судья проверит это в финальном отчёте.")
                # Здесь можно сразу дать фидбек через судью, но для простоты оставим в конце.
            else:
                print("Укажите номер стратагемы, например: /guess 5")
            continue

        dialogue_history.append({"role": "user", "content": user_input})

        # Ответ оппонента
        response = ollama.chat(model=MODEL_NAME, messages=dialogue_history)
        opponent_response = response['message']['content']
        print(f"\n🤖 Оппонент: {opponent_response}\n")
        dialogue_history.append({"role": "assistant", "content": opponent_response})

    # Анализ судьи
    print("═══ ПЕРЕГОВОРЫ ЗАВЕРШЕНЫ. АНАЛИЗ СУДЬИ ═══\n")
    print("Идёт оценка ваших навыков...")

    clean_history = [m for m in dialogue_history if m["role"] != "system"]
    formatted_log = "\n".join([f"{'Игрок' if m['role']=='user' else 'Оппонент'}: {m['content']}" for m in clean_history])

    judge_messages = [
        {"role": "system", "content": judge_prompt},
        {"role": "user", "content": f"Вот лог переговоров:\n{formatted_log}"}
    ]
    judge_response = ollama.chat(model=MODEL_NAME, messages=judge_messages)
    print(judge_response['message']['content'])

if __name__ == "__main__":
    # Создаём необходимые папки, если их нет
    os.makedirs("prompts/cases", exist_ok=True)
    os.makedirs("prompts/stratagems", exist_ok=True)
    start_simulation()