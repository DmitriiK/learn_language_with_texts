Need to track usage of some metrics
For LLM invocations it should be
- length of text been send in users prompt ( it should be written before llm invocations)
-   'input_tokens'
-  'output_tokens'
(after invocations)
Results should be written cumulatively to json file, path from config.
It should be done both for user (if user name is provided) and in overall.

in users.json file need to add new attribute for user, - usage_threshold.
Before invocation of LLM add check total_text_length for the text it is going to process, sum up with value from audit file for this user and if it exceeds threshold - throw exception


