from ..tools.utils import WorkflowState, OPENAI_LLM, ANTHROPIC_LLM, make_system_prompt
from langgraph.types import Command
import time
import logging


def trend_feedback_node(state: WorkflowState):
    logging.info("\n\n---------- Activating the Trend_Feedback_Node ----------\n\n")
    time.sleep(10)

    logging.info("----- USER FEEDBACK REQUIRED -----")
    # print(  "The viral checker agent has provided a topic choice.\n" \
    #         # "-> (1) Enter '1' to agree and continue...\n" \
    #         "-> (2) Enter your preferred topic choice...\n" \
    #         "-> (0) Enter '0' if you want to scrape more trends...")
    user_choice = input("The viral checker agent has provided a topic choice.\n" \
            "-> (1) Enter '1' to agree and continue...\n" \
            "-> (2) Enter your preferred topic choice...\n" \
            "-> (0) Enter '0' if you want to scrape more trends...")

    goto = "writer"
    if user_choice == "1":
        trend_choice = state.get('analysis_schema').trend_choice
        ans = f"The user agrees with the trends analyst choice: {trend_choice}.\nThe writer agent will have to draft a tweet about that topic."
        logging.info(f"\n\nThe user agrees with the viral checker agent's choice: {trend_choice}.\n\n")
    elif user_choice == "2":
        trend_choice = user_choice
        ans = f"The user prefers the topic: {trend_choice}."
        logging.info(f"The user chose another trend")

    else:
        trend_choice = None
        ans = "The user wants to scrape more trends."
        goto = "scraper"
        logging.info(f"The user wants another scraping")


    return Command(
        update={
            "trend_choice_feedback": ans,
            "chosen_trend": trend_choice,
        },
        goto=goto,
    )


def tweet_validation_node(state: WorkflowState):
    logging.info("---------- Activating Tweet_Validation_Node ----------")
    time.sleep(10)

    logging.info("----- USER FEEDBACK REQUIRED -----")
    # print(  "The writer agent has drafted this tweet. Are you satisfied?\n" \
    #         "-> (1) Enter '1' to agree and continue...\n" \
    #         "-> (0) If you want the agent to rewrite, please provide a feedback...")
    user_choice = input("The writer agent has drafted this tweet. Are you satisfied?\n" \
            "-> (1) Enter '1' to agree and continue...\n" \
            "-> (0) If you want the agent to rewrite, please provide a feedback...")

    goto = "publication_node"
    if user_choice == "1":
        tweet = state.get('writer_schema').tweet
        ans = f"The user agrees with the writer agent's tweet:\n{tweet}."
        logging.info(f"\n\nThe user agrees with the tweet!!!.\n\n")

    else:
        tweet = None
        ans =   "The user wants the agent to rewrite the tweet. Here is his feedback:\n" \
                f"{user_choice}"
        goto = "writer"

    return Command(
        update={
            "tweet_validation_feedback": ans,
            "final_tweet": tweet,
        },
        goto=goto,
    )
        