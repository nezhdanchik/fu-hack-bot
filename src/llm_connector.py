import logging
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from prompts import INTERVIEW_PROMPT, FINAL_PROMPT, CHECK_COMPLETENESS_PROMPT

logger = logging.getLogger(__name__)

vllm_api_base = "https://51.250.28.28:10000/gpb_gpt_hack_2025/v1"


def get_llm_model(temperature: float = 0.7,
                  max_tokens: int = 512) -> ChatOpenAI:
    return ChatOpenAI(
        model="leon-se/gemma-3-27b-it-FP8-Dynamic",
        openai_api_base=vllm_api_base,
        openai_api_key="EMPTY",
        temperature=temperature,
        max_tokens=max_tokens,
    )


class LLMConnector:
    def __init__(self):
        self.history = [SystemMessage(content=INTERVIEW_PROMPT)]

    async def send_user_message(self,remaining_count: int) -> str:
        """Отправка сообщения кандидата llm"""
        remaining_count_instruction = SystemMessage(
            content=f"(Осталось {remaining_count} сообщений для уточнения профиля.)"
        )
        llm = get_llm_model()
        response = await llm.ainvoke(self.history + [remaining_count_instruction])
        logger.info(f"AI ответ: {response.content}")
        return response.content


    async def evaluate_candidate(self) -> str:
        """Финальная оценка кандидата."""
        final_instruction = SystemMessage(content=FINAL_PROMPT)
        llm = get_llm_model(temperature=0.0, max_tokens=20)
        response = await llm.ainvoke(self.history + [final_instruction])
        logger.info(f"Оценка AI: {response.content}")
        return response.content


    async def is_info_enough(self) -> bool:
        """Проверка: достаточно ли данных для оценки роли кандидата."""
        llm = get_llm_model(temperature=0.0, max_tokens=20)
        check_prompt = SystemMessage(content=CHECK_COMPLETENESS_PROMPT)
        response = await llm.ainvoke(self.history + [check_prompt])
        answer = response.content.strip().lower()
        logger.info(f"Промежуточная оценка: {answer}")
        return answer == "[достаточно]"


    async def process(
            self,
            user_message: str,
            remaining_count: int,
            current_count: int
    ) -> (str, bool):
        self.history.append(HumanMessage(content=user_message))
        logger.info(
            f"Получено сообщение от пользователя: {user_message}. Осталось сообщений: {remaining_count}"
        )

        if remaining_count >= 1:

            if current_count > 3 and await self.is_info_enough():
                logger.info("Информации достаточно — досрочная финальная оценка")
                final_result = await self.evaluate_candidate()
                return final_result, True

            response_message = await self.send_user_message(remaining_count)
            self.history.append(AIMessage(content=response_message))
            return response_message, False
        return await self.evaluate_candidate(), True
