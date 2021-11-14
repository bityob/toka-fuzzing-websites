import asyncio
from asyncclick.testing import CliRunner

from app.command_line import service_commmand
from app.utils import urls_and_responses, Url


async def call_cli_runner():
    runner = CliRunner()
    result = await runner.invoke(
        service_commmand, ["--url", "https://www.example.com"]
    )
    return result


async def test_service_command():
    asyncio.create_task(call_cli_runner())

    await asyncio.sleep(3)

    assert len(urls_and_responses) == 1
    response = urls_and_responses[Url(url="https://www.example.com")]
    assert response is not None
    assert response.request_info.headers["User-Agent"]
