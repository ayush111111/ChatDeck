
# TODO List - Implementation Roadmap

## 🚀 Immediate Priorities
- [ ] folder is created, and udner that the deck is added
- [ ] figure out release method (.ankiaddon)
- [ ] Add token limit work
- [ ] Upgrade the quality of output flashcards based on dspy experiments and the app
- [ ] Deploy to cloud
- [ ] Add auth, users
- [ ] card count parameter verify
- [ ] retry mechanisms (openrouter specifically)
- [ ] test cases verify and extend
- [ ] latency
- [ ] ui revamp
- [ ] cleanup unused files
- [ ] create a welcome page

## 🎯 DSPy Integration (Completed - Oct 2025)

### Implementation Summary
DSPy has been integrated for all LLM-based flashcard generation, replacing the previous manual prompt engineering approach.

### Key Changes:
1. **Added DSPy to dependencies** (`pyproject.toml`)
   - `dspy>=2.5.0` - DSPy framework for LLM optimization
   - `datasets>=2.0.0` - For future training examples (optional)

2. **Created `fcg/utils/dspy_flashcard_generator.py`**
   - **TextAnalysis Signature**: Analyzes text to identify key concepts and learning priorities
   - **ConceptPrioritization Signature**: Ranks concepts by learning importance
   - **FlashcardGeneration Signature**: Generates flashcards with question, answer, explanation, and topic
   - **TextToFlashcards Module**: Main pipeline that combines all signatures using ChainOfThought

3. **Updated `fcg/utils/flashcard_generator.py`**
   - Removed manual JSON parsing and prompt engineering
   - Now uses DSPy's TextToFlashcards module
   - Automatic card count calculation (~1 card per 100 words, 3-10 cards)
   - Converts DSPy Pydantic models to dict format for API compatibility

### DSPy Approach vs Previous:
- **Before**: Manual prompt with JSON parsing, error-prone formatting
- **After**: Structured signatures with automatic prompt optimization
- **Benefit**: Better quality, easier to maintain and iterate, reproducible

### From dspy-poc Branch Observations:
- Both class docstrings and desc parameters in output fields guide LLM generation
- Each flashcard now has 4 fields: question, answer, explanation, topic
- Explanation field provides detailed context (4-5 sentences) for better learning
- Chain of Thought reasoning improves output quality
- Text analysis step identifies confusion signals and concept hierarchy
- Adapted from conversation-based to general text-based input

### Next Steps:
- [ ] Test with various content types (technical docs, conversations, articles)
- [ ] Consider implementing GEPA optimizer for prompt evolution
- [ ] Add few-shot examples using LabeledFewShot teleprompter
- [ ] Track prompt evolution over time to measure improvements

### Notes from dspy and dspy-poc Branches:

#### dspy-poc Branch Findings:
The dspy-poc branch (`fcg/development/dspy_anki.ipynb`) contains a fully working notebook with:

**Architecture:**
- **ConversationAnalysis**: Identifies user confusion signals, concept hierarchy, and follow-up intensity
- **ConceptPrioritization**: Ranks concepts based on confusion signals and follow-ups
- **FlashcardGeneration**: Creates cards with front, back, and explanation fields
- **Quality Control Signatures** (commented out in production):
  - DistinctnessChecker: Removes overlapping content
  - RepetitionRemover: Eliminates repeated phrasing between front/back
  - NeutralityEnforcer: Removes references to 'user', 'AI', 'conversation'
  - CardComplexityOptimizer: Adjusts based on user comprehension level

**Key Observations from Notebook:**
- ✅ Generated 8 high-quality flashcards from GEPA algorithm conversation
- ✅ Each card has focused question, direct answer, detailed explanation
- ⚠️ Quality control checks were disabled - too many LLM calls caused delays
- ⚠️ Received junk output when all verification calls ran (generated irrelevant content)
- 💡 Both class docstrings AND desc parameters are incorporated into LLM prompts

