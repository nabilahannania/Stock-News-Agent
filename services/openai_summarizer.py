from llm import client


def summarize_text(title: str, content: str, company: str, ticker: str):

    if not content:
        return ""

    prompt = f"""
Summarize the following financial news article in 2-3 sentences.

Focus ONLY on information related to {company} ({ticker}).
Ignore information about other companies if present.

Title: {title}

Article:
{content[:6000]}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You summarize financial market news accurately and concisely.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )

    summary = response.choices[0].message.content.strip()

    return summary
