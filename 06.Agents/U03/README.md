# Weather AI Assistant (MCP + LLM)

This project demonstrates how to build an **AI-powered weather assistant** using the **Model Context Protocol (MCP)** and **Large Language Models (LLMs)**.

The system allows users to ask questions about weather conditions using natural language. The AI agent determines which tool should be used, retrieves data from an external weather API, and returns the results.

---

# Project Goals

The goal of this project is to demonstrate how **AI agents interact with external APIs through MCP tools**.

The project shows how to:

- Build an MCP server
- Integrate external APIs
- Create MCP tools
- Build a CLI client
- Use Claude Desktop as an MCP client
- Run local LLM agents using Ollama

---

# System Architecture

User
↓
Client Application
↓
LLM (Reasoning Layer)
↓
MCP Client Session
↓
MCP Weather Server
↓
Weather Tools
↓
OpenWeatherMap API

The **LLM decides what action to take**, while the **MCP server executes the tools**.

---

# Features

## Current Weather Tool

Returns the **current weather conditions** for a city.

Example:

Current Weather in Riyadh, SA  
Temperature: 21°C  
Humidity: 55%  
Wind: 4 m/s  
Outlook: Overcast clouds

---

## Weather Forecast Tool

Returns **forecast data for upcoming time periods**.

Example:

City: Riyadh, SA

2026-03-13 09:00  
Temperature: 27°C  
Wind: 3 m/s  
Outlook: Clear sky

---

# External API Integration

The MCP server retrieves weather data from the **OpenWeatherMap API**.

Endpoints used:

/weather  
/forecast

The API returns responses in **JSON format**, which are processed and converted into **human-readable text**.

---

# MCP Server Components

## Resources

Resources store configuration data used by MCP tools.

Example resource:

weather_config_resource

This resource stores:

- API base URL
- API key

---

## Tools

Two MCP tools are implemented:

**get_current_weather** → returns current weather

**get_forecast** → returns forecast data

---

## Prompts

The MCP server also provides prompts used by LLM clients to **classify tool calls**.

Example prompt:

weather_classifier

Example transformation:

User input:

What's the weather in Cairo today?

Model output:

{
 "tool": "get_current_weather",
 "args": {"city": "Cairo"}
}

---

# Client Implementations

## CLI Client (Without LLM)

A simple command-line client allows the user to:

- enter a city
- choose between current weather or forecast

The client directly calls MCP tools.

<div align="center">
    <img src="https://imgur.com/A1PQswv.jpg" alt="User Dashboard" />
</div>

---

## Claude Desktop Integration

The MCP server can be registered inside **Claude Desktop configuration**.

Claude can then automatically:

- discover available tools
- call tools
- integrate results

This allows Claude to function as an **AI weather agent**.
<div align="center">
    <img src="https://imgur.com/A1PQswv.jpg" alt="User Dashboard" />
</div>
<div align="center">
    <img src="https://imgur.com/A1PQswv.jpg" alt="User Dashboard" />
</div>
<div align="center">
    <img src="https://imgur.com/A1PQswv.jpg" alt="User Dashboard" />
</div>

---

## Ollama Local AI Agent

The project also demonstrates running an AI agent locally using **Ollama**.

Workflow:

1. User sends request  
2. LLM classifies the request  
3. Tool is selected  
4. MCP server executes the tool  
5. Result returned to the user  

This allows building **local AI agents without cloud APIs**.
<div align="center">
    <img src="https://imgur.com/A1PQswv.jpg" alt="User Dashboard" />
  </div>

---

# Project Structure

Weather-AI-Agent

weather_server.py  
weather_server_ollama.py  
weather_client.py  

pyproject.toml  
README.md

---

# Running the Project

Run the client:

python weather_client.py

Example:

Enter city: Riyadh  
1. Current weather  
2. Forecast

---