**Example Output Quality:**
```
Front: "What is the core similarity between traditional GAs and GEPA?"
Back: "Both share the same evolutionary principle."
Explanation: "Both traditional GAs and GEPA are based on the same core principles
of evolutionary algorithms: candidate representation, fitness evaluation, selection,
mutation & crossover, and generation iteration..."
```

#### dspy Branch Findings:
The dspy branch contains `fcg/development/dspy_poc.py` demonstrating:

**DSPy Concepts Applied:**
1. **Signatures**: Input/output specifications that tell LM *what* to do, not *how*
2. **Modules**: Building blocks that abstract prompting techniques (e.g., ChainOfThought)
3. **Optimizers**: Auto-improve prompts using examples (LabeledFewShot, GEPA)

**Code Example from dspy_poc.py:**
```python
# Basic signature
class BasicQASignature(dspy.Signature):
    __doc__ = """Answer questions with short factoid answers."""
    question = dspy.InputField()
    answer = dspy.OutputField(desc="often between 1 and 5 words")

# Few-shot optimization
from dspy.teleprompt import LabeledFewShot
fewshot_teleprompter = LabeledFewShot(k=3)
basic_fewshot_qa_model = fewshot_teleprompter.compile(basic_qa_model, trainset=squad_train)
```

**Why DSPy?**
- Outperforms 20-hour expert prompt engineering by 40% (UMD research)
- Reproducibility: Track how prompts evolve over time
- Automatic optimization with annotated examples
- Modules serve as learning targets for the optimizer

**File Structure:**
- `fcg/development/dspy_anki.ipynb` - Main working notebook (dspy-poc branch)
- `fcg/development/dspy_poc.py` - Basic DSPy examples and concepts
- `fcg/development/conversation.pkl` - Sample conversation data (7KB)
- `fcg/development/format.html` - Anki card template with explanation toggle

#### Implementation Differences:
**dspy-poc (Conversation-focused):**
- Analyzed user confusion signals and follow-up questions
- Prioritized concepts based on learning engagement
- 3-stage pipeline: analyze → prioritize → generate

**Current Implementation (Text-focused):**
- Generalized for any text input (not just conversations)
- Same 3-stage pipeline adapted for general content
- Automatic card count: ~1 card per 100 words (3-10 range)
- 4 fields per card: question, answer, explanation, topic

#### Best Practices from Experimentation:
1. Keep class docstrings detailed - they guide LLM generation
2. Use `desc` parameter in OutputFields for specific formatting
3. ChainOfThought improves reasoning quality
4. Quality control steps should be optional (performance trade-off)
5. Pydantic models ensure type safety and structure

## 📦 Distribution
- [ ] Upload Anki package to add-on store
- [ ] Upload Chrome extension to Chrome store

---

# Archive - Original TODO

add dspy
- make llm based code modular


- improve UI
    - theme - https://github.com/pranavdeshai/anki-prettify
    - adds/removes blur to reveal answer- https://geoffruddock.com/mental-models-with-anki/
    - https://github.com/ikkz/anki-eco

- adding file upload

- add a cap to the conversation / find a way to deal with large conversations


add pdf support - I am the user for it - I frequently need to summarise books into anki cards
- varying number of cards
- density of information
- type of card - quiz / fill in the blank / thorough (dense)
- wasnt the "core" purpose summarising chats though - i use it more for books than chats

- to summarise files, the app will need a frontend or a sidebar to upload files

Priority


Have a range of topics that the use can select from - that can be converted into flashcards

- book to flashcard - algorithm and logic - will need time and iterations
- api to flashcard - what should the users upload?
    - optional parameter : is there a particular api that will be useful to you / is there a specific section you want to focus on (enhance the question)
- for maths - he restates the same idea in multiple ways, aims for the minimal answer that displays the core idea as sharply as possoble


- - v1 - the design pattern book (410 pages - try set of algorithms, images, core "22" patterns + solid + oop = ~30 "concepts" - 2-3 flashcards per pattern and 1 for for the rest = ~70 cards)
    - density of information
    - "golden" card set from anki

there are better interfaces out there - so just focus on getting the algorithm right for you

---------------------------

https://augmentingcognition.com/ltm.html
> Research Paper -> anki deck

