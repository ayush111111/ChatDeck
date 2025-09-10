# WHy ?
# 	Outperforms 20-hour expert human prompt engineering by 40% [UMD -https://dspy.ai/community/use-cases/]
# https://dspy.ai/production/ - Reproducibility
# Signatures: Signatures specify the input and output types to the LM and what the expected behaviour is. They let you tell the LM what it needs to do, rather than specify how it should do it.

# Modules: Modules are building blocks for programs that interact with LMs. They are generalized to take in any signature while abstracting away the prompting technique for interacting with the LM (e.g., chain of thought).
# modules serve as learning targets for the optimizer. As LMs and prompting strategies evolve, so too does the module.

# Optimizers: Optimizers improve the performance of a DSPy module with annotated examples of input-output pairs. The optimizer can automatically improve and generate prompts, few-shot examples or the language model weights to produce a new, improved module that can perform better on that task.
import os

import dspy
from dotenv import load_dotenv

load_dotenv()
# TODO: build a timeline of how prompts evolve over time to demonstrate the value of DSPy
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
lm = dspy.LM(
    model="openrouter/google/gemini-2.0-flash-001",
    api_base="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)
dspy.configure(lm=lm)

# resp = lm("What is the birthplace of the first author to win a Hugo Award for a translation?")

# _ = lm.inspect_history(n=1)
# print(resp)


class BasicQASignature(dspy.Signature):
    __doc__ = """Answer questions with short factoid answers."""

    question = dspy.InputField()
    answer = dspy.OutputField(desc="often between 1 and 5 words")


sig_predictor = dspy.Predict(BasicQASignature)


# sig_predictor(question="country with the highest gdp?")
# _ = lm.inspect_history(n=1)
# [2025-09-10T11:11:01.510972]

# System message:

# Your input fields are:
# 1. `question` (str):
# Your output fields are:
# 1. `answer` (str): often between 1 and 5 words
# All interactions will be structured in the following way, with the appropriate values filled in.

# [[ ## question ## ]]
# {question}

# [[ ## answer ## ]]
# {answer}

# [[ ## completed ## ]]
# In adhering to this structure, your objective is:
#         Answer questions with short factoid answers.


# User message:

# [[ ## question ## ]]
# country with the highest gdp?

# Respond with the corresponding output fields, starting with the field `[[ ## answer ## ]]`, and then ending with the marker for `[[ ## completed ## ]]`.


# Response:

# [[ ## answer ## ]]
# United States
# [[ ## completed ## ]]


# -------------------

# setup
import os

import dspy
from datasets import load_dataset
from dotenv import load_dotenv


def get_squad_split(squad, split="validation"):
    """
    Use `split='train'` for the train split.

    Returns
    -------
    list of dspy.Example with attributes question, answer

    """
    data = zip(*[squad[split][field] for field in squad[split].features])
    exs = [dspy.Example(question=q, answer=a["text"][0]).with_inputs("question") for eid, title, context, q, a in data]
    return exs


class BasicQA(dspy.Module):
    def __init__(self):
        super().__init__()
        self.generate_answer = dspy.Predict(BasicQASignature)

    def forward(self, question):
        return self.generate_answer(question=question)


basic_qa_model = BasicQA()

squad = load_dataset("squad", trust_remote_code=True)
squad_train = get_squad_split(squad, split="train")
squad_dev = get_squad_split(squad)

# -------------
# zero shot -> few shot
from dspy.teleprompt import LabeledFewShot

fewshot_teleprompter = LabeledFewShot(k=3)
basic_fewshot_qa_model = fewshot_teleprompter.compile(basic_qa_model, trainset=squad_train)

basic_fewshot_qa_model(question="What is the birthplace of the first author to win a Hugo Award for a translation?")
_ = lm.inspect_history(n=1)


# [2025-09-10T11:33:53.308058]

# System message:

# Your input fields are:
# 1. `question` (str):
# Your output fields are:
# 1. `answer` (str): often between 1 and 5 words
# All interactions will be structured in the following way, with the appropriate values filled in.

# [[ ## question ## ]]
# {question}

# [[ ## answer ## ]]
# {answer}

# [[ ## completed ## ]]
# In adhering to this structure, your objective is:
#         Answer questions with short factoid answers.


# User message:

# [[ ## question ## ]]
# What group did Paul VI address in New York in 1965?


# Assistant message:

# [[ ## answer ## ]]
# United Nations

# [[ ## completed ## ]]


# User message:

# [[ ## question ## ]]
# What did Sander's study show in terms of black law students rankings?


# Assistant message:

# [[ ## answer ## ]]
# half of all black law students rank near the bottom of their class after the first year of law school

# [[ ## completed ## ]]


# User message:

# [[ ## question ## ]]
# What problems does linguistic anthropology bring linguistic methods to bear on?


# Assistant message:

# [[ ## answer ## ]]
# anthropological

# [[ ## completed ## ]]


# User message:

# [[ ## question ## ]]
# What is the birthplace of the first author to win a Hugo Award for a translation?

# Respond with the corresponding output fields, starting with the field `[[ ## answer ## ]]`, and then ending with the marker for `[[ ## completed ## ]]`.


# Response:

# [[ ## answer ## ]]
# France

# [[ ## completed ## ]]
