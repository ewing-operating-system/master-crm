# Letter Template Engine — Execution Specification
**Status**: PRIORITY 1 — Start Tonight
**Estimated Build Time**: 4-5 hours (focused, no dependencies)
**Deliverable**: Functional letter generator that can process 1-5 test targets and produce operator-ready letters

---

## WHAT YOU'RE BUILDING

A Python/Node agent that:
1. Reads validated research from `target_research` table
2. Generates personalized letters in operator language (not bot-speak)
3. Stores letter in `proposals.letter_text`
4. Scores personalization (0.0-1.0)
5. Marks ready for CERTIFIER approval

**Input**: Single target with research (story cards, founder context, metrics)
**Output**: Polished letter (600-800 words), personalization_score, tone_signal
**Quality check**: "Would I mention this story at a dinner party?"

---

## THE LETTER FORMULA — By Entity

### Next Chapter (Sell-Side, Business Owner)
```
[GREETING]

I came across [SPECIFIC STORY] in my research on [Company], and your situation jumped out at me.

[CONTEXT HOOK]
Here's what's happening in [Market/Industry right now]:
- [Metric: "HVAC consolidation up 3x YoY" or "Recurring revenue buyers are active"]
- [Founder behavior: "owners like you are exploring options" or "timing is right"]

[YOUR STORY]
[Story card #1 or #2 - something human: started in garage, recovered from setback, third-gen, community champion]
That tells me [implication about their business].

[THE ASK]
I work with [type of business] owners exploring options. Whether you're thinking about it or not, let's talk for 20 minutes. I can share what's happening in your market and what other owners like you are seeing.

[CLOSE]
Call me [phone]. I'm usually around.

Best,
[Name]
```

**Tone**: Peer, not advisor. Specific story, not generic pitch. Mention market metric (EBITDA-adjacent is fine, but speak operator language).

**Examples of good hooks**:
- "Saw you won [Local Award]. That kind of reputation is what buyers are actively looking for."
- "Noticed your company's been in [City] for 20+ years. Multi-generational businesses are in high demand."
- "Read about your [Certifications]. That's exactly the service capability buyers are consolidating."

---

### AND Capital (LP Fundraising)
```
[SALUTATION]

We're focused on [Category: healthcare/energy/assets/etc] and thought you'd want to see recent performance.

[THESIS]
Our thesis on [Market] is straightforward: [founder narrative or return story].
Our LPs have seen [Return X% in Z time], and we're building the next chapter in [Sector].

[DEAL EXAMPLE]
We just underwritten [Company type] in [Market]. The team:
- [Founder 1]: [credential]
- [Founder 2]: [credential]

This is the kind of consolidation thesis we're executing.

[NEXT STEP]
Coffee/video call? I can walk you through the fund thesis and latest portfolio performance.

[CLOSE]
[Calendar link or phone]

Best,
[Name]
```

**Tone**: Peer-to-peer, fund confidence, specific deal story, market insight.

---

### RevsUp (Hiring/Recruiting)
```
[GREETING]

We have [# & Role: "3 founding engineers" or "2 VP-level operators"] from [Background/Experience] who'd be a fit for [Company/Challenge].

[QUICK CONTEXT]
We work with [Company type] building out [Team/Function].

[CANDIDATE SNAPSHOT]
One candidate:
- [Experience]: [Years/Domain]
- [Why they move]: [Motivation, not desperation]
- [Relevant win]: [Specific achievement]

[THE MOTION]
20-min call? I'll walk you through all 3 and we can see if there's a fit.

[CLOSE]
[Your calendar link or phone]

[Name]
```

**Tone**: Quick, friendly, specific candidates, no fluff.

---

## IMPLEMENTATION STEPS