> Image -> anki deck: I have an Anki question which simply says: “Visualize the graph Jones 2011 made of the probability curves for physicists making their prizewinning discoveries by age 30 and 40”. The answer is the image shown above, and I count myself as successful if my mental image is roughly along those lines.

> making Anki cards is an act of understanding in itself - shared decks and deck creation apps are fill-ins until you make your own deck
> Avoid the yes/no pattern
> Using Anki for APIs, books, videos, seminars, conversations, the web, events, and places: Nearly everything I said earlier about Ankifying papers applies also to other resources. Here's a few tips. I've separated out the discussion for APIs into an appendix, which you can read below, if interested.

> For seminars and conversations with colleagues I find it surprisingly helpful to set Anki quotas. For instance, for seminars I try to find at least three high-quality questions to Ankify. For extended conversations, at least one high-quality question to Ankify. I've found that setting quotas helps me pay more attention, especially during seminars. (I find it much easier a priori to pay attention in one-on-one conversation.)

> I'm more haphazard about videos, events, and places. It'd be good to, say, systematically Ankify 3-5 questions after going on an outing or to a new restaurant, to help me remember the experience. I do this sometimes. But I haven't been that systematic.

> I tend to Ankify in real time as I read papers and books. For seminars, conversations, and so on I prefer to immerse myself in the experience. Instead of getting out Anki, I will quickly make a mental (or paper) note of what I want to Ankify. I then enter it into Anki later. This requires some discipline; it's one reason I prefer to set a small quota, so that I merely have to enter a few questions later, rather than dozens.

> What determines the steepness of the curve, i.e., how quickly memories decay? In fact, the steepness depends on many things. For instance, it may be steeper for more complex or less familiar concepts. You may find it easier to remember a name that sounds similar to names you've heard before: say, Richard Hamilton, rather than Suzuki Harunobu. So they'd have a shallower curve. Similarly, you may find it easier to remember something visual than verbal. Or something verbal rather than a motor skill. And if you use more elaborate ways of remembering – mnemonics, for instance, or just taking care to connect an idea to other things you already know – you may be able to flatten the curve out** Although this expansion is much studied, there is surprisingly little work building detailed predictive models of the expansion. An exception is: Burr Settles and Brendan Meeder, A Trainable Spaced Repetition Model for Language Learning (2016). This paper builds a regression model to predict the decay rate of student memory on Duolingo, the online language learning platform. The result was not only better prediction of decay rates, but also improved Duolingo student engagement..

https://jesungpark.com/blog/spaced-repetition.html
History of spaced repetition algorithms

https://l-m-sherlock.notion.site/The-History-of-FSRS-for-Anki-1e6c250163a180a4bfd7fb1fee2a3043
recent developments

https://cognitivemedium.com/srs-mathematics
    Breaking down complex proofs into atomic elements

    Extract single elements from proofs and convert them to individual cards
    Focus on making both questions and answers express a single idea
    Restating ideas in multiple ways

    Simplifying questions and answers

    Trimming unnecessary complexity
    Aiming for "the minimal answer, displaying the core idea as sharply as possible"
    Creating different interpretations

    Geometric interpretations of mathematical constructs
    Questions like "What's a geometric interpretation of..."
    Exploring variations and implications

    Extending concepts through "what if" questions
    Examining what conditions mean for different components
    Creating "distillation" cards

    Cards that attempt to capture an entire proof in one sentence
    Visual representations of the complete proof
    Using these as "boundary conditions or forcing functions"
    Structuring meta-questions about proofs

    "How many key ideas are there in the proof..."
    "What are the two key ideas in the proof..."
    Using visual representations

    Matrix equations to visually represent key ideas
    Desire to highlight crucial elements in visualizations
    Forcing verbal explanations

    "In one sentence, what is the core reason..."
    Converting non-verbal understanding to verbal explanations
    Refactoring cards over time

    Rewriting cards as understanding improves
    Discarding or replacing cards that no longer serve their purpose
    Connecting ideas across cards

    Building a network of interconnected concepts
    Finding multiple explanations for the same concept
    Testing understanding from multiple angles

    Cards that approach the same concept from different directions
    Questions that make you apply the concept in different contexts

