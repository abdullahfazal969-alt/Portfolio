---
title: "DESIGN PATTERNS"
short_description: "This project is a hands-on demonstration of core software design patterns, implemented in Python to build a simple, modular, and scalable multi-agent system. The focus is not on creating a production-level AI, but on showcasing a deep understanding of software architecture"
image: "images/projects/project.jpg"
tags: "Architecturing Multi-Agent System"
---

## Project Overview

This project is a hands-on demonstration of core software design patterns, implemented in Python to build a simple, modular, and scalable multi-agent system. The focus is not on creating a production-level AI, but on showcasing a deep understanding of software architecture

## System Architecture & Design
This system is designed as a decoupled, event-driven architecture. Instead of agents calling each other directly, they communicate through a central EventManager. This approach allows for a flexible and extensible system where new agents and capabilities can be added with minimal changes to existing components.

The core workflow simulates an automated research and reporting pipeline:

- A task is initiated in main.py.
- An AgentFactory creates the necessary agents.
- A ResearchAgent gathers information using a selected Strategy.
- Upon completion, it notifies the EventManager (Singleton) of a research_completed event.
- An AnalysisAgent, acting as an Observer, receives this notification and begins its task.
- The process continues until the final output is generated.

## Core Components
The system is built from several key components that work together.

* Agents
Agents are the primary "workers" of the system. They are defined by the BaseAgent abstract class.

## ResearchAgent (agents/research_agent.py):
- Role: To gather information based on a given topic.
Composition: This agent is composed of a ResearchStrategy object, which dictates how it performs research. This demonstrates the Strategy Pattern, allowing its behavior to be changed dynamically. It also uses mock "Tools" (e.g., MockWebSearchTool) to simulate its work.

## AnalysisAgent (agents/analysis_agent.py):
- Role: To process the findings from the ResearchAgent and generate a summary.
Composition: This agent acts as an Observer. During its initialization, it subscribes to the EventManager to listen for "research_completed" events. When it receives a notification, it triggers its own analysis task.

## Design Patterns in Action
The architecture is held together by four key design patterns:
* Singleton (patterns/event_manager.py):
The EventManager class is implemented as a Singleton to ensure there is only one central "message bus" for the entire application. All inter-agent communication is funneled through this single instance, preventing state conflicts and providing a global point of contact.

* Factory (patterns/agent_factory.py):
The AgentFactory is used to create agents without the main application needing to know the specific agent classes. It uses a self-registering decorator, allowing new agent types (like RAGAgent in our discussion) to be added to the system just by defining their class. This makes the system highly extensible.

* Observer (patterns/event_manager.py & Agents):
The EventManager acts as the Subject, and agents act as Observers. Agents can subscribe to specific event types (e.g., "task_completed"). This decouples the agents from each other; the ResearchAgent doesn't know the AnalysisAgent exists, it only knows to notify the EventManager.

* Strategy (strategies/):
The ResearchAgent's behavior is made flexible by being composed with a ResearchStrategy object. We have implemented several concrete strategies (StandardResearch, DeepDiveResearch), and the agent can either be assigned one or select one dynamically. This allows its core algorithm to be swapped out easily.

[Link to GitHub Repository](https://github.com/abdullahfazal969-alt/Design_Patterns/)
