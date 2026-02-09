import time
from dataclasses import dataclass


GPT4O_MINI_INPUT_PER_MILLION = 0.15
GPT4O_MINI_OUTPUT_PER_MILLION = 0.60


@dataclass
class TokenUsage:
    """
    Simple container for token usage and timing.

    This does NOT talk to the OpenAI API directly – it assumes you pass in
    the token counts you get back from the API / LangChain, and it will
    calculate cost and format a small report.
    """

    model_name: str
    input_tokens: int
    output_tokens: int
    elapsed_seconds: float

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens

    @property
    def input_cost_usd(self) -> float:
        if self.model_name == "gpt-4o-mini":
            return (self.input_tokens / 1_000_000) * GPT4O_MINI_INPUT_PER_MILLION
        return 0.0

    @property
    def output_cost_usd(self) -> float:
        if self.model_name == "gpt-4o-mini":
            return (self.output_tokens / 1_000_000) * GPT4O_MINI_OUTPUT_PER_MILLION
        return 0.0

    @property
    def total_cost_usd(self) -> float:
        return self.input_cost_usd + self.output_cost_usd

    def as_dict(self) -> dict:
        return {
            "model_name": self.model_name,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
            "elapsed_seconds": self.elapsed_seconds,
            "input_cost_usd": round(self.input_cost_usd, 6),
            "output_cost_usd": round(self.output_cost_usd, 6),
            "total_cost_usd": round(self.total_cost_usd, 6),
        }

    def pretty_print(self) -> None:
        data = self.as_dict()
        print("\n=== Token usage ===")
        print(f"Model:          {data['model_name']}")
        print(f"Input tokens:   {data['input_tokens']}")
        print(f"Output tokens:  {data['output_tokens']}")
        print(f"Total tokens:   {data['total_tokens']}")
        print(f"Time (seconds): {data['elapsed_seconds']:.2f}")
        print("\n=== Estimated cost (USD) ===")
        print(f"Input cost:     ${data['input_cost_usd']:.6f}")
        print(f"Output cost:    ${data['output_cost_usd']:.6f}")
        print(f"Total cost:     ${data['total_cost_usd']:.6f}")


def time_call(fn, *args, **kwargs):
    """
    Helper to measure how long a function call takes.

    Returns (result, elapsed_seconds).
    """
    start = time.perf_counter()
    result = fn(*args, **kwargs)
    elapsed = time.perf_counter() - start
    return result, elapsed