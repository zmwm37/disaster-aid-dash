## Project - Deliverable \# 2 Feedback 

This looks good to me. To answer your question, a few notes: 

1. If the API is down then that will make it hard for me to grade. I doubt that will be the case but that's always the downside of using API servers. I wouldn't worry too much about this.  

2. My main advice is for you to define a separate module for each API connection that handles gathering, cleaning and wrangling the data and have them all implement a specific abstract class such that the API managing class can easily create these API connection classes and being able to call the same method for each of the API connection classes. I think this will make it much easier for you to gather all the data efficiently to pass it on to the analysis/vis module. 

*Grade*: 10/10 
