from ..tools.utils import WorkflowState, OPENAI_LLM, ANTHROPIC_LLM, make_system_prompt


def topic_choice_node(state: WorkflowState):
    print("----- USER FEEDBACK REQUIRED -----")
    print("The viral checker agent has provided a topic choice.\n Validate to agree and continue or enter your preferred topic choice.")
    user_choice = input("Your choice: ")

    if user_choice == "1":
        topic = state.get('viral_checker_schema').topic_choice
        ans = f"The user agrees with the viral checker agent's choice: {topic}."
    else:
        topic = user_choice
        ans = f"The user prefers the topic: {user_choice}."

    return {
        "topic_feedback": ans,
        "chosen_topic": topic,
    }

def publication_node(state: WorkflowState):
    pass
    
        