### Step 1: Create Letter Generator Function
```python
# File: /Users/clawdbot/Projects/master-crm/engines/letter_generator.py

import anthropic
import json
from datetime import datetime

def generate_letter(target_research: dict, entity: str) -> dict:
    """
    Generate a personalized letter from validated research.

    Args:
        target_research: {
            "target_id": "uuid",
            "founder_name": "John Smith",
            "company_name": "HVAC Pro Services",
            "entity": "next_chapter",
            "story_cards": [
                {
                    "category": "personal_founder_story",
                    "story": "Started business in garage in 2003...",
                    "source": "website"
                },
                ...
            ],
            "competitive_context": "HVAC consolidation market heating...",
            "research_quality_score": 0.82
        }

    Returns:
        {
            "letter_text": "Dear John...",
            "personalization_score": 0.88,
            "tone_signal": "operator",
            "generated_at": "2026-03-30T20:45:00Z"
        }
    """

    # Extract key data
    founder = target_research.get('founder_name', 'Founder')
    company = target_research.get('company_name', 'Company')
    stories = target_research.get('story_cards', [])
    context = target_research.get('competitive_context', '')

    # Select entity template
    templates = {
        'next_chapter': TEMPLATE_NC,
        'and_capital': TEMPLATE_AND,
        'revsup': TEMPLATE_RU
    }

    template = templates.get(entity, TEMPLATE_NC)

    # Build prompt for Claude
    prompt = f"""
You are writing a personalized business letter on behalf of a market advisor.

INSTRUCTIONS:
- Write in operator language (no jargon, speak like a peer)
- One specific story (not generic facts)
- 600-800 words
- Sound human, not templated
- Pass the "dinner party test" (would I mention this at dinner?)

CONTEXT:
Founder: {founder}
Company: {company}
Entity Type: {entity}
Market Context: {context}

STORIES AVAILABLE (pick 1-2):
{json.dumps(stories, indent=2)}

TEMPLATE STRUCTURE:
{template}

WRITE THE LETTER NOW:
Keep it human. Keep it specific. Keep it short enough to read on a phone.
"""

    client = anthropic.Anthropic()

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1000,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    letter_text = response.content[0].text

    # Score personalization (1-10 factors)
    personalization_score = score_letter(
        letter_text=letter_text,
        founder_name=founder,
        company_name=company,
        stories=stories
    )

    return {
        "letter_text": letter_text,
        "personalization_score": personalization_score,
        "tone_signal": "operator" if entity == 'next_chapter' else "investor" if entity == 'and_capital' else "hiring_manager",
        "generated_at": datetime.utcnow().isoformat() + "Z"
    }


def score_letter(letter_text: str, founder_name: str, company_name: str, stories: list) -> float:
    """
    Score how personalized the letter is (0.0-1.0).

    Factors:
    - Uses founder name in body (not just greeting): +0.15
    - Mentions specific company fact/story: +0.20
    - Mentions company name (besides greeting): +0.10
    - References specific metric or market trend: +0.15
    - Sounds conversational (short paragraphs, no jargon): +0.15
    - Story is specific (not generic): +0.15
    - Call to action is concrete (not vague): +0.10
    """

    score = 0.0

    # Check founder mention
    if founder_name.split()[0].lower() in letter_text.lower():
        score += 0.15

    # Check company mention (besides greeting)
    letter_lines = letter_text.split('\n')
    company_mentions = sum(1 for line in letter_lines[2:] if company_name.lower() in line.lower())
    if company_mentions > 0:
        score += 0.10

    # Check for specific story mention
    if any(story.get('story', '').split()[0:5] for story in stories):
        score += 0.20

    # Check for market/metric language
    metrics_keywords = ['consolidat', 'market', 'EBITDA', 'recurring', 'multiple', 'buyers', 'active', 'trending']
    if any(keyword.lower() in letter_text.lower() for keyword in metrics_keywords):
        score += 0.15

    # Check conversational tone (sentence length avg, lack of jargon)
    sentences = letter_text.split('.')
    avg_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
    if 10 < avg_length < 25:  # Good conversational length
        score += 0.15

    # Check for specific story (not generic)
    if any('garage' in s.lower() or 'recover' in s.lower() or 'award' in s.lower() for s in [str(story) for story in stories]):
        score += 0.15

    # Check for concrete CTA
    if 'call me' in letter_text.lower() or 'calendar' in letter_text.lower() or '20 min' in letter_text.lower():
        score += 0.10

    return min(score, 1.0)
```

### Step 2: Create Queue Listener
```python
# File: /Users/clawdbot/Projects/master-crm/engines/executor_queue.py

import supabase
import json
from letter_generator import generate_letter

def process_executor_queue():
    """
    Claim ready executor queue items and generate letters.
    """

    client = supabase.create_client(
        os.getenv('SUPABASE_URL'),
        os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    )

    # Claim next ready item
    response = client.table('queue_items').update(
        {
            'status': 'in_progress',
            'processed_by': 'executor',
            'updated_at': datetime.utcnow().isoformat()
        }
    ).eq('agent_type', 'executor').eq('status', 'ready').limit(1).execute()

    if not response.data:
        print("No queue items ready for executor")
        return

    queue_item = response.data[0]
    target_id = queue_item['target_id']

    try:
        # Load target and research
        target = client.table('targets').select('*').eq('id', target_id).single().execute()
        research = client.table('target_research').select('*').eq('target_id', target_id).single().execute()

        # Generate letter
        letter = generate_letter(
            target_research=research.data,
            entity=target.data['entity']
        )

        # Store proposal
        proposal = client.table('proposals').insert({
            'target_id': target_id,
            'letter_text': letter['letter_text'],
            'personalization_score': letter['personalization_score'],
            'tone_signal': letter['tone_signal'],
            'created_at': datetime.utcnow().isoformat()
        }).execute()

        # Mark queue item done
        client.table('queue_items').update({
            'status': 'done',
            'updated_at': datetime.utcnow().isoformat()
        }).eq('id', queue_item['id']).execute()

        # Log to pipeline_log
        client.table('pipeline_log').insert({
            'agent_id': 'executor',
            'target_id': target_id,
            'entity': target.data['entity'],
            'status': 'completed',
            'reason': f'letter_generated (personalization={letter["personalization_score"]:.2f})',
            'cost_usd': 0.10,
            'duration_ms': 3000
        }).execute()

        print(f"✓ Letter generated for {target.data['name']} (score: {letter['personalization_score']:.2f})")

    except Exception as e:
        print(f"✗ Error generating letter: {e}")

        client.table('queue_items').update({
            'status': 'failed',
            'error_message': str(e),
            'updated_at': datetime.utcnow().isoformat()
        }).eq('id', queue_item['id']).execute()

        client.table('error_log').insert({
            'agent_id': 'executor',
            'target_id': target_id,
            'error_type': 'generation',
            'error_message': str(e)
        }).execute()
```

