from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

vllm_api_base = "https://51.250.28.28:10000/gpb_gpt_hack_2025/v1"

llm = ChatOpenAI(
    model="leon-se/gemma-3-27b-it-FP8-Dynamic",
    openai_api_base=vllm_api_base,
    openai_api_key="EMPTY",
    temperature=0.7,
    max_tokens=512,
)

system_prompt = """
Ты — HR-бот на собеседовании. Твоя задача — за 10 сообщений собрать как можно больше информации о кандидате, чтобы понять его профессиональный профиль.

- Фокусируйся не на проверке знаний, а на получении фактов: кем работал, чем занимался, какие задачи решал, с кем и как взаимодействовал.
- Будь краток. Задавай конкретные и уточняющие вопросы — про опыт, роли, проекты, инструменты, сложности, типичные задачи. Используй каждый ход эффективно.
- Избегай общих или повторяющихся вопросов. Используй каждый ход максимально эффективно.
- Не делай выводов — просто выясняй максимум о человеке.

Возможные вопросы:
Какие задачи вы решали в последнем проекте?
Вы больше работаете с моделями, данными или процессами?
С какими инструментами или технологиями вы чаще всего работаете?
Какую роль вы обычно занимаете в команде?
Опишите типичную задачу, которую вы решали от начала до конца.
Вы разрабатывали или только использовали ML-модели?

Начни с приветствия и вопроса:  
«Здравствуйте! Расскажите, пожалуйста, кратко о своём опыте в IT или в смежных сферах».
"""

final_prompt = """
Интервью завершено. На основе этого диалога определи, к какой из ролей кандидат подходит больше всего, или напиши, что он некомпетентен.

Возможные ответы:
- [Data Scientist]
- [Data Engineer]
- [Data Analyst]
- [MLOps Engineer]
- [Project Manager]
- [Некомпетентный соискатель]

Проанализируй ответы, обрати внимание на конкретные технологии, опыт, типы задач, логику мышления и уровень детализации. Оцени, насколько кандидат соответствует требованиям по одной из ролей.
Если кандидат ведёт себя неадекватно, не может ответить на вопросы, обманывает или не имеет опыта в IT, напиши [Некомпетентный соискатель]

Ответь **только одной строкой** — выбери **один** из вариантов в квадратных скобках."""


history = [
    SystemMessage(content=system_prompt),
]

def get_middle_message(remaining_count: int) -> str:
    return f"У тебя осталось {remaining_count} сообщений чтобы лучше узнать кандидата. "

async def request_llm(prompt: str, remaining_count: int) -> str:
    hm = HumanMessage(content=prompt)
    print(f"User message: {hm.content}")
    history.append(hm)

    sm = SystemMessage(content=get_middle_message(remaining_count))
    print(f"System message: {sm.content}")
    history.append(sm)

    response = await llm.ainvoke(history)
    history.pop()

    am = AIMessage(content=response.content)
    print(f"AI message: {am.content}")
    history.append(am)

    return response.content

async def final_request_llm(prompt: str) -> str:
    hm = HumanMessage(content=prompt)
    print(f"User message: {hm.content}")
    history.append(hm)

    sm = SystemMessage(content=final_prompt)
    print(f"System message: {sm.content}")
    history.append(sm)

    response = await llm.ainvoke(history)
    return response.content