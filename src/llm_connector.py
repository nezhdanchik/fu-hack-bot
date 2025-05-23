import logging
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from prompts import INTERVIEW_PROMPT, FINAL_PROMPT

logger = logging.getLogger(__name__)

vllm_api_base = "https://51.250.28.28:10000/gpb_gpt_hack_2025/v1"

llm = ChatOpenAI(
    model="leon-se/gemma-3-27b-it-FP8-Dynamic",
    openai_api_base=vllm_api_base,
    openai_api_key="EMPTY",
    temperature=0.7,
    max_tokens=512,
)

ERROR_MESSAGE = "Извините, я сейчас не могу говорить, давайте свяжемся позже."

history = [SystemMessage(content=INTERVIEW_PROMPT)]


async def send_user_message(prompt: str, remaining_count: int) -> str:
    """Отправка сообщения кандидата llm"""
    combined_prompt = f"{prompt}\n\n(Осталось {remaining_count} сообщений для уточнения профиля.)"
    logger.info(f"Сообщение пользователя: {combined_prompt}")

    history.append(HumanMessage(content=combined_prompt))

    try:
        response = await llm.ainvoke(history)
        logger.info(f"AI response: {response.content}")
        history.append(AIMessage(content=response.content))
        return response.content
    except Exception as e:
        logger.exception("Ошибка при запросе к LLM")
        return ERROR_MESSAGE


async def evaluate_candidate(prompt: str) -> str:
    """Финальная оценка кандидата."""
    logger.info("Финальная оценка кандидата началась")

    history.append(HumanMessage(content=prompt))
    final_instruction = SystemMessage(content=FINAL_PROMPT)

    try:
        response = await llm.ainvoke(history + [final_instruction])
        logger.info(f"Оценка завершена. Результат: {response.content}")
        return response.content
    except Exception as e:
        logger.exception("Ошибка при финальной оценке")
        return ERROR_MESSAGE