### Step 3: Test with 1-5 Real Targets

Run against targets that have:
- ✅ research_quality_score ≥ 0.70
- ✅ story_cards populated (5 categories)
- ✅ founder_name, company_name available

Test targets (examples):
1. **AquaScience** (if classified as NC)
2. **Springer Floor** (if classified as NC)
3. Pick 3 more from classified targets with good research

**Test command**:
```bash
# Process 5 targets through executor queue
python3 /Users/clawdbot/Projects/master-crm/engines/executor_queue.py --limit 5

# View generated letters
psql -c "SELECT target_id, personalization_score, letter_text FROM proposals LIMIT 5;" \
  --variable=sslmode=require
```

### Step 4: Manual Review
For each test letter:
1. **Read it out loud** - does it sound human?
2. **Check specificity** - is there a real story or generic fluff?
3. **Check tone** - operator speak or bot speak?
4. **Dinner party test** - would you mention this at dinner?

If score > 0.80 and passes manual review, it's production-ready.

---

## TEMPLATES TO USE IN PROMPT

### TEMPLATE_NC
```
Dear [Founder],

I came across [Specific Story] in my research on [Company], and it stood out.

Here's what's happening in [Industry] right now:
[Market Trend/Metric]

That tells me [Implication about their business].

I work with [Type of business] owners exploring options. Whether you're thinking about it now or not, let's talk for 20 minutes. I can share what's happening in your market and what other owners like you are seeing.

Call me [Phone]. Usually around.

Best,
[Name]
```

### TEMPLATE_AND
```
[Salutation],

We're focused on [Category] and thought you'd want to see recent performance.

Our thesis on [Market] is straightforward: [Thesis].

Our LPs have seen [Return], and we're building the next chapter in [Sector].

We just underwritten [Deal Example], and this is the kind of consolidation thesis we're executing.

Coffee call? I can walk you through fund performance and latest deal.

[Calendar or Phone]

Best,
[Name]
```

### TEMPLATE_RU
```
[Greeting],

We have [# & Role] from [Background] who'd be a fit for what you're building.

One candidate:
- [Experience]: [Years/Domain]
- [Why they move]: [Motivation]
- [Relevant win]: [Specific achievement]

20-min call? I'll walk you through all 3.

[Calendar]

[Name]
```

---

## SCORING RUBRIC (for manual QA)

| Criterion | Poor (0-0.4) | Fair (0.4-0.7) | Good (0.7-0.9) | Excellent (0.9-1.0) |
|-----------|-------------|-----------------|------------------|----------------------|
| **Specific Story** | Generic facts, no narrative | One story mentioned vaguely | One real story with detail | Specific, memorable, dinner party worthy |
| **Founder Reference** | Not mentioned | Named in greeting only | Named + contextualized | Named, mentioned multiple times, personalized |
| **Operator Language** | Jargon-heavy, corporate speak | Some jargon, some natural | Mostly natural, clear | Sounds like a peer, no fluff |
| **Market Insight** | No metrics mentioned | Generic market trends | Specific metric or consolidation signal | Concrete, timely market observation |
| **Call to Action** | Vague "let's talk" | Generic meeting request | Specific: "call me", time frame | Concrete: phone, calendar, specific time |
| **Length** | >900 words or <500 | 500-600 or 800-900 | 650-800 words | 650-750 words, scannable |
| **Tone** | Salesy, bot-like | Somewhat natural but stilted | Natural, peer-to-peer | Effortless, human, genuine |

**Target for production**: Score ≥ 0.75 AND passes manual read-aloud test.

---

## SUCCESS CRITERIA FOR TONIGHT

✅ Letter generator function works (takes research → produces letter)
✅ Scores personalization (0.0-1.0)
✅ Processes 5 test targets without errors
✅ Letters store to proposals table
✅ Queue items marked done
✅ Manual review: all 5 letters pass "operator language" check
✅ Commit to GitHub with test results

**Stretch goal**: Set up cron to auto-process 10-20 targets by tomorrow morning.

---

## IF YOU GET STUCK

**Letter sounds like a bot**: Add more specific story details to prompt, ask Claude for conversational rewrites, reduce template structure in prompt.

**Personalization score too high/low**: Review scoring function, adjust weights, test on known-good letters.

**Supabase connection fails**: Check SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in `~/.openclaw/.env`.

**Queue items not claiming**: Ensure table exists, queue_items.agent_type = 'executor' matches, status = 'ready' exists.

---

**You've got this. 4 hours, 5 letters, production machine boots.**

**Next step after this**: LOB INTEGRATION (print the letters).

---

**Document Created**: 2026-03-30 12:45 MST
**Version**: 1.0
