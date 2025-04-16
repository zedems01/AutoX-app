#  AutoX 🚀

<!-- ![App Screenshot](beautirag-app/public/app_screenshot.png) -->


Developing a team of AI agents using **LangGraph** to autonomously manage an **X (formerly Twitter)** account. The system is designed to handle the full content pipeline, including:

- Identifying trending topics on X in real time  
- Performing web searches and retrieving relevant tweets for contextual understanding  
- Generating, analyzing, and publishing content  
- Managing user interactions such as replies, comments, retweets, and likes  
- Collecting and analyzing engagement metrics for performance monitoring  

The workflow incorporates an optional **Human-in-the-Loop (HITL)** system, allowing for human oversight and refinement at key decision points.


## 🏗️ Architecture

<p style="text-align: center;">
  <img src="./x_automation_app/agents_workflow.png" alt="workflow images" width="500" />
</p>


### 🤖 Agents
- 🕸️ **Web Scraping Agent**: Extracts trending topics on X based on a specified location (city, country, or worldwide).
- 🌐 **Web Search Agent**: Performs real-time web searches to gather contextual news and information related to the trending topics identified.
- 📈 **Trends Analyst Agent**: Evaluates the trending topics and recommends the one most likely to generate high engagement if tweeted.
- ✍️ **Writer Agent**: Crafts the final tweet using insights from the Trends Analyst Agent and a curated set of user tweets related to the topic.
- ....

### Other nodes
- **Human Feedback**
- **Tweets Publication**
- **Interactions**


### 📁 Project Structure


