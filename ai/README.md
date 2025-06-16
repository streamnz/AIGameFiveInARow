# Gomoku DeepSeek AI Implementation

This project implements an intelligent Gomoku (Five in a Row) game using the DeepSeek API.

## Features

- Intelligent decision-making based on DeepSeek Large Language Model
- Support for standard 15x15 Gomoku board
- Smart strategy analysis, including offensive and defensive transitions
- Real-time game response
- Automatic error recovery mechanism

## Configuration Requirements

1. Configure the DeepSeek API key in the `.env` file in the project root directory:

```env
DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

2. Ensure stable network connection to access the DeepSeek API

## AI Strategy

The DeepSeek AI analyzes the current game state:

1. **Defense First**: Identify and block opponent's winning threats
2. **Offensive Opportunities**: Find winning combinations and opportunities
3. **Position Control**: Prioritize occupying key board positions
4. **Smart Fallback**: Use intelligent position selection algorithm when API calls fail

## Usage

The AI automatically handles the following scenarios:
- First move at the start of the game
- Response to each player's move
- Analysis of complex game situations and optimal decision-making
- Handling exceptional cases (such as API timeouts)

## Technical Implementation

- **API Integration**: Using DeepSeek Chat API for game analysis
- **Intelligent Parsing**: Accurate extraction of move coordinates from AI responses
- **Error Handling**: Comprehensive exception handling and fallback mechanisms
- **Position Validation**: Ensuring AI-selected positions are legal and valid

## Notes

- API calls may take some time, please be patient
- Ensure the API key in the `.env` file is correctly configured
- Recommended to use in a stable network environment for the best experience 