Using Anki to Learn APIs - Key Methods
`    The author outlines a specific approach to using Anki for learning programming APIs effectively:

    Effective Learning Process
    Start with working code, not documentation

    Begin by finding small, functioning code samples (tens to hundreds of lines)
    Make small incremental changes (1-5 lines) to build understanding
    Use "gradient descent in the space of meaningful projects"
    Progressive Ankification strategy

    Don't Ankify everything immediately
    Only add cards for central concepts you'll reuse often
    Add to Anki gradually as you work on real projects
    Two-pass tutorial approach

    First pass: Be conservative, Ankify only what you immediately need
    Second pass: After gaining context, Ankify everything likely needed later
    Second pass is often faster than the first
    Project-driven learning

    Bounce between project work and Anki while studying materials
    Let actual usage guide what to memorize
    Even Ankify APIs for code you've personally written
    Things to Avoid
    Speculative Ankification

    "Oh, I might want to learn such-and-such an API one day..."
    Don't add cards for APIs you're not currently using
    Tutorial-first approach

    Don't try to master an API through documentation before using it
    This approach is "seductive" but ineffective
    Orphaned API cards

    Cards for APIs you no longer use lose engagement value
    Consider deleting cards for APIs you won't use again
    The author emphasizes that using an API in a real project sends a "t
`

--------------
Datasets and sources of Anki decks you can use

FSRS-Anki-20k — a 20k sample collection of Anki collections useful for SRS and card metadata. Good for building user behaviour features.
Hugging Face

anki-revlogs-10k — dataset with cards, revlogs and decks. Useful for extracting Q/A pairs and context.

-------------
https://www.lesswrong.com/posts/hGhBhLsgNWLCJ3g9b/creating-flashcards-with-llms

> Note that people tend to overestimate their skills at creating good cards. Especially when creating cards en masse by hand, there is a strong tendency to start simplifying by focusing on the information that is easy to put in flashcards, vs. the information you actually care about, but which is hard to encode into a card. So you should probably lower your expectation of how good your cards actually are (unless you have considerable experience to back up your estimate).

> Create [number of cards] concise, simple, straightforward and distinct Anki cards to study the following article, each with a front and back. Avoid repeating the content in the front on the back of the card. In particular, if the front is a question and the back an answer, avoid repeating the phrasing of the question as the initial part of the answer. Avoid explicitly referring to the author or the article in the cards, and instead treat the article as factual and independent of the author. Use the following format:

    1. Front: [front section of card 1]
    Back: [back section of card 1]

    2. Front: [front section of card 2]
    Back: [back section of card 2]

    ... and so on.

    Here is the article:

    "[Article]"

In my experience with the Rationality deck (see below), if the word count of the article is
N, you can aim for ∼N/100 cards. In general, you should avoid (if you can) breaking the article into smaller parts, each processed independently, as the LLM will lose important context to generate the cards. The template prompt contains pieces of information that are relevant for the LLM to know:

"concise, simple, straightforward": otherwise, GPT-3.5/4 has some tendency to add a lot of text to the back of the card, which goes against some flashcard design principles.
"distinct": mainly to avoid it creating cards covering the same information.
"Avoid repeating the content in the front on the back of the card. In particular, if the front is a question and the back an answer, avoid repeating the phrasing of the question as the initial part of the answer.": very common issue otherwise, GPT-3.5/4 defaults to adding unnecessary information to the back of the card.
"Avoid explicitly referring to the author or the article in the cards, and instead treat the article as factual and independent of the author.": by default, it tends to not treat the information in the article at face value. It would regularly add "According to the article/author" to the front or back of the cards, which is unnecessary.
"each with a front and back" and "Use the following format": By keeping the format consistent among cards, it is easy to post-process them with a script to add to Anki. GPT-4 always follows the template, while GPT-3.5 only does sometimes. It is possible that adding an example card to the end of the prompt would help, but I haven't checked.


... feel free to use LaTeX to write them .. - resulting cards may require additional post-processing
