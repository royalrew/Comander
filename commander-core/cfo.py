import os
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

# Exception for exceeding financial caps
class TokenLimitExceeded(Exception):
    """Raised when the daily API token spend limit is exceeded."""
    pass

class CFOController:
    """
    Chief Financial Officer (CFO) module. 
    Responsible for tracking API spend and Stripe revenue.
    Implements API circuit breakers to prevent budget overruns.
    """
    def __init__(self):
        self.max_daily_spend = float(os.getenv("MAX_DAILY_API_SPEND_USD", "2.00"))
        self.current_daily_spend = 0.0
        
        # Stripe integration placeholders
        self.stripe_secret_key = os.getenv("STRIPE_SECRET_KEY")
        
    def add_cost(self, cost_usd: float) -> None:
        """
        Adds to the daily spend and checks against the circuit breaker.
        Raises TokenLimitExceeded if the limit is breached.
        """
        self.current_daily_spend += cost_usd
        if self.current_daily_spend > self.max_daily_spend:
            # Raise an alarm. In reality, we'd log this and send a Telegram alert before crashing out.
            raise TokenLimitExceeded(
                f"CIRCUIT BREAKER SECURE: Daily spend limit of ${self.max_daily_spend:.2f} exceeded. "
                f"Current spend: ${self.current_daily_spend:.2f}"
            )

    def get_financial_summary(self) -> str:
        """
        Returns a formatted financial summary for the Telegram Morning Briefing.
        """
        return (
            f"💰 **Financial Summary**\n"
            f"• Daily API Spend: ${self.current_daily_spend:.2f} / ${self.max_daily_spend:.2f}\n"
            f"• Revenue (Stripe): $0.00 (Pending implementation)\n"
        )
        
    def estimate_cost(self, prompt_tokens: int, completion_tokens: int, model: str) -> float:
        """
        Estimates cost based on token counts and model pricing. 
        Note: True cost should ideally be parsed from the LiteLLM response directly.
        """
        # Placeholder pricing logic (in reality, LiteLLM handles this or we maintain a pricing map)
        pricing_map = {
            "gpt-4o": {"input": 0.005 / 1000, "output": 0.015 / 1000},
            "deepseek-coder": {"input": 0.00014 / 1000, "output": 0.00028 / 1000},
            "llama3": {"input": 0.0, "output": 0.0}, # Local model = $0
        }
        
        rates = pricing_map.get(model, {"input": 0.01 / 1000, "output": 0.03 / 1000}) # Fallback safe rates
        cost = (prompt_tokens * rates["input"]) + (completion_tokens * rates["output"])
        
        return cost

# Global singleton
cfo = CFOController()
