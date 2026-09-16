# Rule: Always Test Code Before Informing User

When implementing new features, especially backend views or API endpoints, you MUST thoroughly test the implementation before declaring it complete to the user.

## Requirements:
1. After writing code that handles HTTP requests or database queries, use the `run_command` tool to execute a Python script or curl command that sends a real request to the endpoint.
2. If the endpoint requires authentication, verify that the page renders correctly (a 200 or 302 status code without uncaught exceptions or FieldErrors).
3. Do not assume model fields exist (e.g., `created_at`); explicitly check the models if you are unsure, or rely on actual runtime testing to catch `FieldError` exceptions.
4. Only notify the user that the task is "100% complete" after verifying the runtime behavior is free of syntax and runtime errors.
