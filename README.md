# Unstructured Data Conversion

## Introduction

This is a small app that uses the EvaDB ChatGPT utility to convert unstructured data to a provided stuctured format. For the timebeing we focus on user hardware and software complaints. The `data/user_complaints.csv` file contains some example queries.

We run them through ChatGPT via a crafted prompt which classifies the Issue category and Issue Component along with displaying the raw issue string. The default format is the following

```
DEFAULT_STRUCTURE_FORMAT = [
    [
        "Issue Category",
        "What category the issue belongs to",
        "One of (hardware, software)",
    ],
    [
        "Raw Issue String",
        "Raw String containing the exact input given by the user",
        "string",
    ],
    ["Issue Component", "Component that is causing the issue", "string"],
]
```

## Results
```
Query : The keyboard on my laptop is typing the wrong letters and it's driving me crazy!
✅ Answer:
{
  "Issue Category": "hardware",
  "Raw Issue String": "The keyboard on my laptop is typing the wrong letters and it's driving me crazy!",
  "Issue Component": "keyboard"
}
```

## Setup and running the application
