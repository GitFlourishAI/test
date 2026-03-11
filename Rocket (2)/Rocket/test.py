from openai import OpenAI
import os
import json
import asyncio
from typing import List
from openai.types.shared.reasoning import Reasoning
from pydantic import BaseModel
from agents import Agent, ModelSettings, Runner, model_settings, set_default_openai_client, function_tool, AgentOutputSchema
from openai import AsyncOpenAI
from scripts import get_db
with open('scoring', 'r') as f:
    scoring_guide = f.read()
with open('company_details', 'r') as c:
    company_detail = c.read()
from signal123 import SQL
from rag_main import vectordb
from ok import fetch_company_financials, fetch_company_financials_tool
from ok2 import income_statement
import uuid
from datetime import datetime

data = vectordb()
print(data)

SECTOR_MAP = {
    "Technology": "38c26eb7-edc1-4ce0-bbd9-dc7a4824773d",
    "Financials": "090ab22a-5e88-44d4-bae0-cef8c45ea840",
    "Consumer Discretionary": "73204079-d59f-4528-b09a-62ad48446cfd",
    "Industrials": "04b93d80-df81-4712-a666-5adc30673b09",
    "Healthcare": "934f977d-5db6-46c2-b625-52e1b5e33101",
    "Energy": "a2f9f4dd-6f47-4601-9602-b32e0c7e2b54",
}
SHOCK_TO_SOURCE = {
    "Regulatory": "policy",
    "Policy Tailwind": "policy",
    "Monetary Policy": "macro",
    "Currency Shock": "macro",
    "Demand Shock": "commodity",
    "Supply Shock": "commodity",
    "Competition": "sector_news",
}


async_client = AsyncOpenAI(

    api_key = os.environ.get("AI_INTEGRATIONS_OPENAI_API_KEY")

    , base_url=os.environ.get("AI_INTEGRATIONS_OPENAI_BASE_URL")
)

set_default_openai_client(async_client)

# Get the raw data from database
raw_data = SQL()

# Convert to a readable string for the AI agent
if raw_data:
    user_input = f"""
    Event Data:
    - Time: {raw_data[0]}
    - Current Exchange Rate: {raw_data[2]}
    - Exchange Rate Last Month: {raw_data[3]}
    - Change Percentage: {raw_data[4]}
    - Is Significant: {raw_data[5]}
    - Mechanism: {raw_data[6]}
    - Sector: Mining
    """
else:
    user_input = "No recent data available"

print(user_input)


client = OpenAI(api_key = os.environ.get("AI_INTEGRATIONS_OPENAI_API_KEY")
, base_url= os.environ.get("AI_INTEGRATIONS_OPENAI_BASE_URL")             )


@function_tool

def impact_magnitude(financial_impact:float, confidence_level:float) -> str:

    impact_score = float(financial_impact)/float(confidence_level)

    return f"{impact_score}"



class ReasoningOutput(BaseModel):
    sector: str
    mechanism: List[str] = []
    time_horizon: str
    shock_type: str

class ReasoningList(BaseModel):
    reasoning_list: List[ReasoningOutput]



class VerificationOutput(BaseModel):
    mechanism: List[str] = []
    causal_soundness: int
    directional_consistency: int
    time_horizon_alignment: int
    magnitude_plausibility: int
    confidence_calibration: int
    empirical_anchoring: int
    justification: str
    verdict: str  # "Signal", "Flag", or "Reject"
    composite_score: int

class verificationlist(BaseModel):
    verification_list: List[VerificationOutput]

class revised_reasoning_List(BaseModel):
    mechanism: List[str] = []
    time_horizon: str
    shock_type: str
    sector: str

class CompanyTraitTransmission(BaseModel):

    sector: str
    shock_type: str
    time_horizon: str
    transmission_channel: List[str] = []
    originating_mechanisms: str
    exposed_traits: List[str]
    impacted_line_items: List[str]
    direction: str  # "positive", "negative", "mixed"
    sensitivity: str  # "Low", "Medium", "High"


class CompanyTraitsList(BaseModel):
    company_traits_list: List[CompanyTraitTransmission]

class TickerExposureMatch(BaseModel):

    Ticker: str
    trait_match_score: float  # normalized 0.0–1.0
    exposure_strength: str  # "High" | "Medium" | "Low"
    matched_traits: List[str]
    unmatched_traits: List[str]
    impacted_line_items: List[str]
    direction: str

