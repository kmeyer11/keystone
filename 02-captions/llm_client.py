import os
import subprocess
from dotenv import load_dotenv

load_dotenv()


def ask_claude(prompt, model="sonnet"):
    env = os.environ.copy()
    if not env.get("CLAUDE_CODE_OAUTH_TOKEN"):
        raise RuntimeError(
            "CLAUDE_CODE_OAUTH_TOKEN is not set — run `claude setup-token` once "
            "(uses your Claude Pro/Max plan, not paid API credits) and put the "
            "printed token in .env"
        )
    result = subprocess.run(
        ["claude", "-p", prompt, "--model", model, "--output-format", "text"],
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


if __name__ == "__main__":
    print(ask_claude("Reply with exactly: connection ok"))
