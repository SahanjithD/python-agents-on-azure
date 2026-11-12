# py-demo-agent: the HR assistant from bal-demo-agent, rebuilt on Microsoft Agent Framework.
# Structure follows foundry-samples/samples/python/hosted-agents/agent-framework/responses/02-tools.
# Two of the six Ballerina tools are ported (getLeaveBalance, getCompanyHolidays) to compare like for like.

import os
from typing import Annotated

from agent_framework import Agent, tool
from agent_framework.foundry import FoundryChatClient
from agent_framework_foundry_hosting import ResponsesHostServer
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv
from pydantic import Field

load_dotenv()

# Mock data, same values as hr_agent/data.bal
LEAVE_BALANCES = {
    "E1001": {"annual": 14, "sick": 7, "casual": 7},
    "E1002": {"annual": 10, "sick": 7, "casual": 5},
    "E1003": {"annual": 18, "sick": 7, "casual": 7},
    "E1004": {"annual": 20, "sick": 7, "casual": 7},
}
HOLIDAYS = [
    {"date": "2026-01-01", "name": "New Year's Day"},
    {"date": "2026-04-13", "name": "Sinhala and Tamil New Year's Eve"},
    {"date": "2026-04-14", "name": "Sinhala and Tamil New Year's Day"},
    {"date": "2026-05-01", "name": "Labour Day"},
    {"date": "2026-12-25", "name": "Christmas Day"},
    {"date": "2027-01-01", "name": "New Year's Day"},
]


@tool(approval_mode="never_require")
def get_leave_balance(
    employee_id: Annotated[str, Field(description="The employee ID, e.g. E1001")],
) -> dict:
    """Gets an employee's remaining leave balance in days for each leave type."""
    balance = LEAVE_BALANCES.get(employee_id)
    if balance is None:
        raise ValueError(f"No leave balance found for employee {employee_id}")
    return balance


@tool(approval_mode="never_require")
def get_company_holidays() -> list[dict]:
    """Lists the company's public holidays."""
    return HOLIDAYS


INSTRUCTIONS = """You are an HR Assistant. You help employees with HR questions: their leave balances and
public holidays.

- Always use the tools to look up data. Never invent employee details or balances.
- If the user hasn't given their employee ID, ask for it before looking up personal data.
- Keep answers short and friendly."""


def main():
    client = FoundryChatClient(
        project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
        model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
        credential=DefaultAzureCredential(),  # keyless: az login locally, agent identity in Foundry
    )

    agent = Agent(
        client=client,
        name="py-demo-agent",
        instructions=INSTRUCTIONS,
        tools=[get_leave_balance, get_company_holidays],
        # The host keeps the conversation history, so the model service doesn't need to store it too.
        default_options={"store": False},
    )
    ResponsesHostServer(agent).run()


if __name__ == "__main__":
    main()