class TickerBindingOutput(BaseModel):
    sector: str
    shock_type: str
    time_horizon: str
    transmission_channel: str
    bindings: List[TickerExposureMatch]

class TickerBindingList(BaseModel):
    ticker_binding_list: List[TickerBindingOutput]

class revisedBindingList(BaseModel):
    
    Ticker: str
    transmission_channel:str
    trait_match_score: float
    time_horizon: str
    shock_type: str
    sector: str


class calibrationoutput(BaseModel):
     ticker: str
     mechanism: str
     revenue_impact: float
     cost_impact: float
     ebitda_impact: float
     valuation_delta: float
     notes: str

class calibrationList(BaseModel):
    calibration_list:List[calibrationoutput]


class CatalystReport(BaseModel):
    
    sector: str
    shock_type: str
    time_horizon: str
    mechanism: str
    impact_magnitude: float
    ticker: str
    revenue_impact: float
    ebitda_impact: float
    valuation_delta: float
    

class CatalystList(BaseModel):
    catalyst_list:List[CatalystReport]

class revisedCatalystList(BaseModel):
    id: str
    title: str
    description: str
    sector_id: str
    source_type: str
    source_name: str
    source_url: str
    detected_at: str
    time_horizon: str
    confidence_score: float
    impact_magnitude: float
    impact_direction: str
    status: str
    shock_type:str
    evidence_summary: str
    ticker: str
    revenue_impact: float
    ebitda_impact: float
    valuation_delta: float



def revised_list(mechanism: List[str], time_horizon: str, shock_type: str, sector: str) -> revised_reasoning_List:

    return revised_reasoning_List(
mechanism = mechanism, sector = sector, time_horizon = time_horizon, shock_type = shock_type)

    


reason_agent = Agent(
name = "reason",
instructions = (
f"""
You are a financial market reasoning agent.
Your task is to infer price-impact mechanisms based on the provided event description ({user_input}), using historical scenario cases ({data}) as learning references.

Objective:
Generate multiple causal mechanism hypotheses explaining how the event could affect stock prices.

Instructions:

Produce up to 10 distinct mechanism chains, each written in the form:
Event → Intermediate Economic Effects → Firm-Level Financial Impact → Market Pricing Response

For each mechanism, explicitly specify:

Time horizon:  medium-term (1–3 months), or long-term (6–18 months)

Mechanism:
Event → X → Y → Price Impact

Sector: {user_input}

shock_type: regulatory, macro, technology, and consumer, etc.

time_horizon: 3M, 6M



"""

),
    output_type = ReasoningList,
    model_settings = ModelSettings(temperature= 0.56) 
)

verification_agent = Agent(
name = "verification",
instructions= (
f"""
You are a verification agent.

Your task is to evaluate the reasoning agent's outputs of each mechanism chain using the following criteria.{scoring_guide}

1. Causal soundness
2. Directional consistency
3. Time-horizon alignment
4. Magnitude plausibility
5. Confidence calibration
6. Empirical anchoring

Score each criterion from 0 to 5.

- Mechanism chain
- A table of scores
- A 2–3 sentence justification
"""
),

    output_type = verificationlist,
    model_settings = ModelSettings(
        temperature = 0.3
    )


)


company_traits_agent = Agent(
name = "company_traits",
instructions = (
"""

You are a Company Traits Transmission Agent in a multi-layer institutional investment system.

Your task is to convert verified sector-level mechanism chains into company-level transmission logic.

You must:

1. Identify the transmission channels across all provided mechanisms.
2. Translate each transmission channel into specific company traits that determine exposure.
3. Map each trait to affected financial line items.
4. Assign direction (positive/negative / mixed).
5. Assign qualitative sensitivity strength (Low / Medium / High).
6. Return structured JSON only.

You must NOT:
- Select tickers.
- Compute valuation impacts.
- Use numeric % estimates.
- Invent new macro shocks.
- Override provided mechanisms.

Think like a portfolio manager:
“What company characteristics determine whether this mechanism actually hits earnings?”

Your output must be structured, disciplined, and economically coherent.


"""

),

    output_type = CompanyTraitsList,
    model_settings = ModelSettings(
        temperature = 0.3
    )

)


company_match_agents = Agent(
name = "company_match",
instructions = (
"""

You are a Ticker Binding Agent in a multi-layer institutional investment system.

Your role is to match company trait exposure profiles to real publicly traded companies using structured exposure data.

This is a structural classification task, NOT a valuation task.

You must:

1. Read the transmission channel and exposed traits.
2. Use the provided structured company exposure data.
3. Evaluate how strongly each company matches the required traits.
4. Assign a normalized trait_match_score between 0.0 and 1.0.
5. Classify exposure strength:
   - High (≥ 0.75)
   - Medium (0.50–0.74)
   - Low (< 0.50)
6. Identify:
   - Fully matched traits
   - Unmatched traits
7. Identify the financial-line items driving the score.
8. Preserve original sector, shock_type, direction and time horizon.
9. Return structured JSON only.

Rules:

- Do NOT reinterpret macro mechanisms.
- Do NOT compute financial impact or valuation changes.
- Do NOT invent missing data.
- Do NOT modify trait definitions.
- Do NOT introduce new traits.
- Do NOT explain reasoning in prose.

If exposure data is insufficient, reduce match score.

This agent performs structural exposure matching only."""

),

    output_type = TickerBindingList,
    model_settings = ModelSettings(
        temperature = 0.15
    )

)




calibration_agent = Agent(
name = "calibration",
instructions = (
"""

You are the Calibration Agent in a financial catalyst analysis system.

Your task is to translate macroeconomic or sector catalysts into 
quantifiable financial impacts for publicly traded companies.

You receive:
1. A catalyst event
2. A mechanism describing how the event affects companies
3. A list of bound tickers and their exposure profiles

Your responsibilities:

Step 1 — Interpret the mechanism
Determine how the catalyst affects financial drivers such as:
- revenue
- operating costs
- capital expenditures
- commodity prices
- export competitiveness

Step 2 — Estimate sensitivities
Estimate the economic sensitivities that translate the mechanism 
into financial impacts.

Possible sensitivities include:
- revenue_delta_pct
- cost_delta_pct
- commodity_price_delta
- export_volume_delta
- operating_leverage

Step 3 — Call financial data tools
Retrieve company fundamentals using available tools.

Step 4 — Call the impact calculation tools
Use the tools to calculate:

valuation impact
ebitda impact
revenue impact


Rules:

- Never invent company financial data.
- Always retrieve fundamentals using tools.
- Never perform calculations manually if a tool exists.
- Always return structured JSON output.

"""

),

    output_type = calibrationList,
    tools= [income_statement],
    model_settings = ModelSettings(
        temperature = 0.1
    )

)


reporting_agent = Agent(
name = "reporting",
instructions = (
"""
You are a Reporting Agent for an institutional investment intelligence platform.

Your task:

1. Ingest the calibration agent's structured outputs.
2. Rank all valid catalysts by impact magnitude.
3. Select the top 5 catalysts.
4. Produce a concise, investor-ready ranked summary.

Rules:
- Do NOT invent new catalysts.
- Do NOT alter financial impact or confidence values.
- Prefer clarity, credibility, and decision-usefulness.
- Clearly indicate upside vs downside."""
),
    output_type = CatalystList,
    tools = [fetch_company_financials_tool],
    model_settings = ModelSettings(temperature=0.2)
)

async def think_then_answer_then_reflect(user_input: str) -> List[revisedCatalystList]:

    reasoning_result = await Runner.run(reason_agent, user_input)

    prompt_verification = f""" Please reflect on the reasoning agents'answers{reasoning_result.final_output} and score using the scoring guide.

    For each mechanism, provide a score and a justification.
    """


    verification_result = await Runner.run(verification_agent, prompt_verification)


    verified_list = verification_result.final_output.verification_list
    filtered = [v for v in verified_list if v.composite_score >= 20]
    ranked = sorted(filtered, key = lambda v:v.composite_score, reverse = True)
    print(ranked)
    print(reasoning_result.final_output.reasoning_list)

    # Build a lookup dictionary: mechanism key → reasoning output
    reasoning_lookup = {
        tuple(r.mechanism): r
        for r in reasoning_result.final_output.reasoning_list
    }

    # Now map each ranked verification to its matching reasoning data
    revised = [
        revised_list(
            mechanism=v.mechanism,
            time_horizon=reasoning_lookup[tuple(v.mechanism)].time_horizon,
            shock_type=reasoning_lookup[tuple(v.mechanism)].shock_type,
            sector=reasoning_lookup[tuple(v.mechanism)].sector
        )
        for v in ranked
        if tuple(v.mechanism) in reasoning_lookup
    ]
    print(revised)

    revised_json = json.dumps([r.model_dump() for r in revised], indent =2)

    prompt_company_traits = f"""

INPUT: Revised Sector-Level Mechanisms

({revised_json})

Instructions:

For each channel, output:

   - Keep original sector, shock type, and time horizon
   - Define exposed company traits.
   - Identify impacted financial line items.
   - Assign direction.
   - Assign qualitative sensitivity (Low/Medium/High).
   - Keep original time horizon.

"""

    company_trait_result = await Runner.run(company_traits_agent, prompt_company_traits)


    prompt_matching = f"""
    
    INPUT:

Company Trait Transmission Output:
{company_trait_result.final_output}

Company Exposure Database:
{company_detail}

Instructions:

For each transmission channel:
1. Evaluate each company’s structural exposure using provided exposure variables.
2. Compute a normalized trait match score.
3. Return structured JSON only."""

    matching_result = await Runner.run(company_match_agents,prompt_matching)



    verified_list2 = matching_result.final_output.ticker_binding_list

    filtered2 = []
    for channel in verified_list2:
        good_bindings = [b for b in channel.bindings if b.trait_match_score >= 0.6]
        if good_bindings:
            channel.bindings = good_bindings
            filtered2.append(channel)

    for channel in filtered2:
        channel.bindings.sort(key=lambda b: b.trait_match_score, reverse=True)

    tickers_to_calibrate = []
    for channel in filtered2:
        for b in channel.bindings:
            tickers_to_calibrate.append(b.Ticker)

    # Deduplicate
    tickers_to_calibrate = list(set(tickers_to_calibrate))

    

    channels_json = json.dumps([c.model_dump() for c in filtered2], indent=2)

    print(channels_json)
    
    prompt_calibration = f"""
You are the Calibration Agent.

Your task is to estimate the ticker impact line items' actual financial impact using real financial data.

Tickers to calibrate:{tickers_to_calibrate}

Transmission Channels:{channels_json}


MODELING REQUIREMENTS

For each company:

1. Keep the original mechanism
2. Fetch financial data using tools
3. Calculate revenue impact, ebitda impact, and valuation impact
4. Add a brief note


CONSTRAINTS


- Do NOT fabricate financial data.
- If required data is unavailable, return data_gap = True.
- Output structured JSON only.


        """

    
    calibration_result = await Runner.run(calibration_agent,prompt_calibration)

    prompt_reporting = f"""

Calibration Agent Output (Financial Impact)
{calibration_result.final_output}

Based on the above outputs, identify the top catalysts that meet the verification thresholds, rank them by impact magnitude, and provide up to 5 ranked catalysts. Keep the original information (Mechanism, Ticker, revenue_impact, valuation_delta, etc.) from the calibration agent.
"""

    reporting_result = await Runner.run(reporting_agent, prompt_reporting)

    revised_catalyst = [ 
        revisedCatalystList(
            id=str(uuid.uuid4()),
            title=f"{c.mechanism} in {c.sector} sector",
            description=f"{c.mechanism} in {c.sector} sector",
            sector_id=SECTOR_MAP.get(c.sector, "04b93d80-df81-4712-a666-5adc30673b09"),
            source_type=SHOCK_TO_SOURCE.get(c.shock_type, "macro"),
            source_name="Alpha Vantage",
            source_url=f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={c.ticker}",
            detected_at=datetime.now().isoformat(),
            time_horizon=c.time_horizon,
            confidence_score=50.0,
            impact_magnitude=c.impact_magnitude,
            impact_direction="positive" if c.valuation_delta > 0 else "negative",
            status="active",
            shock_type=c.shock_type,
            evidence_summary=f"{c.mechanism} in {c.sector} sector",
            ticker=c.ticker,
            revenue_impact=c.revenue_impact,
            ebitda_impact=c.ebitda_impact,
            valuation_delta=c.valuation_delta
        )
        for c in reporting_result.final_output.catalyst_list
    ]
    

    print(company_trait_result.final_output,
        matching_result.final_output, calibration_result.final_output)
    
    return revised_catalyst

async def main():

    result = await think_then_answer_then_reflect(user_input)

    print(result)


asyncio.run(main())
